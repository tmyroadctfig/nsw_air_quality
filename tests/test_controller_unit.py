import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from custom_components.nsw_air_quality.air_qual_controller import AirQualityController, fetch_available_sites
from custom_components.nsw_air_quality.sensor_type import SensorType


@pytest.mark.unit
def test_controller_initialization():
    """Test that controller initializes correctly."""
    controller = AirQualityController()
    
    assert controller._site_ids == []
    assert controller._site_data is None


@pytest.mark.unit
def test_add_site():
    """Test adding sites to controller."""
    controller = AirQualityController()
    
    controller.add_site(123)
    assert 123 in controller._site_ids
    
    # Adding same site again shouldn't duplicate
    controller.add_site(123)
    assert controller._site_ids.count(123) == 1
    
    # Adding different site should work
    controller.add_site(456)
    assert len(controller._site_ids) == 2
    assert 456 in controller._site_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_available_sites_success():
    """Test successful site fetching with mocked response."""
    mock_response_data = [
        {"Site_Id": 123, "SiteName": "test site one"},
        {"Site_Id": 456, "SiteName": "TEST SITE TWO"},
    ]
    
    with patch('custom_components.nsw_air_quality.air_qual_controller.aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_get.return_value = mock_response
        
        sites = await fetch_available_sites()
        
        assert len(sites) == 2
        assert sites[123] == "Test Site One"
        assert sites[456] == "Test Site Two"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_available_sites_error():
    """Test site fetching with error response."""
    with patch('custom_components.nsw_air_quality.air_qual_controller.aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_get.return_value = mock_response
        
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
    """Test site reading with mock data."""
    controller = AirQualityController()
    
    # Mock site data
    controller._site_data = [
        {
            "Site_Id": 123,
            "Parameter": {"ParameterCode": "PM2.5"},
            "Value": 15.5,
            "Hour": 14
        },
        {
            "Site_Id": 123,
            "Parameter": {"ParameterCode": "PM10"},
            "Value": 25.0,
            "Hour": 14
        },
        {
            "Site_Id": 456,
            "Parameter": {"ParameterCode": "PM2.5"},
            "Value": 12.0,
            "Hour": 14
        }
    ]
    
    # Test PM2.5 reading for site 123
    result = controller.site_reading(123, SensorType.PM25)
    assert len(result) == 1
    assert result[0]["Value"] == 15.5
    assert result[0]["Site_Id"] == 123
    
    # Test PM10 reading for site 123
    result = controller.site_reading(123, SensorType.PM10)
    assert len(result) == 1
    assert result[0]["Value"] == 25.0
    
    # Test reading for different site
    result = controller.site_reading(456, SensorType.PM25)
    assert len(result) == 1
    assert result[0]["Value"] == 12.0
    
    # Test reading for non-existent sensor type
    result = controller.site_reading(123, SensorType.CO)
    assert len(result) == 0
