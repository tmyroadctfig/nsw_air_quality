import aiohttp

SITE_DATA_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_Observations"

class AirQualityController:
    def __init__(self, site_ids: []):
        """Initialize the sensor."""
        self.site_ids = site_ids
        self.site_data = None

    async def async_update(self):
        """Fetch new data and send a POST request."""

        payload = {
            "Parameters": [ "NEPH", "PM10" ],
            "Sites": self.site_ids,
            "StartDate": (now() - timedelta( hours = 1 )).strftime("%Y-%m-%dT%H:00:00"),
            "EndDate": now().strftime("%Y-%m-%dT%H:00:00"),
            "Categories": [ "Averages", "Site AQC" ],
            "Frequency": [ "Hourly average"]
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(SITE_DATA_ENDPOINT, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.site_data = data.get("status", "unknown")  # Update sensor state
                    else:
                        self.site_data = f"Error {response.status}"
            except aiohttp.ClientError as e:
                self.site_data = f"Request failed: {str(e)}"