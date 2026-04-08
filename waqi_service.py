# """
# services/waqi_service.py — Real-time air quality data via WAQI API.

# Docs: https://aqicn.org/json-api/doc/
# Free token gives ~1 000 req/day; enough for real-world usage with caching.
# """

# from __future__ import annotations
# import requests
# import logging
# from datetime import datetime, timezone
# from typing import Optional

# from flask import current_app
# from aqi import AirQualityReading, Pollutants
# from cache import cache

# log = logging.getLogger(__name__)


# def _token() -> str:
#     return current_app.config["WAQI_API_TOKEN"]


# def _base() -> str:
#     return current_app.config["WAQI_BASE_URL"]


# def _extract_pollutants(iaqi: dict) -> Pollutants:
#     """Parse the WAQI 'iaqi' block into a Pollutants object."""
#     def _val(key: str) -> Optional[float]:
#         block = iaqi.get(key)
#         return float(block["v"]) if block else None

#     return Pollutants(
#         pm25=_val("pm25"),
#         pm10=_val("pm10"),
#         o3=_val("o3"),
#         no2=_val("no2"),
#         so2=_val("so2"),
#         co=_val("co"),
#     )


# def _parse_reading(data: dict) -> AirQualityReading:
#     """Convert a WAQI station 'data' dict into an AirQualityReading."""
#     aqi_raw = data.get("aqi", 0)
#     # WAQI sometimes returns "-" for unavailable stations
#     aqi = float(aqi_raw) if str(aqi_raw).lstrip("-").isdigit() else 0.0

#     city_block = data.get("city", {})
#     city_name   = city_block.get("name", "Unknown")
#     geo         = city_block.get("geo", [0.0, 0.0])
#     lat, lon    = float(geo[0]), float(geo[1])

#     # Derive country from city name (WAQI embeds it) or station attribution
#     country = "MY"  # default Malaysia; override with geocoding if needed

#     # Timestamp
#     time_block = data.get("time", {})
#     ts_str = time_block.get("iso", datetime.now(timezone.utc).isoformat())

#     iaqi        = data.get("iaqi", {})
#     pollutants  = _extract_pollutants(iaqi)
#     dominant    = data.get("dominentpol", "pm25")

#     return AirQualityReading(
#         aqi=aqi,
#         station=city_name,
#         city=city_name.split(",")[0].strip(),
#         country=country,
#         latitude=lat,
#         longitude=lon,
#         timestamp=ts_str,
#         pollutants=pollutants,
#         dominant_pollutant=dominant,
#     )


# # ── Public functions ─────────────────────────────────────────────────────────

# def get_by_city(city: str) -> Optional[AirQualityReading]:
#     """
#     Fetch the nearest WAQI station for *city*.
#     Results are cached for REALTIME_CACHE_TTL seconds.
#     """
#     cache_key = f"waqi:city:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         log.debug("Cache hit: %s", cache_key)
#         return cached

#     url = f"{_base()}/feed/{requests.utils.quote(city)}/"
#     params = {"token": _token()}

#     try:
#         resp = requests.get(url, params=params, timeout=5)
#         resp.raise_for_status()
#         body = resp.json()
#     except requests.RequestException as exc:
#         log.error("WAQI city request failed: %s", exc)
#         return None

#     if body.get("status") != "ok":
#         log.warning("WAQI returned non-ok status for %s: %s", city, body)
#         return None

#     reading = _parse_reading(body["data"])
#     ttl = current_app.config["REALTIME_CACHE_TTL"]
#     cache.set(cache_key, reading, ttl)
#     return reading


# def get_by_coordinates(lat: float, lon: float) -> Optional[AirQualityReading]:
#     """
#     Fetch the nearest WAQI station to the given GPS coordinates.
#     """
#     cache_key = f"waqi:geo:{lat:.3f}:{lon:.3f}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached

#     url = f"{_base()}/feed/geo:{lat};{lon}/"
#     params = {"token": _token()}

#     try:
#         resp = requests.get(url, params=params, timeout=5)
#         resp.raise_for_status()
#         body = resp.json()
#     except requests.RequestException as exc:
#         log.error("WAQI geo request failed: %s", exc)
#         return None

#     if body.get("status") != "ok":
#         log.warning("WAQI returned non-ok for geo (%s,%s): %s", lat, lon, body)
#         return None

#     reading = _parse_reading(body["data"])
#     ttl = current_app.config["REALTIME_CACHE_TTL"]
#     cache.set(cache_key, reading, ttl)
#     return reading


# def search_stations(keyword: str) -> list[dict]:
#     """
#     Search WAQI for stations matching a keyword.
#     Returns a list of {uid, station, aqi, lat, lon} dicts.
#     """
#     cache_key = f"waqi:search:{keyword.lower()}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached

#     url = f"{_base()}/search/"
#     params = {"token": _token(), "keyword": keyword}

#     try:
#         resp = requests.get(url, params=params, timeout=5)
#         resp.raise_for_status()
#         body = resp.json()
#     except requests.RequestException as exc:
#         log.error("WAQI search failed: %s", exc)
#         return []

#     if body.get("status") != "ok":
#         return []

#     stations = []
#     for item in body.get("data", []):
#         stations.append({
#             "uid":     item.get("uid"),
#             "station": item.get("station", {}).get("name", ""),
#             "aqi":     item.get("aqi"),
#             "lat":     item.get("station", {}).get("geo", [0, 0])[0],
#             "lon":     item.get("station", {}).get("geo", [0, 0])[1],
#         })

#     cache.set(cache_key, stations, 300)
#     return stations
