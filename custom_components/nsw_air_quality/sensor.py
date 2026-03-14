"""Sensor platform for NSW Air Quality Data"""

import logging
from datetime import datetime, timedelta

from homeassistant import exceptions
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, CONCENTRATION_PARTS_PER_MILLION
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .air_qual_controller import AirQualityController
from .const import (
    CONCENTRATION_PARTS_PER_HUNDRED_MILLION,
    CONF_CONTROLLER,
    CONF_SITE_ID,
    DOMAIN,
    MODEL_NAME,
    SHORT_ATTRIBUTION,
)
from .sensor_type import SensorType

_LOGGER = logging.getLogger(__name__)


def _select_value(current_value, sensor_data):
    """Return the new sensor value, or keep current_value if API data is invalid.

    Keeps the previous value when sensor_data is None, no entry exists for the
    previous hour, or the reported value is None or negative.
    """
    if sensor_data is None:
        return current_value

    previous_hour = (datetime.now() - timedelta(hours=1)).hour
    entry = next((item for item in sensor_data if item["Hour"] == previous_hour), None)
    if entry is None:
        return current_value

    value = entry.get("Value")
    if value is None or value < 0:
        _LOGGER.debug("Invalid API value %s, keeping previous value", value)
        return current_value

    return value


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(CONF_CONTROLLER, AirQualityController())

    controller = hass.data[DOMAIN][CONF_CONTROLLER]
    site_id = entry.data[CONF_SITE_ID]
    site_name = entry.title

    controller.add_site(site_id)

    sensors = []

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
        self._attr_unique_id = f"{sensor_type.name.lower()}"
        self._attr_state_class = "measurement"
        self._attr_native_value = initial_value
        self.controller = controller

        self._site_id = site_id
        self._sensor_type = sensor_type

        match sensor_type:
            case SensorType.NEPH:
                self._attr_native_unit_of_measurement = "10^-4 m^-1"

            case SensorType.PM10:
                self._attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                self._attr_device_class = SensorDeviceClass.PM10

            case SensorType.PM25:
                self._attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                self._attr_device_class = SensorDeviceClass.PM25

            case SensorType.CO:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
                # self._attr_device_class = SensorDeviceClass.CO

            case SensorType.NH3:
                self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION

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

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self._site_id}")},
            manufacturer=SHORT_ATTRIBUTION,
            model=MODEL_NAME,
            name=f"{site_name}",
        )

    async def async_update(self):
        await self.controller.async_update()

        sensor_data = self.controller.site_reading(self._site_id, self._sensor_type)
        self._attr_native_value = _select_value(self._attr_native_value, sensor_data)
