import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from .const import DOMAIN, CONF_SITE_IDS

SITE_DETAILS_ENDPOINT = "https://data.airquality.nsw.gov.au/api/Data/get_SiteDetails"

async def fetch_available_sites():
    """Fetch site list from the API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(SITE_DETAILS_ENDPOINT) as response:
            if response.status == 200:
                data = await response.json()
                return {site["Site_Id"]: site["SiteName"] for site in data}
            return {}

class NswAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Fetch the latest site list from API
        available_sites = await fetch_available_sites()

        if not available_sites:
            errors["base"] = "cannot_fetch_sites"
            return self.async_show_form(step_id="user", errors=errors)

        if user_input is not None:
            return self.async_create_entry(title="PM10 Sensors", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_SITE_IDS, default=[]): vol.All(
                vol.Length(min=1),
                vol.In(available_sites.keys())
            )
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
