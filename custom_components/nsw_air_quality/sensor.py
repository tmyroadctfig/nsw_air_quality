"""Sensor platform for NSW Air Quality Data """

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfConcentration
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .air_qual_controller import AirQualityController
from .const import DOMAIN, SHORT_ATTRIBUTION, MODEL_NAME, CONF_SITE_ID, CONF_NEPH_CREATE, CONF_PM10_CREATE

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    site_id = entry.data[CONF_SITE_ID]
    site_name = entry.title

    create_neph = entry.options.get(
        CONF_NEPH_CREATE, entry.data.get(CONF_NEPH_CREATE)
    )

    create_pm10 = entry.options.get(
        CONF_PM10_CREATE, entry.data.get(CONF_PM10_CREATE)
    )

    controller = AirQualityController([site_id])
    sensors = []

    if create_neph is True:
        sensors.append(PM10Sensor(site_id + "_neph", site_name, controller))

    if create_pm10 is True:
        sensors.append(PM10Sensor(site_id, site_name, controller))

    async_add_entities(sensors, True)

class PM10Sensor(SensorEntity):
    """Representation of a PM10 sensor."""

    def __init__(self, site_id: str, site_name: str, controller: AirQualityController, initial_value: float = None):
        """Initialize the sensor."""
        self._attr_name = site_name
        self._attr_unique_id = f"pm10_{site_id}"
        self._attr_native_unit_of_measurement = UnitOfConcentration.MICROGRAMS_PER_CUBIC_METER
        self._attr_device_class = "pm10"
        self._attr_state_class = "measurement"
        self._attr_native_value = initial_value
        self.controller = controller

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self.site_id}")},
            manufacturer=SHORT_ATTRIBUTION,
            model=MODEL_NAME,
            name=self.site_id,
        )

    def update(self):
        """Fetch new state data (dummy implementation)."""
        # In a real implementation, fetch data from an API or hardware sensor
        self._attr_native_value = 12.5  # Example PM10 value