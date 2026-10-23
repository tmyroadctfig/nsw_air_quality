"""Unit tests for sensor value selection and retention on invalid API responses."""

import pytest

from custom_components.nsw_air_quality.sensor import _select_value


def _make_entry(hour, value, date="2026-10-21", frequency="Hourly average"):
    return {
        "Site_Id": 123,
        "Parameter": {"ParameterCode": "OZONE", "Frequency": frequency},
        "Date": date,
        "Hour": hour,
        "Value": value,
    }


@pytest.mark.unit
def test_valid_value_is_returned():
    """A valid (non-negative) API value replaces the current value."""
    result = _select_value(10.0, [_make_entry(21, 42.5)])
    assert result == 42.5


@pytest.mark.unit
def test_uses_most_recent_valid_hour():
    """Readings arrive an hour or two late, so the latest valid hour wins rather than a fixed hour."""
    entries = [_make_entry(19, 1.0), _make_entry(21, 3.0), _make_entry(20, 2.0), _make_entry(22, None)]
    assert _select_value(10.0, entries) == 3.0


@pytest.mark.unit
def test_most_recent_hour_spans_dates():
    """Yesterday's late hours are older than today's early hours."""
    entries = [_make_entry(24, 1.0, date="2026-10-20"), _make_entry(1, 2.0, date="2026-10-21")]
    assert _select_value(10.0, entries) == 2.0


@pytest.mark.unit
def test_ignores_rolling_averages():
    """Rolling-average rows (e.g. ozone 4h/8h) are not the hourly reading."""
    entries = [
        _make_entry(21, 9.0, frequency="4h rolling average derived from 1h average"),
        _make_entry(21, 1.5),
        _make_entry(21, 8.0, frequency="8h rolling average derived from 1h average"),
    ]
    assert _select_value(10.0, entries) == 1.5


@pytest.mark.unit
def test_keeps_previous_when_sensor_data_is_none():
    """None sensor data keeps the previous value."""
    result = _select_value(10.0, None)
    assert result == 10.0


@pytest.mark.unit
def test_keeps_previous_when_no_entries():
    """An empty response keeps the previous value."""
    assert _select_value(10.0, []) == 10.0


@pytest.mark.unit
def test_keeps_previous_when_only_rolling_averages():
    """Without an hourly-average row the previous value is kept."""
    entries = [_make_entry(21, 9.0, frequency="8h rolling average derived from 1h average")]
    assert _select_value(10.0, entries) == 10.0


@pytest.mark.unit
def test_keeps_previous_when_value_is_negative():
    """A negative API value keeps the previous value."""
    result = _select_value(10.0, [_make_entry(21, -1.0)])
    assert result == 10.0


@pytest.mark.unit
def test_keeps_previous_when_value_is_none():
    """A None API value keeps the previous value."""
    result = _select_value(10.0, [_make_entry(21, None)])
    assert result == 10.0


@pytest.mark.unit
def test_skips_invalid_latest_hour():
    """An invalid latest reading falls back to the latest valid one."""
    entries = [_make_entry(20, 4.0), _make_entry(21, -0.01)]
    assert _select_value(10.0, entries) == 4.0


@pytest.mark.unit
def test_zero_is_a_valid_value():
    """Zero is a valid reading and should replace the current value."""
    result = _select_value(10.0, [_make_entry(21, 0.0)])
    assert result == 0.0


@pytest.mark.unit
def test_keeps_previous_across_multiple_bad_reads():
    """The last good value is preserved across consecutive bad reads."""
    current = 5.5
    for bad_value in [-1.0, None, -99.0]:
        current = _select_value(current, [_make_entry(21, bad_value)])
    assert current == 5.5
