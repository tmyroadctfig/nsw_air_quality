"""Test configuration and fixtures."""

import os
import sys
from unittest.mock import MagicMock

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Minimal stand-ins for HA's flow base classes, used by the stub below so config/options
# flows can be unit tested without a full HA install.
class _StubFlow:
    hass = None
    handler = None

    def async_create_entry(self, title="", data=None):
        return {"type": "create_entry", "title": title, "data": data or {}}

    def async_show_form(self, step_id, data_schema=None, errors=None):
        return {"type": "form", "step_id": step_id, "data_schema": data_schema, "errors": errors or {}}

    def async_abort(self, reason):
        return {"type": "abort", "reason": reason}


class _StubConfigFlow(_StubFlow):
    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)

    def _async_current_entries(self):
        return []

    @staticmethod
    def async_get_options_flow(config_entry):
        raise NotImplementedError

    @classmethod
    def async_supports_options_flow(cls, config_entry):
        return cls.async_get_options_flow is not _StubConfigFlow.async_get_options_flow


class _StubOptionsFlow(_StubFlow):
    @property
    def config_entry(self):
        # Mirrors HA: the entry is looked up by the flow's handler (the entry id)
        return self.hass.config_entries.async_get_known_entry(self.handler)


# Plain base class so sensor entities can be instantiated and updated in unit tests.
class _StubSensorEntity:
    pass


# Provide a lightweight homeassistant stub when the full package is unavailable.
# In CI the real package is installed; this fallback enables local development
# without the heavy HA dependency tree.
try:
    import homeassistant  # noqa: F401
except ImportError:
    _ha = MagicMock()
    _ha.util.Throttle = lambda min_time: lambda f: f
    _ha.core.callback = lambda f: f

    _ha.config_entries.ConfigFlow = _StubConfigFlow
    _ha.config_entries.OptionsFlow = _StubOptionsFlow
    _ha.components.sensor.SensorEntity = _StubSensorEntity

    _ha_modules = {
        "homeassistant": _ha,
        "homeassistant.util": _ha.util,
        "homeassistant.config_entries": _ha.config_entries,
        "homeassistant.core": _ha.core,
        "homeassistant.exceptions": _ha.exceptions,
        "homeassistant.const": _ha.const,
        "homeassistant.helpers": _ha.helpers,
        "homeassistant.helpers.typing": _ha.helpers.typing,
        "homeassistant.helpers.entity": _ha.helpers.entity,
        "homeassistant.helpers.entity_platform": _ha.helpers.entity_platform,
        "homeassistant.helpers.entity_registry": _ha.helpers.entity_registry,
        "homeassistant.helpers.device_registry": _ha.helpers.device_registry,
        "homeassistant.components": _ha.components,
        "homeassistant.components.sensor": _ha.components.sensor,
    }
    sys.modules.update(_ha_modules)
