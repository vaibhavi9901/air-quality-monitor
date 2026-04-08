"""
services/openmeteo_service.py — Real-time air quality via Open-Meteo.

Changes vs previous version:
  - get_by_city/get_by_coordinates now return an UPDATE_DELAYED status
    when the live fetch fails and no cache exists (#8)
  - get_by_city queries a small grid of points around the city and returns
    the MAX AQI reading among them (#13)
  - to_dict() on AirQualityReading now includes date and last_updated
    formatted fields (#15)
"""

from __future__ import annotations
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

import requests
from flask import current_app
from models.aqi import AirQualityReading, Pollutants
from utils.cache import cache

log = logging.getLogger(__name__)

GEOCODING_URL   = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

HOURLY_VARS = "pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide,carbon_monoxide,us_aqi"

# Small grid offsets (degrees) to simulate querying nearby stations (#13)
# Covers roughly a 10km radius around the city centre
GRID_OFFSETS = [
    (0.0,  0.0),    # centre
    (0.05, 0.0),    # north
    (-0.05, 0.0),   # south
    (0.0,  0.05),   # east
    (0.0, -0.05),   # west
]


def geocode_city(city: str) -> Optional[dict]:
    cache_key = f"geo:city:{city.lower().replace(' ','_')}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        timeout = 20  # generous for production (e.g. Render) where latency to Open-Meteo can be high
        resp = requests.get(GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=timeout)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results: return None
        geo = results[0]
        result = {
            "name":         geo.get("name", city),
            "latitude":     geo["latitude"],
            "longitude":    geo["longitude"],
            "country":      geo.get("country", ""),
            "country_code": geo.get("country_code", ""),
        }
        cache.set(cache_key, result, 86400)
        return result
    except requests.RequestException as exc:
        log.error("Geocoding failed for '%s': %s", city, exc)
        return None


def _fetch_air_quality(lat: float, lon: float) -> Optional[dict]:
    try:
        timeout = 20  # generous for production (e.g. Render)
        resp = requests.get(AIR_QUALITY_URL, params={
            "latitude": lat, "longitude": lon,
            "hourly": HOURLY_VARS,
            "timezone": "auto",
            "forecast_days": 2,
        }, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log.error("Open-Meteo AQ request failed (%s, %s): %s", lat, lon, exc)
        return None


def _find_current_index(times: list[str]) -> int:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    best_idx, best_diff = 0, float("inf")
    for i, t in enumerate(times):
        try:
            dt   = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
            diff = abs((dt - now).total_seconds())
            if diff < best_diff:
                best_diff, best_idx = diff, i
        except ValueError:
            continue
    return best_idx


def _parse_reading(raw: dict, city_name: str, country: str) -> AirQualityReading:
    hourly = raw.get("hourly", {})
    times  = hourly.get("time", [])
    idx    = _find_current_index(times)

    def _val(key):
        arr = hourly.get(key, [])
        v   = arr[idx] if idx < len(arr) else None
        return float(v) if v is not None else None

    aqi  = _val("us_aqi") or 0.0
    pm25 = _val("pm2_5")
    pm10 = _val("pm10")

    pollutants = Pollutants(
        pm25=pm25, pm10=pm10,
        no2=_val("nitrogen_dioxide"),
        o3=_val("ozone"),
        so2=_val("sulphur_dioxide"),
        co=_val("carbon_monoxide"),
    )

    dominant = "pm25"
    if pm25 and pm25 > 35.4: dominant = "pm25"
    elif pm10 and pm10 > 154: dominant = "pm10"

    timestamp = times[idx] if idx < len(times) else datetime.now(timezone.utc).isoformat()

    return AirQualityReading(
        aqi=aqi,
        station=city_name,
        city=city_name.split(",")[0].strip(),
        country=country,
        latitude=float(raw.get("latitude", 0)),
        longitude=float(raw.get("longitude", 0)),
        timestamp=timestamp,
        pollutants=pollutants,
        dominant_pollutant=dominant,
    )


def _format_datetime(iso_str: str) -> dict:
    """Return date and last_updated as human-readable strings (#15)."""
    try:
        dt = datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)
        return {
            "date":         dt.strftime("%A, %d %B %Y"),      # e.g. "Friday, 14 March 2026"
            "last_updated": dt.strftime("%I:%M %p UTC"),       # e.g. "08:00 AM UTC"
        }
    except Exception:
        return {"date": "", "last_updated": ""}


def _reading_to_response(reading: AirQualityReading, status: str = "ok") -> dict:
    """
    Convert a reading to the full response dict including date/last_updated (#15).
    """
    d = reading.to_dict()
    dt_fields = _format_datetime(reading.timestamp)
    d["date"]         = dt_fields["date"]
    d["last_updated"] = dt_fields["last_updated"]
    d["status"]       = status
    return d


