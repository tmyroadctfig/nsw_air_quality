"""Sensor platform for NSW Air Quality Data """

from datetime import datetime

from homeassistant import exceptions
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

import logging

from .air_qual_controller import AirQualityController
from .const import DOMAIN, SHORT_ATTRIBUTION, MODEL_NAME, CONF_SITE_ID, CONF_NEPH_CREATE, CONF_PM10_CREATE, CONF_CONTROLLER
from .sensor_type import SensorType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(CONF_CONTROLLER, AirQualityController())

    controller = hass.data[DOMAIN][CONF_CONTROLLER]
    site_id = entry.data[CONF_SITE_ID]
    site_name = entry.title

    controller.add_site(site_id)

    create_neph = entry.options.get(
        CONF_NEPH_CREATE, entry.data.get(CONF_NEPH_CREATE)
    )

    create_pm10 = entry.options.get(
        CONF_PM10_CREATE, entry.data.get(CONF_PM10_CREATE)
    )

    sensors = []

    if create_neph is True:
        sensors.append(AirQualitySensor(site_id, site_name, controller, SensorType.NEPH))

    if create_pm10 is True:
        sensors.append(AirQualitySensor(site_id, site_name, controller, SensorType.PM10))

    async_add_entities(sensors, True)

class AirQualitySensor(SensorEntity):
    def __init__(self, site_id: str, site_name: str, controller: AirQualityController, sensor_type: SensorType, initial_value: float = None):
        """Initialize the sensor."""
        _LOGGER.info("Initializing site '%s' (site-id:%s) sensor type: '%s'", site_name, site_id, sensor_type)

        self._attr_name = f"{site_name} {sensor_type.name}"
        self._attr_unique_id = f"{sensor_type.name}_{site_id}"
        self._attr_state_class = "measurement"
        self._attr_native_value = initial_value
        self.controller = controller

        self._site_id = site_id
        self._sensor_type = sensor_type

        match sensor_type:
            case SensorType.NEPH:
                self._attr_native_unit_of_measurement = "10^-4 m^-1"
                self._attr_device_class = "neph"

            case SensorType.PM10:
                self._attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                self._attr_device_class = "pm10"

            case _:
                _LOGGER.error("Unknown sensor type: %s", sensor_type)
                raise exceptions.HomeAssistantError("Invalid sensor type")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self._site_id}")},
            manufacturer=SHORT_ATTRIBUTION,
            model=MODEL_NAME,
            name=f"{site_name} (site:{self._site_id})",
        )

    async def async_update(self):
        await self.controller.async_update()

        sensor_data = self.controller.site_reading(self._site_id, self._sensor_type)
        if sensor_data is None:
            self._attr_native_value = None
            return

        current_hour = datetime.now().hour
        entry = next((item for item in sensor_data if item["Hour"] == current_hour), None)
        self._attr_native_value = entry.get("Value")