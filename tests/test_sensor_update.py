"""Unit tests for sensor value retention on invalid API responses."""

from datetime import datetime, timedelta

import pytest

from custom_components.nsw_air_quality.sensor import _select_value


def _make_entry(hour, value):
    return {"Site_Id": 123, "Hour": hour, "Value": value}


def _prev_hour():
    return (datetime.now() - timedelta(hours=1)).hour


@pytest.mark.unit
def test_valid_value_is_returned():
    """A valid (non-negative) API value replaces the current value."""
    result = _select_value(10.0, [_make_entry(_prev_hour(), 42.5)])
    assert result == 42.5


@pytest.mark.unit
def test_keeps_previous_when_sensor_data_is_none():
    """None sensor data keeps the previous value."""
    result = _select_value(10.0, None)
    assert result == 10.0


@pytest.mark.unit
def test_keeps_previous_when_no_entry_for_hour():
    """Missing entry for the previous hour keeps the previous value."""
    wrong_hour = (datetime.now() - timedelta(hours=5)).hour
    result = _select_value(10.0, [_make_entry(wrong_hour, 99.0)])
    assert result == 10.0


@pytest.mark.unit
def test_keeps_previous_when_value_is_negative():
    """A negative API value keeps the previous value."""
    result = _select_value(10.0, [_make_entry(_prev_hour(), -1.0)])
    assert result == 10.0


@pytest.mark.unit
def test_keeps_previous_when_value_is_none():
    """A None API value keeps the previous value."""
    result = _select_value(10.0, [_make_entry(_prev_hour(), None)])
    assert result == 10.0


@pytest.mark.unit
def test_zero_is_a_valid_value():
    """Zero is a valid reading and should replace the current value."""
    result = _select_value(10.0, [_make_entry(_prev_hour(), 0.0)])
    assert result == 0.0


@pytest.mark.unit
def test_keeps_previous_across_multiple_bad_reads():
    """The last good value is preserved across consecutive bad reads."""
    current = 5.5
    for bad_value in [-1.0, None, -99.0]:
        current = _select_value(current, [_make_entry(_prev_hour(), bad_value)])
    assert current == 5.5