def get_by_city(city: str) -> Optional[AirQualityReading]:
    """
    Fetch the highest-AQI reading from a small grid around the city (#13).
    Returns None and logs UPDATE_DELAYED if all grid points fail (#8).
    Grid points are fetched in parallel to reduce latency.
    """
    t0 = time.perf_counter()
    cache_key = f"openmeteo:city:{city.lower().replace(' ','_')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # 1. Geocoding (external HTTP) — often the first bottleneck
    t_geo = time.perf_counter()
    geo = geocode_city(city)
    if geo is None:
        return None
    geo_ms = (time.perf_counter() - t_geo) * 1000
    print(f"[AQ] get_by_city {city}: geocode {geo_ms:.0f}ms")

    lat, lon = geo["latitude"], geo["longitude"]

    # 2. Fetch grid points in parallel (was 5 sequential HTTP calls — main bottleneck)
    def fetch_one(dlat: float, dlon: float):
        raw = _fetch_air_quality(lat + dlat, lon + dlon)
        if raw:
            return _parse_reading(raw, geo["name"], geo.get("country", ""))
        return None

    t_fetch = time.perf_counter()
    readings = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_one, dlat, dlon): (dlat, dlon) for dlat, dlon in GRID_OFFSETS}
        for fut in as_completed(futures):
            reading = fut.result()
            if reading:
                readings.append(reading)
    fetch_ms = (time.perf_counter() - t_fetch) * 1000
    print(f"[AQ] get_by_city {city}: grid fetch {fetch_ms:.0f}ms ({len(readings)}/{len(GRID_OFFSETS)} points)")

    if not readings:
        log.warning("UPDATE_DELAYED: all grid points failed for '%s'", city)
        return None   # caller handles UPDATE_DELAYED (#8)

    # Pick the reading with the highest AQI (#13)
    worst = max(readings, key=lambda r: r.aqi)

    ttl = current_app.config["REALTIME_CACHE_TTL"]
    cache.set(cache_key, worst, ttl)
    total_ms = (time.perf_counter() - t0) * 1000
    print(f"[AQ] get_by_city {city}: total {total_ms:.0f}ms (geocode + {len(GRID_OFFSETS)} parallel AQI fetches)")
    return worst


def get_by_coordinates(lat: float, lon: float) -> Optional[AirQualityReading]:
    cache_key = f"openmeteo:geo:{lat:.3f}:{lon:.3f}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    raw = _fetch_air_quality(lat, lon)
    if raw is None:
        log.warning("UPDATE_DELAYED: coordinates (%.3f, %.3f) fetch failed", lat, lon)
        return None

    reading = _parse_reading(raw, f"{lat:.3f},{lon:.3f}", "")
    ttl = current_app.config["REALTIME_CACHE_TTL"]
    cache.set(cache_key, reading, ttl)
    return reading


def get_hourly_forecast(city: str) -> Optional[list[dict]]:
    cache_key = f"openmeteo:forecast:{city.lower().replace(' ','_')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    geo = geocode_city(city)
    if geo is None:
        return None

    raw = _fetch_air_quality(geo["latitude"], geo["longitude"])
    if raw is None:
        return None

    hourly = raw.get("hourly", {})
    times  = hourly.get("time", [])
    points = []
    for i, t in enumerate(times):
        def _v(key):
            arr = hourly.get(key, [])
            v   = arr[i] if i < len(arr) else None
            return float(v) if v is not None else None
        points.append({
            "time":             t,
            "us_aqi":           _v("us_aqi"),
            "pm2_5":            _v("pm2_5"),
            "pm10":             _v("pm10"),
            "nitrogen_dioxide": _v("nitrogen_dioxide"),
            "ozone":            _v("ozone"),
        })

    ttl = current_app.config["FORECAST_CACHE_TTL"]
    cache.set(cache_key, points, ttl)
    return points


def search_stations(keyword: str) -> list[dict]:
    cache_key = f"openmeteo:search:{keyword.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        resp = requests.get(GEOCODING_URL,
            params={"name": keyword, "count": 10, "language": "en", "format": "json"},
            timeout=5)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException as exc:
        log.error("Geocoding search failed: %s", exc)
        return []
    stations = [{"station": r.get("name",""), "lat": r.get("latitude"),
                 "lon": r.get("longitude"), "country": r.get("country","")} for r in results]
    cache.set(cache_key, stations, 300)
    return stations

# """
# services/openmeteo_service.py — Real-time & forecast air quality via Open-Meteo.
 
# Open-Meteo Air Quality API: https://open-meteo.com/en/docs/air-quality-api
# Open-Meteo Geocoding API:   https://open-meteo.com/en/docs/geocoding-api
 
