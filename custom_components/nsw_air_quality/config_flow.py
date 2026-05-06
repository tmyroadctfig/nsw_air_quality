import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .air_qual_controller import fetch_available_sites
from .const import CONF_SITE_ID, CONF_SITE_NAME, DOMAIN
from .sensor_type import SensorType

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

            site_name = available_sites.get(site_id)
            _LOGGER.info("Setting up site %s: %s", site_id, site_name)
            user_input[CONF_SITE_NAME] = site_name

            return self.async_create_entry(title=site_name, data=user_input)

        sensor_options = {vol.Optional(sensor.name.upper(), default=True): bool for sensor in SensorType}

        schema = vol.Schema(
            {
                vol.Required(CONF_SITE_ID): vol.In(available_sites),
                **sensor_options,  # Unpacking the dynamically generated dictionary
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @callback
    def _async_entry_for_site_id(self, site_id):
        for entry in self._async_current_entries():
            if entry.data.get(CONF_SITE_ID) == site_id:
                return entry
        return None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NswAirQualityOptionsFlow(config_entry)


class NswAirQualityOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        sensor_options = {}
        for sensor in SensorType:
            key = sensor.name.upper()
            current = self._config_entry.options.get(key, self._config_entry.data.get(key, True))
            sensor_options[vol.Optional(key, default=current)] = bool

        return self.async_show_form(step_id="init", data_schema=vol.Schema(sensor_options))
