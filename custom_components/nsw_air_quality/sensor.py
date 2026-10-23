"""Sensor platform for NSW Air Quality Data"""

import logging

from homeassistant import exceptions
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfDensity, UnitOfRatio
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .air_qual_controller import AirQualityController
from .const import (
    AIR_QUALITY_CATEGORIES,
    CONCENTRATION_PARTS_PER_HUNDRED_MILLION,
    CONF_CONTROLLER,
    CONF_SITE_ID,
    DOMAIN,
    HOURLY_AVERAGE_FREQUENCY,
    MODEL_NAME,
    SHORT_ATTRIBUTION,
    SITE_AQC_PARAMETER_CODE,
)
from .sensor_type import SensorType

_LOGGER = logging.getLogger(__name__)


def _select_value(current_value, sensor_data):
    """Return the most recent valid hourly reading, or keep current_value if there is none.

    Only "Hourly average" rows are considered; some pollutants also have rolling-average rows (e.g. ozone
    4h/8h) for the same hour. Readings that are None or negative are ignored. Readings arrive an hour or two
    late, so the latest valid hour is used rather than a fixed hour.
    """
    readings = [
        entry
        for entry in sensor_data or []
        if (entry.get("Parameter") or {}).get("Frequency") == HOURLY_AVERAGE_FREQUENCY
        and entry.get("Value") is not None
        and entry["Value"] >= 0
    ]
    if not readings:
        _LOGGER.debug("No valid hourly reading, keeping previous value %s", current_value)
        return current_value

    return max(readings, key=lambda entry: (entry.get("Date"), entry.get("Hour")))["Value"]


def _normalise_category(raw_category):
    """Map an API category such as "VERY POOR" onto a sensor option, or None if it isn't a known rating."""
    if not raw_category:
        return None

    category = raw_category.strip().lower().replace(" ", "_").replace("-", "_")
    return category if category in AIR_QUALITY_CATEGORIES else None


def _select_category(current_category, site_entries):
    """Return the site's overall air quality category, or keep current_category if no rating is available.

    Uses the most recent hour with any rating. The official site-level AQC row is preferred; it is only
    present in some API responses, so otherwise fall back to the worst pollutant category for that hour.
    """
    rated = []
    for entry in site_entries or []:
        category = _normalise_category(entry.get("AirQualityCategory"))
        if category is not None:
            rated.append(((entry.get("Date"), entry.get("Hour")), entry, category))

    if not rated:
        return current_category

    latest_hour = max(hour for hour, _, _ in rated)
    latest = [(entry, category) for hour, entry, category in rated if hour == latest_hour]

    for entry, category in latest:
        if (entry.get("Parameter") or {}).get("ParameterCode") == SITE_AQC_PARAMETER_CODE:
            return category

    return max((category for _, category in latest), key=AIR_QUALITY_CATEGORIES.index)


def _device_info(site_id, site_name):
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, f"{site_id}")},
        manufacturer=SHORT_ATTRIBUTION,
        model=MODEL_NAME,
        name=f"{site_name}",
    )


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(CONF_CONTROLLER, AirQualityController())

    controller = hass.data[DOMAIN][CONF_CONTROLLER]
    site_id = entry.data[CONF_SITE_ID]
    site_name = entry.title

    controller.add_site(site_id)

    sensors = [AirQualityCategorySensor(site_id, site_name, controller)]

    for sensor in SensorType:
        # Convert Enum name to uppercase for matching config keys
        config_key = sensor.name.upper()

        create_sensor = entry.options.get(config_key, entry.data.get(config_key))

        if create_sensor is True:
            sensors.append(AirQualitySensor(site_id, site_name, controller, sensor))

    async_add_entities(sensors, True)


class AirQualitySensor(SensorEntity):
    def __init__(
        self,
        site_id: str,
        site_name: str,
        controller: AirQualityController,
        sensor_type: SensorType,
        initial_value: float | None = None,
    ):
        """Initialize the sensor."""
        _LOGGER.info("Initializing site '%s' (site-id:%s) sensor type: '%s'", site_name, site_id, sensor_type)

        self._attr_has_entity_name = True
        self._attr_name = f"{sensor_type.name}"
        self._attr_unique_id = f"{site_id}_{sensor_type.name.lower()}"
        self._attr_state_class = "measurement"
        self._attr_native_value = initial_value
        self.controller = controller

        self._site_id = site_id
        self._sensor_type = sensor_type

        match sensor_type:
            case SensorType.NEPH:
                self._attr_native_unit_of_measurement = "10^-4 m^-1"

            case SensorType.PM10:
                self._attr_native_unit_of_measurement = UnitOfDensity.MICROGRAMS_PER_CUBIC_METER
                self._attr_device_class = SensorDeviceClass.PM10

            case SensorType.PM25:
                self._attr_native_unit_of_measurement = UnitOfDensity.MICROGRAMS_PER_CUBIC_METER
                self._attr_device_class = SensorDeviceClass.PM25

            case SensorType.CO:
                self._attr_native_unit_of_measurement = UnitOfRatio.PARTS_PER_MILLION
                # self._attr_device_class = SensorDeviceClass.CO

            case SensorType.NH3:
                self._attr_native_unit_of_measurement = UnitOfRatio.PARTS_PER_MILLION

            case SensorType.NO:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_HUNDRED_MILLION
                # self._attr_device_class = SensorDeviceClass.NITROGEN_MONOXIDE

            case SensorType.NO2:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_HUNDRED_MILLION
                # self._attr_device_class = SensorDeviceClass.NITROGEN_DIOXIDE

            case SensorType.OZONE:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_HUNDRED_MILLION
                # self._attr_device_class = SensorDeviceClass.OZONE

            case SensorType.SO2:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_HUNDRED_MILLION
                # self._attr_device_class = SensorDeviceClass.SULPHUR_DIOXIDE

            case _:
                _LOGGER.error("Unknown sensor type: %s", sensor_type)
                raise exceptions.HomeAssistantError("Invalid sensor type")

        self._attr_device_info = _device_info(site_id, site_name)

    async def async_update(self):
        await self.controller.async_update()

        sensor_data = self.controller.site_reading(self._site_id, self._sensor_type)
        self._attr_native_value = _select_value(self._attr_native_value, sensor_data)


class AirQualityCategorySensor(SensorEntity):
    """Overall air quality category for a site, e.g. "good" or "fair"."""

    def __init__(self, site_id: str, site_name: str, controller: AirQualityController):
        self._attr_has_entity_name = True
        self._attr_name = "Air quality"
        self._attr_translation_key = "air_quality_category"
        self._attr_unique_id = f"{site_id}_air_quality_category"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = AIR_QUALITY_CATEGORIES
        self._attr_native_value = None
        self._attr_device_info = _device_info(site_id, site_name)
        self.controller = controller

        self._site_id = site_id

    async def async_update(self):
        await self.controller.async_update()

        site_entries = self.controller.site_entries(self._site_id)
        self._attr_native_value = _select_category(self._attr_native_value, site_entries)
