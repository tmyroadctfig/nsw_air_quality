"""Unit tests for config_flow options flow."""

from unittest.mock import MagicMock

import pytest

from custom_components.nsw_air_quality.config_flow import NswAirQualityConfigFlow, NswAirQualityOptionsFlow
from custom_components.nsw_air_quality.sensor_type import SensorType


def _make_config_entry(data=None, options=None):
    entry = MagicMock()
    entry.data = data or {s.name.upper(): True for s in SensorType}
    entry.options = options or {}
    return entry


@pytest.mark.unit
def test_async_get_options_flow_returns_options_flow():
    config_entry = _make_config_entry()
    flow = NswAirQualityConfigFlow.async_get_options_flow(config_entry)
    assert isinstance(flow, NswAirQualityOptionsFlow)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_flow_shows_form_without_user_input():
    config_entry = _make_config_entry()
    flow = NswAirQualityOptionsFlow(config_entry)
    result = await flow.async_step_init(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert result["data_schema"] is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_flow_saves_user_input():
    config_entry = _make_config_entry()
    flow = NswAirQualityOptionsFlow(config_entry)

    user_input = {s.name.upper(): True for s in SensorType}
    user_input["PM25"] = False

    result = await flow.async_step_init(user_input=user_input)

    assert result["type"] == "create_entry"
    assert result["data"] == user_input


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_flow_prefers_options_over_data():
    data = {s.name.upper(): True for s in SensorType}
    options = {"PM25": False, "CO": False}
    config_entry = _make_config_entry(data=data, options=options)

    flow = NswAirQualityOptionsFlow(config_entry)
    result = await flow.async_step_init(user_input=None)

    assert result["type"] == "form"
    schema_keys = {str(k): k.default() for k in result["data_schema"].schema}
    assert schema_keys["PM25"] is False
    assert schema_keys["CO"] is False
    assert schema_keys["PM10"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_options_flow_defaults_missing_sensor_to_true():
    config_entry = _make_config_entry(data={}, options={})
    flow = NswAirQualityOptionsFlow(config_entry)
    result = await flow.async_step_init(user_input=None)

    assert result["type"] == "form"
    schema_keys = {str(k): k.default() for k in result["data_schema"].schema}
    assert all(v is True for v in schema_keys.values())
