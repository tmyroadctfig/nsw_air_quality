from datetime import datetime

from custom_components.nsw_air_quality.air_qual_controller import AirQualityController, fetch_available_sites

import pytest

from custom_components.nsw_air_quality.sensor_type import SensorType

@pytest.mark.asyncio
async def test_fetch_sites() -> None:
    """Tests fetching site info."""

    sites = await fetch_available_sites()

    assert len(sites) > 0
    assert sites.get(500) == "Wollongong"

@pytest.mark.asyncio
async def test_fetch_data() -> None:
    """Tests fetching data from Air Quality Controller."""

    site_id = 500
    controller = AirQualityController()
    controller.add_site(site_id)

    await controller.async_update()

    current_hour = datetime.now().hour
    neph = controller.site_reading(site_id, SensorType.NEPH)
    pm10 = controller.site_reading(site_id, SensorType.PM10)
    no = controller.site_reading(site_id, SensorType.NO)

    current_neph = next((item for item in neph if item["Hour"] == current_hour), None)
    current_pm10 = next((item for item in pm10 if item["Hour"] == current_hour), None)
    current_no = next((item for item in no if item["Hour"] == current_hour), None)

    assert len(neph) == 24
    assert len(pm10) == 24
    assert len(no) == 24

    assert current_neph.get("Site_Id") == site_id
    assert current_pm10.get("Site_Id") == site_id
    assert current_no.get("Site_Id") == site_id

