"""
Sensor for NSW Air Quality Data
"""

from functools import partial
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .const import CONF_SITE_ID, DOMAIN
from .sensor_type import SensorType

# Sensor unique IDs before they were scoped to a site, which made a second site's sensors collide with the first's
LEGACY_UNIQUE_IDS = {sensor_type.name.lower() for sensor_type in SensorType}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (if applicable)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an instance from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data  # Store config data

    await er.async_migrate_entries(hass, entry.entry_id, partial(_migrate_unique_id, entry.data[CONF_SITE_ID]))

    # Forward the entry to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Reload when the options flow changes which pollutants are tracked
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


@callback
def _migrate_unique_id(site_id: Any, entity_entry: er.RegistryEntry) -> dict[str, Any] | None:
    """Rewrite a legacy unscoped unique ID (e.g. "pm25") to the site-scoped form (e.g. "123_pm25")."""
    if entity_entry.unique_id in LEGACY_UNIQUE_IDS:
        return {"new_unique_id": f"{site_id}_{entity_entry.unique_id}"}
    return None


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry so sensors match the updated options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)  # Remove stored data

    return unload_ok
