import logging
from datetime import datetime, timedelta
from urllib.parse import quote

import aiohttp
from homeassistant.util import Throttle

from .const import HEADERS
from .sensor_type import SensorType

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

SITE_DATA_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_Observations"
SITE_DETAILS_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_SiteDetails"
SITE_DATA_ENDPOINT2 = "https://www.airquality.nsw.gov.au/_design/air-quality-api/getsitedetails2/getconcentrationdata-station"


async def fetch_available_sites():
    """Fetch site list from the API."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        _LOGGER.debug("Fetching site list")
        async with session.get(SITE_DETAILS_ENDPOINT) as response:
            if response.status == 200:
                data = await response.json()
                return {site["Site_Id"]: site["SiteName"].title() for site in data}
            else:
                _LOGGER.error("Error fetching site list: %s", response.status)
                return {}


class AirQualityController:
    def __init__(self):
        """Initialize the sensor."""
        self._site_ids = []
        self._site_data = None

    def add_site(self, site_id):
        if site_id not in self._site_ids:
            self._site_ids.append(site_id)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch new data and send a POST request."""

        now = datetime.now()
        start_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:00:00")
        end_date = now.strftime("%Y-%m-%dT%H:00:00")
        sites_list = quote(",".join(map(str, self._site_ids)))
        url = f"{SITE_DATA_ENDPOINT2}?site_ids={sites_list}&start_datetime={start_date}&end_datetime={end_date}"

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            _LOGGER.info("Fetching site readings for site IDs: %s", self._site_ids)
            try:
                async with session.get(url) as response:
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