# Key advantages over WAQI:
#   • Completely free — no API key or registration required.
#   • Returns hourly US AQI directly plus raw pollutant values.
#   • Provides up to 5-day hourly forecast in a single call.
#   • Global coverage including all Malaysian cities.
 
# Endpoints used:
#   Geocoding:   GET https://geocoding-api.open-meteo.com/v1/search
#   Air Quality: GET https://air-quality-api.open-meteo.com/v1/air-quality
# """
 
# from __future__ import annotations
# import logging
# import requests
# from datetime import datetime, timezone
# from typing import Optional
 
# from flask import current_app
# from models.aqi import AirQualityReading, Pollutants
# from utils.cache import cache
 
# log = logging.getLogger(__name__)
 
# GEOCODING_URL  = "https://geocoding-api.open-meteo.com/v1/search"
# AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
 
# # Hourly variables we request from Open-Meteo
# HOURLY_VARS = ",".join([
#     "pm2_5",
#     "pm10",
#     "nitrogen_dioxide",
#     "ozone",
#     "sulphur_dioxide",
#     "carbon_monoxide",
#     "us_aqi",
# ])
 
 
# # ── Geocoding ────────────────────────────────────────────────────────────────
 
# def geocode_city(city: str) -> Optional[dict]:
#     """
#     Convert a city name to lat/lon using Open-Meteo's free geocoding API.
#     Returns {name, latitude, longitude, country, country_code} or None.
#     """
#     cache_key = f"geo:city:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
 
#     try:
#         resp = requests.get(
#             GEOCODING_URL,
#             params={"name": city, "count": 1, "language": "en", "format": "json"},
#             timeout=5,
#         )
#         resp.raise_for_status()
#         results = resp.json().get("results", [])
#         if not results:
#             log.warning("Geocoding found no results for '%s'", city)
#             return None
#         geo = results[0]
#         result = {
#             "name":         geo.get("name", city),
#             "latitude":     geo["latitude"],
#             "longitude":    geo["longitude"],
#             "country":      geo.get("country", ""),
#             "country_code": geo.get("country_code", ""),
#         }
#         cache.set(cache_key, result, 86400)   # city coords rarely change — cache 24 h
#         return result
#     except requests.RequestException as exc:
#         log.error("Geocoding request failed for '%s': %s", city, exc)
#         return None
 
 
# # ── Air quality fetch ────────────────────────────────────────────────────────
 
# def _fetch_air_quality(lat: float, lon: float) -> Optional[dict]:
#     """
#     Call Open-Meteo Air Quality API for the given coordinates.
#     Returns the raw JSON response dict or None on failure.
#     """
#     try:
#         resp = requests.get(
#             AIR_QUALITY_URL,
#             params={
#                 "latitude":     lat,
#                 "longitude":    lon,
#                 "hourly":       HOURLY_VARS,
#                 "timezone":     "auto",
#                 "forecast_days": 2,       # today + tomorrow = 48 hourly points
#             },
#             timeout=5,
#         )
#         resp.raise_for_status()
#         return resp.json()
#     except requests.RequestException as exc:
#         log.error("Open-Meteo air quality request failed (%s, %s): %s", lat, lon, exc)
#         return None
 
 
# def _find_current_index(times: list[str]) -> int:
#     """
#     Find the index in the hourly time array that is closest to now.
#     Open-Meteo times are strings like "2024-05-01T13:00".
#     """
#     now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
#     best_idx = 0
#     best_diff = float("inf")
#     for i, t in enumerate(times):
#         try:
#             dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
#             diff = abs((dt - now).total_seconds())
#             if diff < best_diff:
#                 best_diff = diff
#                 best_idx = i
#         except ValueError:
#             continue
#     return best_idx
 
 
# def _parse_reading(raw: dict, city_name: str, country: str) -> AirQualityReading:
#     """Convert an Open-Meteo response into an AirQualityReading."""
#     hourly = raw.get("hourly", {})
#     times  = hourly.get("time", [])
#     idx    = _find_current_index(times)
 
#     def _val(key: str) -> Optional[float]:
#         arr = hourly.get(key, [])
#         v = arr[idx] if idx < len(arr) else None
#         return float(v) if v is not None else None
 
#     aqi  = _val("us_aqi") or 0.0
#     pm25 = _val("pm2_5")
#     pm10 = _val("pm10")
#     no2  = _val("nitrogen_dioxide")
#     o3   = _val("ozone")
#     so2  = _val("sulphur_dioxide")
#     co   = _val("carbon_monoxide")
 
#     pollutants = Pollutants(pm25=pm25, pm10=pm10, no2=no2, o3=o3, so2=so2, co=co)
 
