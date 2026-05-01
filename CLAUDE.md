# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## NSW Air Quality — Developer Notes

This is a Home Assistant custom integration (HACS-compatible) that polls the NSW Government air quality API and exposes pollutant readings as HA sensor entities.

## Commands

```bash
# Run unit tests (no network required)
/usr/local/bin/python3 -m pytest -m unit

# Run a single test file or test function
/usr/local/bin/python3 -m pytest tests/test_controller_unit.py
/usr/local/bin/python3 -m pytest tests/test_controller_unit.py::test_add_site

# Run with coverage report
/usr/local/bin/python3 -m pytest -m unit --cov=custom_components/nsw_air_quality --cov-report=term-missing

# Run integration tests (requires live NSW API access)
/usr/local/bin/python3 -m pytest -m integration --timeout=60

# Lint
/usr/local/bin/python3 -m flake8 custom_components/ tests/

# Type check
/usr/local/bin/python3 -m mypy custom_components/

# Format (check only)
/usr/local/bin/python3 -m black --check custom_components/ tests/
/usr/local/bin/python3 -m isort --check-only custom_components/ tests/

# Format (apply)
/usr/local/bin/python3 -m black custom_components/ tests/
/usr/local/bin/python3 -m isort custom_components/ tests/
```

## Testing

Use TDD when adding new behaviour or fixing bugs:

1. Write a failing test that reproduces the bug or describes the new behaviour.
2. Run it to confirm it fails.
3. Make the minimal code change to pass the test.
4. Run the full unit suite to confirm nothing regressed.

Mark each test with `@pytest.mark.unit` (no external calls) or `@pytest.mark.integration` (calls the live API). The CI pipeline runs only unit tests on PRs; integration tests run on push to main.

## Architecture

The integration follows the standard Home Assistant config-entry pattern. The data flow is:

**Config Flow → Controller → Sensors**

1. `config_flow.py` — UI setup wizard. Fetches available monitoring sites from the NSW API, lets the user pick a site and which pollutants to track, then writes a config entry.

2. `air_qual_controller.py` — `AirQualityController` is the single object shared across all sensors for a given site. It owns the HTTP session and fetches concentration data from the NSW API (throttled to one call per 5 minutes via HA's `Throttle` decorator). `site_reading(site_id, sensor_type)` extracts the most-recent reading from the raw JSON, handling the PM2.5 naming discrepancy (`"PM2.5"` in the API vs `PM25` in the enum).

3. `sensor.py` — One `AirQualitySensor` entity per pollutant per site. All sensors for a site share one device. `_select_value()` enforces data quality: it ignores `None`, negative, or missing values and retains the previous state rather than going `unavailable`.

4. `sensor_type.py` — `SensorType` enum enumerating the 9 supported pollutants (NEPH, PM10, PM25, CO, NH3, NO, NO2, OZONE, SO2).

### API Endpoints

- **Sites list:** `https://data.airquality.nsw.gov.au/api/Data/get_SiteDetails`
- **Concentration data:** `https://www.airquality.nsw.gov.au/_design/air-quality-api/getsitedetails2/getconcentrationdata-station`

Both are unauthenticated public endpoints. The `HEADERS` constant in `const.py` sets the User-Agent string sent with every request.

### conftest.py shim

`tests/conftest.py` injects a lightweight stub of the `homeassistant` package when the real package is not installed. This lets unit tests run without a full HA install. The stub mocks `Throttle` (wraps the function as-is), `config_entries`, and core constants. If a test starts failing because a newly imported HA symbol is missing from the stub, add it there.

## Code Style

- Line length: 127 characters (Black + flake8 configured).
- Python 3.12; `match`/`case` is used in `sensor.py` for per-pollutant configuration.
- mypy is run in strict mode for `custom_components.nsw_air_quality.*`.
- isort is configured for Black compatibility (`force_sort_within_sections`, known first-party: `custom_components`).
