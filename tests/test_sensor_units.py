"""Unit tests for sensor units of measurement."""

import pytest

from custom_components.nsw_air_quality import sensor


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    ["CONCENTRATION_MICROGRAMS_PER_CUBIC_METER", "CONCENTRATION_PARTS_PER_MILLION"],
)
def test_does_not_use_deprecated_concentration_constants(name):
    """HA removes these constants in 2027.8; use UnitOfDensity/UnitOfRatio instead."""
    assert not hasattr(sensor, name)
