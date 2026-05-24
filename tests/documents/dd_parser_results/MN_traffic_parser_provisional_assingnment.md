# 📑 Data Dictionary: Provisional Entity Assignment Report
**Source Blueprint:** `MN_traffic_dd.csv`

### 📊 Classification Summary
- **WeatherObservations**: 7 fields
- **RegionalHolidays**: 1 fields
- **TrafficData**: 1 fields

---

### 📋 Detailed Assignments
| Attribute             | Provisional Entity Assignment   | Native Type   |
|-----------------------|---------------------------------|---------------|
| `holiday`             | `RegionalHolidays`              | `float`       |
| `temp`                | `WeatherObservations`           | `float`       |
| `rain_1h`             | `WeatherObservations`           | `float`       |
| `snow_1h`             | `WeatherObservations`           | `float`       |
| `clouds_all`          | `WeatherObservations`           | `int`         |
| `weather_main`        | `WeatherObservations`           | `str`         |
| `weather_description` | `WeatherObservations`           | `str`         |
| `date_time`           | `WeatherObservations`           | `str`         |
| `traffic_volume`      | `TrafficData`                   | `int`         |

---
*Report generated via automated dd-parser post-processing.*