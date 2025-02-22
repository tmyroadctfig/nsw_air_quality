﻿from custom_components.nsw_air_quality.air_qual_controller import AirQualityController

import pytest

from custom_components.nsw_air_quality.sensor_type import SensorType


@pytest.mark.asyncio
async def test_fetch_data() -> None:
    """Tests fetching data from Air Quality Controller."""

    site_id = 500
    controller = AirQualityController()
    controller.add_site(site_id)

    await controller.async_update()

    neph = controller.site_reading(site_id, SensorType.NEPH)
    pm10 = controller.site_reading(site_id, SensorType.PM10)

    assert neph.get("Site_Id") == site_id
    assert pm10.get("Site_Id") == site_id
