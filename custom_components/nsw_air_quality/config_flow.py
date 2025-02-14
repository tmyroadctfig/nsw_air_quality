import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_SITE_ID, CONF_NEPH_CREATE, CONF_PM10_CREATE

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
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        # Fetch the latest site list from API
        available_sites = await fetch_available_sites()

        if not available_sites:
            errors["base"] = "cannot_fetch_sites"
            return self.async_show_form(step_id="user", errors=errors)

        if user_input is not None:
            return self.async_create_entry(title="NSW Air Quality", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_SITE_ID): vol.In(available_sites),
            vol.Optional(CONF_NEPH_CREATE, default=True): bool,
            vol.Optional(CONF_PM10_CREATE, default=True): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @callback
    def async_get_options_flow(self):
        return NswAirQualityConfigFlow(self.config_entry)