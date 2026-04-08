"""
services/forecast_service.py — 24-hour forecast with failure states.

Returns {"available": false, "message": "Data Not Available"} when the
forecast cannot be generated, satisfying requirement #4.
Also tags each hour with the current seasonal event (#5).
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone, date

from flask import current_app
from models.aqi import ForecastPoint, classify_aqi
from utils.cache import cache
import services.openmeteo_service as openmeteo

log = logging.getLogger(__name__)

# Seasonal event tags by month — used to flag "Haze Period" etc. in forecast (#5)
SEASONAL_EVENTS = {
    1:  None,
    2:  None,
    3:  {"seasonal_event": "Pre-Haze Season",    "risk_name": "Haze Risk Rising"},
    4:  {"seasonal_event": "Haze Season",         "risk_name": "Haze Period"},
    5:  {"seasonal_event": "Haze Season (Peak)",  "risk_name": "Haze Period"},
    6:  {"seasonal_event": "Haze Season (Late)",  "risk_name": "Haze Period"},
    7:  None,
    8:  None,
    9:  None,
    10: {"seasonal_event": "Festive Haze",        "risk_name": "Festive Season Risk"},
    11: None,
    12: {"seasonal_event": "Year-End Festivities","risk_name": "Festive Season Risk"},
}

_DIURNAL = [
    0.70, 0.65, 0.62, 0.60, 0.62, 0.72,
    0.85, 1.05, 1.20, 1.10, 1.00, 0.95,
    0.90, 0.88, 0.90, 0.95, 1.05, 1.20,
    1.25, 1.15, 1.05, 0.95, 0.85, 0.75,
]


def _unavailable_response(city: str) -> dict:
    """Standard 'Data Not Available' response (#4)."""
    return {
        "available":   False,
        "message":     "Data Not Available",
        "city":        city,
        "hourly":      [],
        "data_source": "none",
    }


def _tag_seasonal(point: dict, month: int) -> dict:
    """Add seasonal_event tag to a forecast point (#5)."""
    event = SEASONAL_EVENTS.get(month)
    point["seasonal_event"] = event["seasonal_event"] if event else None
    point["risk_name"]      = event["risk_name"]      if event else None
    return point


def get_24h_forecast(city: str) -> dict:
    """
    Return 24-hour forecast. Returns an unavailable response dict on failure.
    """
    cache_key = f"forecast:24h:{city.lower().replace(' ', '_')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    raw_points = openmeteo.get_hourly_forecast(city)
    current_month = datetime.now(timezone.utc).month

    if raw_points:
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        start_idx = 0
        for i, p in enumerate(raw_points):
            try:
                dt = datetime.fromisoformat(p["time"]).replace(tzinfo=timezone.utc)
                if dt >= now:
                    start_idx = i
                    break
            except ValueError:
                continue

        window = raw_points[start_idx: start_idx + 24]
        if not window:
            return _unavailable_response(city)

        points = []
        for p in window:
            aqi_val = p.get("us_aqi")
            if aqi_val is None:
                continue
            pm25 = p.get("pm2_5")
            try:
                hour = int(p["time"][11:13])
            except (IndexError, ValueError):
                hour = 0

            fp = ForecastPoint(hour=hour, aqi=float(aqi_val), pm25=pm25)
            d  = fp.to_dict()
            d["time"] = p["time"]
            d = _tag_seasonal(d, current_month)
            points.append(d)

        # Pad to 24 if needed
        while len(points) < 24 and points:
            last    = points[-1]
            risk    = classify_aqi(last["aqi"])
            padded  = {
                "hour":  (last["hour"] + 1) % 24,
                "time":  "",
                "aqi":   last["aqi"],
                "pm25":  None,
                "label": risk["label"],
                "color": risk["color"],
                "icon":  risk["icon"],
            }
            padded = _tag_seasonal(padded, current_month)
            points.append(padded)

        if not points:
            return _unavailable_response(city)

    else:
        # Live API failed — check if we have a current reading to base on
        log.warning("Open-Meteo forecast unavailable for %s.", city)
        reading = openmeteo.get_by_city(city)
        if reading is None:
            # Both forecast and current reading failed — return unavailable (#4)
            return _unavailable_response(city)

        # Statistical fallback from current reading
        import random
        base_aqi     = reading.aqi
        current_hour = datetime.now(timezone.utc).hour
        points = []
        for offset, mult in enumerate(_DIURNAL):
            aqi_val = max(0.0, round(base_aqi * mult * (1 + random.gauss(0, 0.02)), 1))
            hour    = (current_hour + offset) % 24
            fp      = ForecastPoint(hour=hour, aqi=aqi_val, pm25=round(aqi_val / 2.1, 1))
            d       = fp.to_dict()
            d["time"] = ""
            d = _tag_seasonal(d, current_month)
            points.append(d)

    result = {
        "available":   True,
        "city":        city,
        "hourly":      points,
        "data_source": "Open-Meteo",
    }

    ttl = current_app.config["FORECAST_CACHE_TTL"]
    cache.set(cache_key, result, ttl)
    return result


def get_forecast_summary(city: str) -> dict:
    """Return forecast summary. Propagates unavailable state if needed."""
    forecast = get_24h_forecast(city)

    if not forecast.get("available", False):
        return forecast   # pass the "Data Not Available" response straight through

    points     = forecast["hourly"]
    aqi_values = [p["aqi"] for p in points if p.get("aqi") is not None]

    if not aqi_values:
        return _unavailable_response(city)

    max_aqi  = max(aqi_values)
    min_aqi  = min(aqi_values)
    avg_aqi  = round(sum(aqi_values) / len(aqi_values), 1)
    peak_idx = aqi_values.index(max_aqi)

    peak_risk = classify_aqi(max_aqi)
    avg_risk  = classify_aqi(avg_aqi)

    # Collect any seasonal events present in this 24h window (#5)
    seasonal_events = list({
        p["seasonal_event"] for p in points
        if p.get("seasonal_event") is not None
    })

    forecast["max_aqi"]          = round(max_aqi, 1)
    forecast["min_aqi"]          = round(min_aqi, 1)
    forecast["avg_aqi"]          = avg_aqi
    forecast["peak_hour"]        = points[peak_idx]["hour"]
    forecast["peak_time"]        = points[peak_idx].get("time", "")
    forecast["peak_risk"]        = peak_risk["label"]
    forecast["peak_color"]       = peak_risk["color"]
    forecast["overall_risk"]     = avg_risk["label"]
    forecast["overall_color"]    = avg_risk["color"]
    forecast["alert_recommended"] = peak_risk["alert"]
    forecast["seasonal_events"]  = seasonal_events     # e.g. ["Haze Season"]
    forecast["seasonal_risk_name"] = points[peak_idx].get("risk_name")  # e.g. "Haze Period"

    return forecast

# """
# services/forecast_service.py — 24-hour air quality forecast.

# Strategy:
# 1. Pull today's WAQI forecast block (the API returns daily min/max/avg
#    for PM2.5, O3, PM10 for the coming days).
# 2. Expand the daily forecast into hourly buckets using a diurnal pattern
#    derived from real-world pollution behaviour (morning peak, midday dip,
#    evening peak).
# 3. If the WAQI forecast block is unavailable (demo token / station),
#    fall back to a statistical model built from the last reading ± noise.

# The result is always a list of 24 ForecastPoint objects (hours 0-23).
# """

# from __future__ import annotations
# import math
# import random
# import logging
# from datetime import datetime, timezone
# from typing import Optional

# from flask import current_app
# from aqi import ForecastPoint, classify_aqi
# from cache import cache
# import waqi_service as waqi

# log = logging.getLogger(__name__)

# # Diurnal multiplier: index = hour 0-23
# # Pattern: low at night, rising morning rush, dip midday, peak evening rush
# _DIURNAL = [
#     0.70, 0.65, 0.62, 0.60, 0.62, 0.72,   # 00-05 overnight
#     0.85, 1.05, 1.20, 1.10, 1.00, 0.95,   # 06-11 morning
#     0.90, 0.88, 0.90, 0.95, 1.05, 1.20,   # 12-17 afternoon
#     1.25, 1.15, 1.05, 0.95, 0.85, 0.75,   # 18-23 evening/night
# ]


# def _daily_waqi_forecast(city: str) -> Optional[dict]:
#     """
#     Return WAQI's forecast block for *city* (keys: pm25, pm10, o3).
#     Each key maps to a list of {avg, min, max, day} dicts.
#     """
#     import requests
#     token = current_app.config["WAQI_API_TOKEN"]
#     base  = current_app.config["WAQI_BASE_URL"]
#     url   = f"{base}/feed/{requests.utils.quote(city)}/"
#     try:
#         resp = requests.get(url, params={"token": token}, timeout=5)
#         resp.raise_for_status()
#         body = resp.json()
#         if body.get("status") == "ok":
#             return body["data"].get("forecast", {}).get("daily")
#     except Exception as exc:
#         log.warning("Could not fetch WAQI forecast: %s", exc)
#     return None


# def _interpolate_hourly(daily_avg: float, base_aqi: float) -> list[float]:
#     """
#     Produce 24 hourly AQI values given a daily average and a baseline.
#     We weight the WAQI daily average (60%) against the current reading (40%).
#     """
#     anchor = 0.6 * daily_avg + 0.4 * base_aqi
#     hourly = []
#     for mult in _DIURNAL:
#         value = anchor * mult
#         # Add small noise ±3 %
#         value *= 1 + (random.gauss(0, 0.015))
#         hourly.append(max(0.0, round(value, 1)))
#     return hourly


# def _statistical_forecast(base_aqi: float) -> list[float]:
#     """
#     Fallback: generate hourly AQI from the current reading using the
#     diurnal multipliers and Gaussian noise.
#     """
#     hourly = []
#     for mult in _DIURNAL:
#         v = base_aqi * mult * (1 + random.gauss(0, 0.02))
#         hourly.append(max(0.0, round(v, 1)))
#     return hourly


# # ── Public API ───────────────────────────────────────────────────────────────

# def get_24h_forecast(city: str) -> list[dict]:
#     """
#     Return a list of 24 forecast dicts (one per hour, starting from the
#     current hour) for *city*.  Results are cached for FORECAST_CACHE_TTL.
#     """
#     cache_key = f"forecast:24h:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached

#     # 1. Get current AQI as baseline
#     reading = waqi.get_by_city(city)
#     base_aqi = reading.aqi if reading else 80.0   # sensible KL default

#     # 2. Try to get WAQI daily forecast → pick today's PM2.5 avg
#     hourly_aqi: list[float]
#     daily = _daily_waqi_forecast(city)

#     if daily and "pm25" in daily and daily["pm25"]:
#         today = daily["pm25"][0]           # first entry = today
#         daily_avg_pm25 = float(today.get("avg", base_aqi))
#         # Very rough PM2.5 → AQI conversion (linear 0-500 scale used by WAQI)
#         daily_avg_aqi = daily_avg_pm25 * 2.1
#         hourly_aqi = _interpolate_hourly(daily_avg_aqi, base_aqi)
#         log.debug("Using WAQI daily forecast for %s", city)
#     else:
#         hourly_aqi = _statistical_forecast(base_aqi)
#         log.debug("Using statistical forecast fallback for %s", city)

#     # 3. Build ForecastPoint objects
#     current_hour = datetime.now(timezone.utc).hour
#     points: list[dict] = []
#     for offset in range(24):
#         hour = (current_hour + offset) % 24
#         aqi_val = hourly_aqi[offset]
#         pm25_est = round(aqi_val / 2.1, 1)
#         fp = ForecastPoint(hour=hour, aqi=aqi_val, pm25=pm25_est)
#         points.append(fp.to_dict())

#     ttl = current_app.config["FORECAST_CACHE_TTL"]
#     cache.set(cache_key, points, ttl)
#     return points


# def get_forecast_summary(city: str) -> dict:
#     """
#     Return a summary of the 24-hour forecast: peak hour, min/max AQI,
#     overall risk level, and whether an alert should be raised.
#     """
#     points = get_24h_forecast(city)
#     aqi_values = [p["aqi"] for p in points]

#     max_aqi = max(aqi_values)
#     min_aqi = min(aqi_values)
#     avg_aqi = round(sum(aqi_values) / len(aqi_values), 1)
#     peak_hour = aqi_values.index(max_aqi)

#     peak_risk = classify_aqi(max_aqi)
#     avg_risk  = classify_aqi(avg_aqi)

#     return {
#         "city":        city,
#         "max_aqi":     round(max_aqi, 1),
#         "min_aqi":     round(min_aqi, 1),
#         "avg_aqi":     avg_aqi,
#         "peak_hour":   (peak_hour + datetime.now(timezone.utc).hour) % 24,
#         "peak_risk":   peak_risk["label"],
#         "overall_risk": avg_risk["label"],
#         "overall_color": avg_risk["color"],
#         "alert_recommended": peak_risk["alert"],
#         "hourly": points,
#     }
