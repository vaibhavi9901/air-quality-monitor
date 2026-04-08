"""
routes/air_quality.py — Real-time air quality endpoints.

Handles UPDATE_DELAYED state (#8) and returns date/last_updated (#15).
"""

import logging
import time
from flask import Blueprint, request, current_app
import services.openmeteo_service as openmeteo
import services.alert_service as alerts
from utils.responses import success, error

log = logging.getLogger(__name__)
air_quality_bp = Blueprint("air_quality", __name__)

POPULAR_MY_STATIONS = [
    "Kuala Lumpur","Petaling Jaya","Shah Alam","Johor Bahru","Penang",
    "Ipoh","Kota Kinabalu","Kuching","Alor Setar","Kuantan",
]

# ── UPDATE_DELAYED response (#8) ──────────────────────────────────────────────
def _update_delayed_response():
    return success({
        "status":       "UPDATE_DELAYED",
        "message":      "UPDATE DELAYED",
        "available":    False,
        "aqi":          None,
        "risk":         None,
        "date":         None,
        "last_updated": None,
    }, message="UPDATE DELAYED")


@air_quality_bp.get("/city/<path:city>")
def current_by_city(city: str):
    t0 = time.perf_counter()
    reading = openmeteo.get_by_city(city)

    if reading is None:
        # Try default city
        default = current_app.config["DEFAULT_CITY"]
        reading = openmeteo.get_by_city(default)
        if reading is None:
            return _update_delayed_response()   # #8

    t_after_fetch = time.perf_counter()
    alert_payload = alerts.evaluate_alert(reading)
    data = reading.to_dict()

    # Add date / last_updated (#15)
    from services.openmeteo_service import _format_datetime
    dt = _format_datetime(reading.timestamp)
    data["date"]         = dt["date"]
    data["last_updated"] = dt["last_updated"]
    data["status"]       = "ok"
    data["alert"]        = alert_payload
    data["data_source"]  = "Open-Meteo"

    total_ms = (time.perf_counter() - t0) * 1000
    fetch_ms = (t_after_fetch - t0) * 1000
    print(f"[AQ] GET /city/{city}: total {total_ms:.0f}ms (openmeteo {fetch_ms:.0f}ms, alert+serialize {total_ms - fetch_ms:.0f}ms)")
    return success(data, message="Air quality data retrieved successfully.")


@air_quality_bp.get("/geo")
def current_by_geo():
    try:
        lat = float(request.args["lat"])
        lon = float(request.args["lon"])
    except (KeyError, ValueError):
        return error("Query parameters 'lat' and 'lon' are required and must be numbers.")

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return error("Invalid latitude or longitude values.")

    reading = openmeteo.get_by_coordinates(lat, lon)
    if reading is None:
        # Fallback to default city so the UI still gets data (e.g. Open-Meteo timeout)
        default_city = current_app.config["DEFAULT_CITY"]
        reading = openmeteo.get_by_city(default_city)
        if reading is None:
            return _update_delayed_response()   # #8

    alert_payload = alerts.evaluate_alert(reading)
    data = reading.to_dict()

    from services.openmeteo_service import _format_datetime
    dt = _format_datetime(reading.timestamp)
    data["date"]         = dt["date"]
    data["last_updated"] = dt["last_updated"]
    data["status"]       = "ok"
    data["alert"]        = alert_payload
    data["data_source"]  = "Open-Meteo"

    return success(data, message="Air quality data retrieved successfully.")


@air_quality_bp.get("/search")
def search_stations():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return error("Query parameter 'q' is required.")
    stations = openmeteo.search_stations(keyword)
    return success(stations, message=f"Found {len(stations)} result(s) for '{keyword}'.")


@air_quality_bp.get("/stations")
def popular_stations():
    results = []
    for city in POPULAR_MY_STATIONS:
        reading = openmeteo.get_by_city(city)
        if reading:
            results.append({
                "city":  reading.city,
                "aqi":   reading.aqi,
                "risk":  reading.risk["label"],
                "color": reading.risk["color"],
                "icon":  reading.risk["icon"],
                "lat":   reading.latitude,
                "lon":   reading.longitude,
            })
    return success(results, message=f"Retrieved data for {len(results)} stations.")


