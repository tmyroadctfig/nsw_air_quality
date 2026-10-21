"""Unit tests for the config and options flows."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant import config_entries

from custom_components.nsw_air_quality import async_setup_entry
from custom_components.nsw_air_quality.config_flow import NswAirQualityConfigFlow
from custom_components.nsw_air_quality.const import CONF_SITE_ID, CONF_SITE_NAME
from custom_components.nsw_air_quality.sensor_type import SensorType

pytestmark = pytest.mark.skipif(isinstance(config_entries, MagicMock), reason="Requires the real homeassistant package")

ENTRY_ID = "entry-1"


def make_entry(data=None, options=None):
    entry = MagicMock()
    entry.entry_id = ENTRY_ID
    entry.data = {CONF_SITE_ID: 123, CONF_SITE_NAME: "Test Site", **{s.name: True for s in SensorType}, **(data or {})}
    entry.options = options or {}
    return entry


def make_options_flow(entry):
    flow = NswAirQualityConfigFlow.async_get_options_flow(entry)
    flow.hass = MagicMock()
    flow.hass.config_entries.async_get_known_entry.return_value = entry
    flow.handler = ENTRY_ID
    return flow


def form_defaults(result):
    return {str(key): key.default() for key in result["data_schema"].schema}


@pytest.mark.unit
def test_get_options_flow_returns_options_flow():
    """HA calls async_get_options_flow(entry) on the class; it must return an OptionsFlow (issue #1)."""
    flow = NswAirQualityConfigFlow.async_get_options_flow(make_entry())

    assert isinstance(flow, config_entries.OptionsFlow)


@pytest.mark.unit
def test_config_flow_supports_options():
    """The Configure button is only shown when the flow supports options."""
    assert NswAirQualityConfigFlow.async_supports_options_flow(make_entry())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_form_defaults_to_current_selection():
    """Options from a previous save take precedence over the original setup data."""
    entry = make_entry(data={"CO": False, "NH3": False}, options={"NH3": True})
    flow = make_options_flow(entry)

    result = await flow.async_step_init()

    assert result["type"] == "form"
    assert result["step_id"] == "init"
    defaults = form_defaults(result)
    assert set(defaults) == {s.name for s in SensorType}
    assert defaults["CO"] is False
    assert defaults["NH3"] is True
    assert defaults["PM25"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_form_saves_selection():
    flow = make_options_flow(make_entry())
    selection = {s.name: s is SensorType.PM25 for s in SensorType}

    result = await flow.async_step_init(selection)

    assert result["type"] == "create_entry"
    assert result["data"] == selection


@pytest.mark.unit
@pytest.mark.asyncio
async def test_setup_entry_reloads_when_options_change():
    """Changing options must reload the entry so sensors are added or removed."""
    hass = MagicMock()
    hass.data = {"nsw_air_quality": {}}
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock(return_value=True)
    entry = make_entry()

    assert await async_setup_entry(hass, entry)

    entry.add_update_listener.assert_called_once()
    entry.async_on_unload.assert_called_once_with(entry.add_update_listener.return_value)
    listener = entry.add_update_listener.call_args.args[0]
    await listener(hass, entry)
    hass.config_entries.async_reload.assert_awaited_once_with(ENTRY_ID)
