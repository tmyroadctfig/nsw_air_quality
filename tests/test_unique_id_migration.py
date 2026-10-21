"""Unit tests for site-scoped sensor unique IDs and migrating the legacy ones."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.nsw_air_quality import _migrate_unique_id, async_setup_entry
from custom_components.nsw_air_quality.const import CONF_SITE_ID
from custom_components.nsw_air_quality.sensor import AirQualitySensor
from custom_components.nsw_air_quality.sensor_type import SensorType


@pytest.mark.unit
@pytest.mark.parametrize("sensor_type", list(SensorType))
def test_sensor_unique_id_is_scoped_to_site(sensor_type):
    """Two sites tracking the same pollutant must not share a unique ID."""
    sensor = AirQualitySensor(123, "Test Site", MagicMock(), sensor_type)

    assert sensor._attr_unique_id == f"123_{sensor_type.name.lower()}"


@pytest.mark.unit
@pytest.mark.parametrize("sensor_type", list(SensorType))
def test_migrates_legacy_unique_id(sensor_type):
    """Legacy unscoped IDs (e.g. "pm25") are rewritten to the site-scoped form."""
    entity_entry = MagicMock(unique_id=sensor_type.name.lower())

    assert _migrate_unique_id(123, entity_entry) == {"new_unique_id": f"123_{sensor_type.name.lower()}"}


@pytest.mark.unit
@pytest.mark.parametrize("unique_id", ["123_pm25", "123_air_quality_category", "something_else"])
def test_leaves_other_unique_ids_alone(unique_id):
    """Already-migrated and unrelated IDs are not changed, so migration is idempotent."""
    assert _migrate_unique_id(123, MagicMock(unique_id=unique_id)) is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_setup_entry_migrates_unique_ids_before_creating_sensors():
    """Registry entries are migrated for this config entry before the sensor platform is set up."""
    hass = MagicMock()
    hass.data = {"nsw_air_quality": {}}
    calls = []
    hass.config_entries.async_forward_entry_setups = AsyncMock(side_effect=lambda *args: calls.append("forward"))
    entry = MagicMock(entry_id="entry-1", data={CONF_SITE_ID: 123})

    with patch(
        "custom_components.nsw_air_quality.er.async_migrate_entries",
        AsyncMock(side_effect=lambda *args: calls.append("migrate")),
    ) as migrate:
        assert await async_setup_entry(hass, entry)

    assert calls == ["migrate", "forward"]
    migrate_hass, entry_id, callback = migrate.await_args.args
    assert (migrate_hass, entry_id) == (hass, "entry-1")
    assert callback(MagicMock(unique_id="pm10")) == {"new_unique_id": "123_pm10"}
