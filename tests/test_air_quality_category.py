"""Unit tests for the overall site air quality category sensor."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.nsw_air_quality.air_qual_controller import AirQualityController
from custom_components.nsw_air_quality.const import AIR_QUALITY_CATEGORIES
from custom_components.nsw_air_quality.sensor import AirQualityCategorySensor, _select_category


def _make_entry(parameter_code, category, hour=21, date="2026-10-21", site_id=123):
    return {
        "Site_Id": site_id,
        "Parameter": {"ParameterCode": parameter_code},
        "Date": date,
        "Hour": hour,
        "Value": None,
        "AirQualityCategory": category,
    }


@pytest.mark.unit
def test_site_entries_returns_all_rows_for_site():
    """site_entries returns every row for the site regardless of parameter."""
    controller = AirQualityController()
    controller._site_data = [
        _make_entry("PM2.5", "GOOD"),
        _make_entry("AQC", "GOOD"),
        _make_entry("PM10", "FAIR", site_id=456),
    ]

    result = controller.site_entries(123)

    assert [entry["Parameter"]["ParameterCode"] for entry in result] == ["PM2.5", "AQC"]


@pytest.mark.unit
def test_site_entries_no_data():
    """site_entries returns None before the first successful fetch."""
    assert AirQualityController().site_entries(123) is None


@pytest.mark.unit
def test_prefers_official_site_aqc_row():
    """The site-level AQC row is the official rating and wins over per-pollutant categories."""
    entries = [_make_entry("PM2.5", "POOR"), _make_entry("AQC", "FAIR")]

    assert _select_category(None, entries) == "fair"


@pytest.mark.unit
def test_falls_back_to_worst_pollutant_category():
    """Without an AQC row, the overall category is the worst pollutant category."""
    entries = [_make_entry("OZONE", "GOOD"), _make_entry("PM2.5", "POOR"), _make_entry("PM10", "FAIR")]

    assert _select_category(None, entries) == "poor"


@pytest.mark.unit
def test_uses_most_recent_rated_hour():
    """Older hours are ignored once a newer hour has a rating."""
    entries = [
        _make_entry("PM2.5", "HAZARDOUS", hour=20),
        _make_entry("PM2.5", "GOOD", hour=21),
        _make_entry("PM2.5", "GOOD", hour=1, date="2026-10-20"),
    ]

    assert _select_category(None, entries) == "good"


@pytest.mark.unit
def test_ignores_hours_without_a_rating():
    """The latest hours often have no category yet; fall back to the latest rated hour."""
    entries = [_make_entry("PM2.5", "FAIR", hour=21), _make_entry("PM2.5", None, hour=22), _make_entry("AQC", "N/A", hour=22)]

    assert _select_category(None, entries) == "fair"


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw, expected",
    [("VERY POOR", "very_poor"), ("Extremely Poor", "extremely_poor"), ("very-poor", "very_poor"), ("HAZARDOUS", "hazardous")],
)
def test_normalises_multi_word_categories(raw, expected):
    """API categories are mapped onto the sensor's enum options."""
    assert _select_category(None, [_make_entry("AQC", raw)]) == expected


@pytest.mark.unit
@pytest.mark.parametrize("entries", [None, [], [_make_entry("PM2.5", None)], [_make_entry("PM2.5", "UNKNOWN")]])
def test_keeps_previous_category_without_a_rating(entries):
    """Missing or unrecognised ratings keep the previous state rather than going unknown."""
    assert _select_category("fair", entries) == "fair"


@pytest.mark.unit
def test_categories_are_ordered_best_to_worst():
    assert AIR_QUALITY_CATEGORIES == ["good", "fair", "poor", "very_poor", "extremely_poor", "hazardous"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_category_sensor_update():
    """The sensor refreshes the controller and reports the site's category."""
    controller = MagicMock()
    controller.async_update = AsyncMock()
    controller.site_entries.return_value = [_make_entry("AQC", "FAIR")]

    sensor = AirQualityCategorySensor(123, "Test Site", controller)
    await sensor.async_update()

    controller.async_update.assert_awaited_once()
    controller.site_entries.assert_called_once_with(123)
    assert sensor._attr_native_value == "fair"
    assert sensor._attr_options == AIR_QUALITY_CATEGORIES
    assert sensor._attr_unique_id == "123_air_quality_category"