#     # Determine dominant pollutant (highest AQI contribution)
#     dominant = "pm25"
#     if pm25 and pm25 > 35.4:
#         dominant = "pm25"
#     elif pm10 and pm10 > 154:
#         dominant = "pm10"
#     elif o3 and o3 > 70:
#         dominant = "ozone"
 
#     timestamp = times[idx] if idx < len(times) else datetime.now(timezone.utc).isoformat()
 
#     return AirQualityReading(
#         aqi=aqi,
#         station=city_name,
#         city=city_name.split(",")[0].strip(),
#         country=country,
#         latitude=raw.get("latitude", 0.0),
#         longitude=raw.get("longitude", 0.0),
#         timestamp=timestamp,
#         pollutants=pollutants,
#         dominant_pollutant=dominant,
#     )
 
 
# # ── Public API (mirrors the old waqi_service interface) ──────────────────────
 
# def get_by_city(city: str) -> Optional[AirQualityReading]:
#     """
#     Fetch current air quality for a named city.
#     Geocodes the city first, then queries Open-Meteo.
#     Results are cached for REALTIME_CACHE_TTL seconds.
#     """
#     cache_key = f"openmeteo:city:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         log.debug("Cache hit: %s", cache_key)
#         return cached
 
#     geo = geocode_city(city)
#     if geo is None:
#         return None
 
#     raw = _fetch_air_quality(geo["latitude"], geo["longitude"])
#     if raw is None:
#         return None
 
#     reading = _parse_reading(raw, geo["name"], geo.get("country", ""))
#     ttl = current_app.config["REALTIME_CACHE_TTL"]
#     cache.set(cache_key, reading, ttl)
#     return reading
 
 
# def get_by_coordinates(lat: float, lon: float) -> Optional[AirQualityReading]:
#     """
#     Fetch current air quality for GPS coordinates (browser geolocation).
#     Results are cached for REALTIME_CACHE_TTL seconds.
#     """
#     cache_key = f"openmeteo:geo:{lat:.3f}:{lon:.3f}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
 
#     raw = _fetch_air_quality(lat, lon)
#     if raw is None:
#         return None
 
#     reading = _parse_reading(raw, f"{lat:.3f},{lon:.3f}", "")
#     ttl = current_app.config["REALTIME_CACHE_TTL"]
#     cache.set(cache_key, reading, ttl)
#     return reading
 
 
# def get_hourly_forecast(city: str) -> Optional[list[dict]]:
#     """
#     Return up to 48 raw hourly data points for a city.
#     Each dict contains: time, us_aqi, pm2_5, pm10, nitrogen_dioxide, ozone.
#     Used by forecast_service.py to build the 24-hour forecast.
#     """
#     cache_key = f"openmeteo:forecast:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
 
#     geo = geocode_city(city)
#     if geo is None:
#         return None
 
#     raw = _fetch_air_quality(geo["latitude"], geo["longitude"])
#     if raw is None:
#         return None
 
#     hourly = raw.get("hourly", {})
#     times  = hourly.get("time", [])
 
#     points = []
#     for i, t in enumerate(times):
#         def _v(key: str):
#             arr = hourly.get(key, [])
#             v = arr[i] if i < len(arr) else None
#             return float(v) if v is not None else None
 
#         points.append({
#             "time":              t,
#             "us_aqi":            _v("us_aqi"),
#             "pm2_5":             _v("pm2_5"),
#             "pm10":              _v("pm10"),
#             "nitrogen_dioxide":  _v("nitrogen_dioxide"),
#             "ozone":             _v("ozone"),
#         })
 
#     ttl = current_app.config["FORECAST_CACHE_TTL"]
#     cache.set(cache_key, points, ttl)
#     return points
 
 
# def search_stations(keyword: str) -> list[dict]:
#     """
#     Search for locations matching a keyword using Open-Meteo geocoding.
#     Returns a list of {station, lat, lon, country} dicts.
#     """
#     cache_key = f"openmeteo:search:{keyword.lower()}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
 
#     try:
#         resp = requests.get(
#             GEOCODING_URL,
#             params={"name": keyword, "count": 10, "language": "en", "format": "json"},
#             timeout=5,
#         )
#         resp.raise_for_status()
#         results = resp.json().get("results", [])
#     except requests.RequestException as exc:
#         log.error("Geocoding search failed: %s", exc)
#         return []
 
#     stations = [
#         {
#             "station": r.get("name", ""),
#             "lat":     r.get("latitude"),
#             "lon":     r.get("longitude"),
#             "country": r.get("country", ""),
#         }
#         for r in results
#     ]
 
#     cache.set(cache_key, stations, 300)
#     return stations