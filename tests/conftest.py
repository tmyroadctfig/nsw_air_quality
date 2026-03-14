"""Test configuration and fixtures."""

import sys
import os
from unittest.mock import MagicMock

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Provide a lightweight homeassistant stub when the full package is unavailable.
# In CI the real package is installed; this fallback enables local development
# without the heavy HA dependency tree.
try:
    import homeassistant  # noqa: F401
except ImportError:
    _ha = MagicMock()
    _ha.util.Throttle = lambda min_time: lambda f: f
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
        "homeassistant.helpers.device_registry": _ha.helpers.device_registry,
        "homeassistant.components": _ha.components,
        "homeassistant.components.sensor": _ha.components.sensor,
    }
    sys.modules.update(_ha_modules)
