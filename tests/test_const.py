import pytest

from custom_components.nsw_air_quality.const import (
    DOMAIN,
    SHORT_ATTRIBUTION,
    MODEL_NAME,
    CONF_SITE_ID,
    CONF_SITE_NAME,
    CONF_CONTROLLER,
    HEADERS,
    CONCENTRATION_PARTS_PER_HUNDRED_MILLION,
)


@pytest.mark.unit
def test_domain_constant():
    """Test that domain constant is correct."""
    assert DOMAIN == "nsw_air_quality"


@pytest.mark.unit
def test_attribution_constants():
    """Test attribution and model constants."""
    assert SHORT_ATTRIBUTION == "NSW Air Quality"
    assert MODEL_NAME == "Air Monitoring Site"


@pytest.mark.unit
def test_config_constants():
    """Test configuration key constants."""
    assert CONF_SITE_ID == "site_id"
    assert CONF_SITE_NAME == "site_name"
    assert CONF_CONTROLLER == "controller"


@pytest.mark.unit
def test_headers_format():
    """Test that headers are properly formatted."""
    assert isinstance(HEADERS, dict)
    assert "User-Agent" in HEADERS
    assert "home-assistant" in HEADERS["User-Agent"]


@pytest.mark.unit
def test_concentration_unit():
    """Test concentration unit constant."""
    assert CONCENTRATION_PARTS_PER_HUNDRED_MILLION == "pphm"
