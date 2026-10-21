from typing import Final

DOMAIN: Final = "nsw_air_quality"

SHORT_ATTRIBUTION: Final = "NSW Air Quality"
MODEL_NAME: Final = "Air Monitoring Site"

CONF_SITE_ID: Final = "site_id"
CONF_SITE_NAME: Final = "site_name"
CONF_CONTROLLER: Final = "controller"

# Parameter Frequency of the plain hourly reading, as opposed to rolling averages such as ozone 4h/8h
HOURLY_AVERAGE_FREQUENCY: Final = "Hourly average"

HEADERS = {"User-Agent": "home-assistant/tmyroadctfig/nsw_air_quality"}

CONCENTRATION_PARTS_PER_HUNDRED_MILLION = "pphm"

# NSW air quality categories, ordered best to worst. These are the enum options of the site category sensor.
AIR_QUALITY_CATEGORIES: Final = ["good", "fair", "poor", "very_poor", "extremely_poor", "hazardous"]

# ParameterCode of the API row carrying the official site-level air quality category
SITE_AQC_PARAMETER_CODE: Final = "AQC"
