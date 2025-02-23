from datetime import timedelta
import aiohttp
from datetime import datetime
from homeassistant.util import Throttle

import logging

from custom_components.nsw_air_quality.const import HEADERS
from custom_components.nsw_air_quality.sensor_type import SensorType

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

SITE_DATA_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_Observations"
SITE_DETAILS_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_SiteDetails"

async def fetch_available_sites():
    """Fetch site list from the API."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        _LOGGER.debug("Fetching site list")
        async with session.get(SITE_DETAILS_ENDPOINT) as response:
            if response.status == 200:
                data = await response.json()
                return { site["Site_Id"]: site["SiteName"].title() for site in data }
            else:
                _LOGGER.error("Error fetching site list: %s", response.status)
                return {}

class AirQualityController:
    def __init__(self):
        """Initialize the sensor."""
        self._site_ids = []
        self._site_data = None

    def add_site(self, site_id):
        self._site_ids.append(site_id)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch new data and send a POST request."""

        payload = {
            "Parameters": [ "NEPH", "PM10", "PM2.5", "CO", "NH3", "NO", "NO2", "OZONE", "SO2" ],
            "Sites": self._site_ids,
            "StartDate": (datetime.now() - timedelta( days = 1 )).strftime("%Y-%m-%d"),
            "EndDate": datetime.now().strftime("%Y-%m-%d"),
            "Categories": [ "Averages", "Site AQC" ],
            "Frequency": [ "Hourly average"]
        }

        async with aiohttp.ClientSession(headers = HEADERS) as session:
            _LOGGER.info("Fetching site readings for site IDs: %s", self._site_ids)
            try:
                async with session.post(SITE_DATA_ENDPOINT, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._site_data = data  # Update sensor state
                    else:
                        _LOGGER.error("Error fetching site list: %s", response.status)
                        self._site_data = f"Error {response.status}"
            except aiohttp.ClientError as e:
                self._site_data = f"Request failed: {str(e)}"

    def site_reading(self, site_id, sensor_type: SensorType):
        if not self._site_data:
            return None

        parameter_code = sensor_type.name
        if sensor_type == SensorType.PM25:
            parameter_code = "PM2.5"

        site_data = [entry for entry in self._site_data if entry.get("Site_Id") == site_id]
        sensor_data = [entry for entry in site_data if entry.get("Parameter").get("ParameterCode") == parameter_code]
        return sensor_data