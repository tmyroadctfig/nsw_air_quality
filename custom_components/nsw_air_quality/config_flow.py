import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

import logging

from .air_qual_controller import fetch_available_sites
from .const import DOMAIN, CONF_SITE_ID, CONF_NEPH_CREATE, CONF_PM10_CREATE, CONF_SITE_NAME

_LOGGER = logging.getLogger(__name__)

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
            site_id = user_input[CONF_SITE_ID]
            existing_entry = self._async_entry_for_site_id(site_id)
            if existing_entry:
                _LOGGER.error("Site already configured %s", existing_entry)
                return self.async_abort("Already configured")

            _LOGGER.info("Setting up site %s", existing_entry)
            user_input[CONF_SITE_NAME] = available_sites.get(site_id)

            return self.async_create_entry(title=user_input[CONF_SITE_NAME], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_SITE_ID): vol.In(available_sites),
            vol.Optional(CONF_NEPH_CREATE, default=True): bool,
            vol.Optional(CONF_PM10_CREATE, default=True): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @callback
    def _async_entry_for_site_id(self, site_id):
        for entry in self._async_current_entries():
            if entry.data.get(CONF_SITE_ID) == site_id:
                return entry
        return None

    @callback
    def async_get_options_flow(self):
        return NswAirQualityConfigFlow(self.config_entry)