@air_quality_bp.get("/risk-tiers")
def risk_tiers():
    from models.aqi import RISK_TIERS
    return success(RISK_TIERS, message="Risk tier definitions.")

# """
# routes/air_quality.py — Real-time air quality endpoints.

# GET /api/air-quality/city/<city>
#     Fetch current AQI for a named city.

# GET /api/air-quality/geo?lat=<lat>&lon=<lon>
#     Fetch current AQI by GPS coordinates (from browser geolocation).

# GET /api/air-quality/search?q=<keyword>
#     Search for monitoring stations by name.

# GET /api/air-quality/stations
#     List popular Malaysian monitoring stations.
# """

# from flask import Blueprint, request, current_app
# import waqi_service as waqi
# import alert_service as alerts
# from responses import success, error

# air_quality_bp = Blueprint("air_quality", __name__)

# POPULAR_MY_STATIONS = [
#     "Kuala Lumpur", "Petaling Jaya", "Shah Alam",
#     "Johor Bahru", "Penang", "Ipoh", "Kota Kinabalu",
#     "Kuching", "Alor Setar", "Kuantan",
# ]


# @air_quality_bp.get("/city/<path:city>")
# def current_by_city(city: str):
#     """
#     Return current air quality for *city*.
#     Example: GET /api/air-quality/city/Kuala%20Lumpur
#     """
#     reading = waqi.get_by_city(city)
#     if reading is None:
#         default = current_app.config["DEFAULT_CITY"]
#         reading = waqi.get_by_city(default)
#         if reading is None:
#             return error(f"Could not retrieve air quality data for '{city}'.", 503)

#     alert_payload = alerts.evaluate_alert(reading)
#     data = reading.to_dict()
#     data["alert"] = alert_payload   # override with enriched alert block

#     return success(data, message="Air quality data retrieved successfully.")


# @air_quality_bp.get("/geo")
# def current_by_geo():
#     """
#     Return current AQI for a lat/lon pair (browser geolocation).
#     Example: GET /api/air-quality/geo?lat=3.1390&lon=101.6869
#     """
#     try:
#         lat = float(request.args["lat"])
#         lon = float(request.args["lon"])
#     except (KeyError, ValueError):
#         return error("Query parameters 'lat' and 'lon' are required and must be numbers.")

#     if not (-90 <= lat <= 90 and -180 <= lon <= 180):
#         return error("Invalid latitude or longitude values.")

#     reading = waqi.get_by_coordinates(lat, lon)
#     if reading is None:
#         return error("Could not retrieve air quality data for the given coordinates.", 503)

#     alert_payload = alerts.evaluate_alert(reading)
#     data = reading.to_dict()
#     data["alert"] = alert_payload

#     return success(data, message="Air quality data retrieved successfully.")


# @air_quality_bp.get("/search")
# def search_stations():
#     """
#     Search monitoring stations.
#     Example: GET /api/air-quality/search?q=Penang
#     """
#     keyword = request.args.get("q", "").strip()
#     if not keyword:
#         return error("Query parameter 'q' is required.")

#     stations = waqi.search_stations(keyword)
#     return success(stations, message=f"Found {len(stations)} station(s) for '{keyword}'.")


# @air_quality_bp.get("/stations")
# def popular_stations():
#     """
#     Return a list of popular Malaysian monitoring stations with
#     their current AQI values.
#     """
#     results = []
#     for city in POPULAR_MY_STATIONS:
#         reading = waqi.get_by_city(city)
#         if reading:
#             results.append({
#                 "city":  reading.city,
#                 "aqi":   reading.aqi,
#                 "risk":  reading.risk["label"],
#                 "color": reading.risk["color"],
#                 "icon":  reading.risk["icon"],
#                 "lat":   reading.latitude,
#                 "lon":   reading.longitude,
#             })

#     return success(results, message=f"Retrieved data for {len(results)} stations.")


# @air_quality_bp.get("/risk-tiers")
# def risk_tiers():
#     """Return the full list of AQI risk tiers and their thresholds."""
#     from aqi import RISK_TIERS
#     return success(RISK_TIERS, message="Risk tier definitions.")
