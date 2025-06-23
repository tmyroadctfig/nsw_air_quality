import pytest

from custom_components.nsw_air_quality.sensor_type import SensorType


@pytest.mark.unit
def test_sensor_type_enum():
    """Test that SensorType enum has expected values."""
    expected_sensors = [
        SensorType.NEPH,
        SensorType.PM10,
        SensorType.PM25,
        SensorType.CO,
        SensorType.NH3,
        SensorType.NO,
        SensorType.NO2,
        SensorType.OZONE,
        SensorType.SO2,
    ]
    
    assert len(SensorType) == 9
    for sensor in expected_sensors:
        assert sensor in SensorType


@pytest.mark.unit
def test_sensor_type_names():
    """Test that sensor type names are correct."""
    assert SensorType.PM25.name == "PM25"
    assert SensorType.PM10.name == "PM10"
    assert SensorType.OZONE.name == "OZONE"
    assert SensorType.NO2.name == "NO2"


@pytest.mark.unit
def test_sensor_type_values():
    """Test that sensor type values are unique."""
    values = [sensor.value for sensor in SensorType]
    assert len(values) == len(set(values))  # All values should be unique
