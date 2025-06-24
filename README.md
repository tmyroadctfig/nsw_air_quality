# NSW Air Quality Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A Home Assistant custom integration that provides real-time air quality data from NSW (New South Wales) Government air monitoring stations across Australia.

## Features

- **Real-time Air Quality Data**: Get current air quality readings from official NSW Government monitoring stations
- **Multiple Pollutants**: Monitor 9 different air quality parameters:
  - **PM2.5** - Fine particulate matter (μg/m³)
  - **PM10** - Coarse particulate matter (μg/m³)
  - **Ozone (O₃)** - Ground-level ozone (pphm)
  - **Nitrogen Dioxide (NO₂)** - (pphm)
  - **Nitrogen Monoxide (NO)** - (pphm)
  - **Carbon Monoxide (CO)** - (ppm)
  - **Sulfur Dioxide (SO₂)** - (pphm)
  - **Ammonia (NH₃)** - (ppm)
  - **Nephelometer (NEPH)** - Light scattering coefficient (10⁻⁴ m⁻¹)

- **136+ Monitoring Stations**: Choose from monitoring stations across NSW including Sydney, Newcastle, Wollongong, and regional areas
- **Automatic Updates**: Data refreshes every 5 minutes
- **Device Grouping**: All sensors from a monitoring station are grouped under a single device
- **Home Assistant Integration**: Full integration with Home Assistant's sensor platform and device registry

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots menu (⋮) in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/tmyroadctfig/nsw_air_quality`
6. Select "Integration" as the category
7. Click "Add"
8. Find "NSW Air Quality" in the integrations list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page][releases]
2. Extract the contents
3. Copy the `custom_components/nsw_air_quality` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Configuration

### Via Home Assistant UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"NSW Air Quality"**
4. Select your desired monitoring station from the dropdown
5. Choose which air quality parameters you want to monitor
6. Click **"Submit"**

### Available Monitoring Stations

The integration automatically fetches the latest list of available monitoring stations. Some popular locations include:

- **Sydney Metro**: Randwick, Rozelle, Liverpool, Bringelly
- **Newcastle**: Wallsend, Newcastle, Beresfield
- **Wollongong**: Wollongong, Port Kembla, Albion Park South
- **Regional NSW**: Bathurst, Orange, Tamworth, Wagga Wagga, and many more

## Usage

Once configured, the integration will create sensors for each selected air quality parameter. Sensors are named using the pattern:

```
sensor.{station_name}_{parameter}
```

For example:
- `sensor.wollongong_pm25`
- `sensor.randwick_ozone`
- `sensor.newcastle_no2`

### Sensor States

- **State**: Current air quality reading
- **Unit of Measurement**: Appropriate unit for each parameter (μg/m³, ppm, pphm, etc.)
- **Device Class**: Proper Home Assistant device classes for PM2.5 and PM10
- **Attributes**: Additional metadata about the reading

## Automation Examples

### Air Quality Alert

```yaml
automation:
  - alias: "High PM2.5 Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.wollongong_pm25
        above: 25
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "High PM2.5 levels detected: {{ states('sensor.wollongong_pm25') }} μg/m³"
```

### Air Quality Dashboard Card

```yaml
type: entities
title: Air Quality - Wollongong
entities:
  - entity: sensor.wollongong_pm25
    name: PM2.5
  - entity: sensor.wollongong_pm10
    name: PM10
  - entity: sensor.wollongong_ozone
    name: Ozone
  - entity: sensor.wollongong_no2
    name: NO₂
```

## Data Source

This integration uses data from the NSW Government's Air Quality Monitoring Network, which operates monitoring stations across New South Wales. The data is sourced from:

- **API Endpoint**: NSW Department of Planning and Environment
- **Update Frequency**: Every 5 minutes
- **Data Accuracy**: Official government monitoring data
- **Coverage**: 136+ monitoring stations across NSW

## Troubleshooting

### Debug Logging

To enable debug logging for troubleshooting:

```yaml
logger:
  default: warning
  logs:
    custom_components.nsw_air_quality: debug
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run unit tests
pytest -m unit

# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/nsw_air_quality
```

### Code Quality

```bash
# Linting
flake8 custom_components/

# Type checking
mypy custom_components/nsw_air_quality/

# Code formatting
black custom_components/ tests/
isort custom_components/ tests/
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues][issues]
- **Discussions**: [GitHub Discussions][discussions]
- **Home Assistant Community**: [Community Forum][community]

---

[releases-shield]: https://img.shields.io/github/release/tmyroadctfig/nsw_air_quality.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tmyroadctfig/nsw_air_quality.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/tmyroadctfig/nsw_air_quality.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge

[releases]: https://github.com/tmyroadctfig/nsw_air_quality/releases
[commits]: https://github.com/tmyroadctfig/nsw_air_quality/commits/main
[hacs]: https://github.com/hacs/integration
[issues]: https://github.com/tmyroadctfig/nsw_air_quality/issues
[discussions]: https://github.com/tmyroadctfig/nsw_air_quality/discussions
[community]: https://community.home-assistant.io/
