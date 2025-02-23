
from typing import Final

DOMAIN: Final = "nsw_air_quality"

SHORT_ATTRIBUTION: Final = "NSW Air Quality"
MODEL_NAME: Final = "Air Monitoring Site"

CONF_SITE_ID: Final = "site_id"
CONF_SITE_NAME: Final = "site_name"
CONF_CONTROLLER: Final = "controller"

HEADERS = { "User-Agent": "home-assistant/tmyroadctfig/nsw_air_quality" }

CONCENTRATION_PARTS_PER_HUNDRED_MILLION = "pphm"