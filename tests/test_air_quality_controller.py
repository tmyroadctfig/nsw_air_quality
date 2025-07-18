import logging
from datetime import datetime, timedelta

import pytest

from custom_components.nsw_air_quality.air_qual_controller import AirQualityController, fetch_available_sites
from custom_components.nsw_air_quality.sensor_type import SensorType

LOGGER = logging.getLogger(__name__)

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires network access - run manually")
async def test_fetch_sites() -> None:
    """Tests fetching site info."""

    sites = await fetch_available_sites()

    assert len(sites) > 0
    # Test structure rather than specific values to avoid API changes breaking tests
    assert all(isinstance(site_id, int) for site_id in sites.keys())
    assert all(isinstance(name, str) for name in sites.values())
    # Only test for Wollongong if it exists, don't fail if API changes
    if 500 in sites:
        assert "wollongong" in sites.get(500).lower()

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skip(reason="Requires network access - run manually")
async def test_fetch_data() -> None:
    """Tests fetching data from Air Quality Controller."""

    site_id = 500
    controller = AirQualityController()
    controller.add_site(site_id)

    await controller.async_update()

    previous_hour = (datetime.now() - timedelta(hours = 1)).hour
    neph = controller.site_reading(site_id, SensorType.NEPH)
    pm10 = controller.site_reading(site_id, SensorType.PM10)
    pm25 = controller.site_reading(site_id, SensorType.PM25)
    no = controller.site_reading(site_id, SensorType.NO)

    current_neph = next((item for item in neph if item["Hour"] == previous_hour), None)
    current_pm10 = next((item for item in pm10 if item["Hour"] == previous_hour), None)
    current_pm25 = next((item for item in pm25 if item["Hour"] == previous_hour), None)
    current_no = next((item for item in no if item["Hour"] == previous_hour), None)

    assert len(neph) == 24
    assert len(pm10) == 24
    assert len(pm25) == 24
    assert len(no) == 24

    assert current_neph.get("Site_Id") == site_id
    assert current_pm10.get("Site_Id") == site_id
    assert current_pm25.get("Site_Id") == site_id
    assert current_no.get("Site_Id") == site_id

    assert current_neph.get("Value") is not None
    assert current_pm10.get("Value") is not None
    assert current_pm25.get("Value") is not None
    assert current_no.get("Value") is not None

    assert current_neph.get("Hour") == previous_hour
    assert current_pm10.get("Hour") == previous_hour
    assert current_pm25.get("Hour") == previous_hour
    assert current_no.get("Hour") == previous_hour

    LOGGER.info("Current neph info: %s", current_neph)
    LOGGER.info("Current PM10 info: %s", current_pm10)
    LOGGER.info("Current PM25 info: %s", current_pm25)
    LOGGER.info("Current NO info: %s", current_no)
