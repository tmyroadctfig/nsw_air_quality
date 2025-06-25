"""Unit tests for the air quality controller."""
import pytest
from aioresponses import aioresponses

from custom_components.nsw_air_quality.air_qual_controller import (
    AirQualityController,
    fetch_available_sites,
    SITE_DETAILS_ENDPOINT,
)
from custom_components.nsw_air_quality.sensor_type import SensorType


@pytest.mark.unit
def test_controller_initialization():
    """Test controller initialization."""
    controller = AirQualityController()
    
    assert controller._site_ids == []
    assert controller._site_data is None


@pytest.mark.unit
def test_add_site():
    """Test adding a site to the controller."""
    controller = AirQualityController()
    
    controller.add_site(123)
    
    assert 123 in controller._site_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_available_sites_success():
    """Test successful site fetching with mocked response."""
    mock_response_data = [
        {"Site_Id": 123, "SiteName": "test site one"},
        {"Site_Id": 456, "SiteName": "TEST SITE TWO"},
    ]
    
    with aioresponses() as m:
        m.get(SITE_DETAILS_ENDPOINT, payload=mock_response_data)
        
        sites = await fetch_available_sites()
        
        assert len(sites) == 2
        assert sites[123] == "Test Site One"
        assert sites[456] == "Test Site Two"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_available_sites_error():
    """Test site fetching with error response."""
    with aioresponses() as m:
        m.get(SITE_DETAILS_ENDPOINT, status=500)
        
        sites = await fetch_available_sites()
        
        assert sites == {}


@pytest.mark.unit
def test_site_reading_no_data():
    """Test site reading when no data is available."""
    controller = AirQualityController()
    
    result = controller.site_reading(123, SensorType.PM25)
    
    assert result is None


@pytest.mark.unit
def test_site_reading_with_data():
    """Test site reading when data is available."""
    controller = AirQualityController()
    
    # Mock some data in the expected format
    controller._site_data = [
        {
            "Site_Id": 123,
            "Parameter": {"ParameterCode": "PM2.5"},
            "Value": 15.5
        },
        {
            "Site_Id": 123,
            "Parameter": {"ParameterCode": "PM10"},
            "Value": 25.0
        }
    ]
    
    result = controller.site_reading(123, SensorType.PM25)
    assert len(result) == 1
    assert result[0]["Value"] == 15.5
    
    result = controller.site_reading(123, SensorType.PM10)
    assert len(result) == 1
    assert result[0]["Value"] == 25.0
    
    # Test non-existent sensor type
    result = controller.site_reading(123, SensorType.CO)
    assert result == []
