"""
services/historical_service.py — Seasonal insights with explicit failure state.

Returns {"available": false, "message": "No seasonal insights available"}
when ALL data sources fail, satisfying requirement #3.
"""

from __future__ import annotations
import logging
import requests
from datetime import date, timedelta
from typing import Optional

from flask import current_app
from utils.cache import cache

log = logging.getLogger(__name__)

HISTORICAL_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DATA_CUTOFF    = date(2026, 2, 28)
HISTORY_YEARS  = 3

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

STATIC_MONTHLY_AQI = {
    1:52,2:58,3:65,4:72,5:85,
    6:78,7:60,8:63,9:61,10:70,
    11:55,12:60,
}

SEASONAL_CONTEXT = {
    1:  {"season":"Post-Monsoon Clearance",  "driver":"Northeast monsoon winds clearing residual urban haze",       "characteristic":"Transitional — improving air quality",            "tip":"Good time to resume outdoor exercise routines."},
    2:  {"season":"Dry Inter-Monsoon",        "driver":"Low wind, urban exhaust accumulation",                      "characteristic":"Moderate urban pollution, stagnant air",           "tip":"Avoid high-traffic roads during peak hours (7–9 am, 5–7 pm)."},
    3:  {"season":"Pre-Haze Season",          "driver":"Start of land-clearing burns in Sumatra & Borneo",         "characteristic":"Rising PM2.5, early transboundary haze",           "tip":"Monitor daily API readings; prepare N95 masks at home."},
    4:  {"season":"Haze Season (Early)",      "driver":"Regional agricultural burning (Sumatra, Kalimantan)",      "characteristic":"Transboundary haze episodes",                      "tip":"Use air purifiers indoors; limit morning outdoor walks."},
    5:  {"season":"Haze Season (Peak)",       "driver":"Peak biomass burning + hot, dry conditions",               "characteristic":"Highest annual PM2.5 concentrations",              "tip":"Use air purifiers; keep windows closed; wear N95 outdoors."},
    6:  {"season":"Haze Season (Late)",       "driver":"Residual burning + urban construction dust",               "characteristic":"Persistently elevated pollution",                   "tip":"Stay indoors during hazy afternoons; hydrate well."},
    7:  {"season":"Southwest Monsoon",        "driver":"Monsoon rains washing out pollutants, brief respite",      "characteristic":"Improved air quality between rain spells",          "tip":"Take advantage of post-rain windows for outdoor activity."},
    8:  {"season":"Monsoon Stagnation",       "driver":"Urban exhaust trapped by low inversion layer",             "characteristic":"Localised urban smog pockets",                     "tip":"Avoid high-traffic roads; use public transport where possible."},
    9:  {"season":"Inter-Monsoon",            "driver":"Thunderstorm activity, erratic wind patterns",             "characteristic":"Variable — sudden spikes possible",                "tip":"Check API before outdoor plans; carry a mask as precaution."},
    10: {"season":"Festive Haze (Deepavali)", "driver":"Fireworks + incense burning during festive season",        "characteristic":"Short-lived but intense PM2.5 spikes",             "tip":"Close windows during celebrations; run air purifiers."},
    11: {"season":"Northeast Monsoon Onset",  "driver":"Heavy rainfall bringing cleaner air",                      "characteristic":"Improving conditions; flood-related dust possible", "tip":"Good air quality overall; watch for post-flood mold spores."},
    12: {"season":"Year-End Festive Season",  "driver":"Christmas / New Year fireworks + increased traffic",       "characteristic":"Moderate festive spikes",                          "tip":"Close windows on New Year's Eve; air out home the next morning."},
}

KL_LAT, KL_LON = 3.1390, 101.6869


def _unavailable_response(city: str) -> dict:
    """Standard failure response for requirement #3."""
    return {
        "available": False,
        "message":   "No seasonal insights available",
        "city":      city,
        "months":    [],
    }


def _effective_today():
    return min(date.today(), DATA_CUTOFF)


def _aqi_to_risk(aqi):
    if aqi <= 50:  return "#22c55e", "Good"
    if aqi <= 100: return "#eab308", "Moderate"
    if aqi <= 150: return "#f97316", "Unhealthy for Sensitive Groups"
    if aqi <= 200: return "#ef4444", "Unhealthy"
    if aqi <= 300: return "#7c3aed", "Very Unhealthy"
    return "#991b1b", "Hazardous"


def _read_from_db(city: str) -> Optional[dict]:
    try:
        from database.models import SeasonalSummary
        row = SeasonalSummary.query.filter(
            SeasonalSummary.city.ilike(f"%{city}%")
        ).order_by(SeasonalSummary.id.desc()).first()
        if row is None:
            return None
        months_data = row.to_dict(include_months=True)["months"]
        if not months_data:
            return None
        month_aqi = {m["month"]: m["aqi"] for m in months_data if m["aqi"] is not None}
        return {
            "city":         row.city,
            "peak_month":   row.peak_month,
            "safest_month": row.safest_month,
            "months":       months_data,
            "month_aqi":    month_aqi,
        }
    except Exception as exc:
        log.warning("DB seasonal read failed: %s", exc)
        return None


def _fetch_live_month(lat, lon, year, month) -> Optional[float]:
    effective_today = _effective_today()
    start = date(year, month, 1)
    end   = (date(year, month+1, 1) if month < 12 else date(year+1,1,1)) - timedelta(days=1)
    if start > effective_today: return None
    if end   > effective_today: end = effective_today

    cache_key = f"hist:live:{lat:.3f}:{lon:.3f}:{year}:{month:02d}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(HISTORICAL_URL, params={
            "latitude": lat, "longitude": lon, "hourly": "us_aqi",
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "timezone": "Asia/Kuala_Lumpur",
        }, timeout=10)
        resp.raise_for_status()
        aqi_arr = [v for v in resp.json().get("hourly",{}).get("us_aqi",[]) if v is not None]
        if not aqi_arr: return None
        avg = round(sum(aqi_arr)/len(aqi_arr), 1)
        cache.set(cache_key, avg, 86400)
        return avg
    except Exception as exc:
        log.warning("Live seasonal fetch failed (%d-%02d): %s", year, month, exc)
        return None


def get_seasonal_insights(
    city: str   = "Malaysia",
    lat:  float = KL_LAT,
    lon:  float = KL_LON,
    num_years: int = HISTORY_YEARS,
) -> dict:
    cache_key = f"historical:seasonal:{city.lower().replace(' ','_')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # ── 1. Try DB ──
    db_data = _read_from_db(city)

    if db_data:
        months = db_data["months"]
        for m in months:
            month_num = m.get("month")
            if month_num and month_num in SEASONAL_CONTEXT:
                ctx = SEASONAL_CONTEXT[month_num]
                m.setdefault("season",         ctx["season"])
                m.setdefault("driver",         ctx["driver"])
                m.setdefault("characteristic", ctx["characteristic"])
                m.setdefault("tip",            ctx["tip"])
        month_aqi   = db_data["month_aqi"]
        data_source = "Database"

    else:
        # ── 2. Try live API ──
        log.info("'%s' not in DB — trying live API.", city)
        today      = _effective_today()
        start_year = today.year - num_years + 1
        month_aqi  = {}

        for year in range(today.year, start_year - 1, -1):
            for month in range(1, 13):
                if date(year, month, 1) > today: continue
                avg = _fetch_live_month(lat, lon, year, month)
                if avg is not None:
                    month_aqi[month] = avg

        # ── 3. If live API also failed completely → return unavailable (#3) ──
        if not month_aqi:
            log.error("All data sources failed for '%s' — returning unavailable.", city)
            result = _unavailable_response(city)
            cache.set(cache_key, result, 300)   # cache the failure briefly
            return result

        # Fill remaining months with static baseline
        for m in range(1, 13):
            if m not in month_aqi:
                month_aqi[m] = STATIC_MONTHLY_AQI[m]

        months = []
        for m in range(1, 13):
            aqi_val = month_aqi[m]
            color, risk_label = _aqi_to_risk(aqi_val)
            ctx = SEASONAL_CONTEXT[m]
            months.append({
                "month": m, "month_name": MONTH_NAMES[m-1],
                "aqi": aqi_val, "risk_label": risk_label, "color": color, **ctx,
            })
        data_source = "Live API (Open-Meteo)"

    valid   = [m for m in months if m.get("aqi") is not None]
    if not valid:
        result = _unavailable_response(city)
        cache.set(cache_key, result, 300)
        return result

    peak   = max(valid, key=lambda x: x["aqi"])
    safest = min(valid, key=lambda x: x["aqi"])

    result = {
        "available":    True,
        "city":         city,
        "months":       months,
        "peak_month":   peak["month_name"],
        "peak_aqi":     peak["aqi"],
        "peak_season":  peak.get("season",""),
        "safest_month": safest["month_name"],
        "safest_aqi":   safest["aqi"],
        "data_source":  data_source,
        "summary": (
            f"Air quality peaks in {peak['month_name']} "
            f"({peak.get('season','')}, AQI {peak['aqi']:.0f}). "
            f"Best in {safest['month_name']} (AQI {safest['aqi']:.0f})."
        ),
    }

    ttl = current_app.config["HISTORICAL_CACHE_TTL"]
    cache.set(cache_key, result, ttl)
    return result


def get_month_detail(month: int) -> dict:
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")
    ctx               = SEASONAL_CONTEXT[month]
    aqi_val           = STATIC_MONTHLY_AQI[month]
    color, risk_label = _aqi_to_risk(aqi_val)
    return {
        "month": month, "month_name": MONTH_NAMES[month-1],
        "aqi": aqi_val, "risk_label": risk_label, "color": color, **ctx,
    }

# """
# services/historical_service.py — Seasonal risk insights from OpenDOSM.

# Data source: https://open.dosm.gov.my/
# Dataset: Monthly air pollution statistics for Malaysia.

# The service:
# 1. Fetches or uses cached OpenDOSM data (12 months).
# 2. Enriches each month with a seasonal context label derived from the
#    Malaysian meteorological / cultural calendar.
# 3. Attaches actionable protection tips.
# 4. Falls back to embedded static data if the API is unreachable.
# """

# from __future__ import annotations
# import logging
# import requests
# from typing import Any

# from flask import current_app
# from cache import cache

# log = logging.getLogger(__name__)


# # ── Malaysian seasonal context map ───────────────────────────────────────────
# # month_number → {season, driver, tip, risk_modifier}

# SEASONAL_CONTEXT: dict[int, dict] = {
#     1:  {
#         "season":   "Post-Monsoon Clearance",
#         "driver":   "Northeast monsoon winds clearing residual urban haze",
#         "characteristic": "Transitional — improving air quality",
#         "tip":      "Good time to resume outdoor exercise routines.",
#         "risk_modifier": -0.05,
#     },
#     2:  {
#         "season":   "Dry Inter-Monsoon",
#         "driver":   "Low wind, urban exhaust accumulation",
#         "characteristic": "Moderate urban pollution, stagnant air",
#         "tip":      "Avoid high-traffic roads during peak hours (7–9 am, 5–7 pm).",
#         "risk_modifier": 0.05,
#     },
#     3:  {
#         "season":   "Pre-Haze Season",
#         "driver":   "Start of land-clearing burns in Sumatra & Borneo",
#         "characteristic": "Rising PM2.5, early transboundary haze",
#         "tip":      "Monitor daily API readings; prepare N95 masks at home.",
#         "risk_modifier": 0.10,
#     },
#     4:  {
#         "season":   "Haze Season (Early)",
#         "driver":   "Regional agricultural burning (Sumatra, Kalimantan)",
#         "characteristic": "Transboundary haze episodes",
#         "tip":      "Use air purifiers indoors; limit morning outdoor walks.",
#         "risk_modifier": 0.20,
#     },
#     5:  {
#         "season":   "Haze Season (Peak)",
#         "driver":   "Peak biomass burning + hot, dry conditions",
#         "characteristic": "Highest annual PM2.5 concentrations",
#         "tip":      "Use air purifiers; keep windows closed; wear N95 outdoors.",
#         "risk_modifier": 0.30,
#     },
#     6:  {
#         "season":   "Haze Season (Late)",
#         "driver":   "Residual burning + urban construction dust",
#         "characteristic": "Persistently elevated pollution",
#         "tip":      "Stay indoors during hazy afternoons; hydrate well.",
#         "risk_modifier": 0.20,
#     },
#     7:  {
#         "season":   "Southwest Monsoon",
#         "driver":   "Monsoon rains washing out pollutants, brief respite",
#         "characteristic": "Improved air quality between rain spells",
#         "tip":      "Take advantage of post-rain windows for outdoor activity.",
#         "risk_modifier": -0.10,
#     },
#     8:  {
#         "season":   "Monsoon Stagnation",
#         "driver":   "Urban exhaust trapped by low inversion layer",
#         "characteristic": "Localised urban smog pockets",
#         "tip":      "Avoid high-traffic roads; use public transport where possible.",
#         "risk_modifier": 0.05,
#     },
#     9:  {
#         "season":   "Inter-Monsoon",
#         "driver":   "Thunderstorm activity, erratic wind patterns",
#         "characteristic": "Variable — sudden spikes possible",
#         "tip":      "Check API before outdoor plans; carry a mask as precaution.",
#         "risk_modifier": 0.00,
#     },
#     10: {
#         "season":   "Festive Haze (Deepavali)",
#         "driver":   "Fireworks + incense burning during festive season",
#         "characteristic": "Short-lived but intense PM2.5 spikes",
#         "tip":      "Close windows during celebrations; run air purifiers.",
#         "risk_modifier": 0.15,
#     },
#     11: {
#         "season":   "Northeast Monsoon Onset",
#         "driver":   "Heavy rainfall bringing cleaner air",
#         "characteristic": "Improving conditions; flood-related dust possible",
#         "tip":      "Good air quality overall; watch for post-flood mold spores.",
#         "risk_modifier": -0.10,
#     },
#     12: {
#         "season":   "Year-End Festive Season",
#         "driver":   "Christmas / New Year fireworks + increased traffic",
#         "characteristic": "Moderate festive spikes",
#         "tip":      "Close windows on New Year's Eve; air out home the next morning.",
#         "risk_modifier": 0.10,
#     },
# }

# MONTH_NAMES = [
#     "Jan", "Feb", "Mar", "Apr", "May", "Jun",
#     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
# ]

# # Static fallback: Malaysia monthly average API (approximate, 2019-2023 avg)
# STATIC_MONTHLY_API: dict[int, float] = {
#     1: 52, 2: 58, 3: 65, 4: 72, 5: 85,
#     6: 78, 7: 60, 8: 63, 9: 61, 10: 70,
#     11: 55, 12: 60,
# }


# # ── OpenDOSM fetch ────────────────────────────────────────────────────────────

# def _fetch_opendosm() -> list[dict[str, Any]]:
#     """
#     Attempt to pull the latest 12-month dataset from OpenDOSM.
#     Returns a list of {month, year, api_value} dicts or [] on failure.
#     """
#     base    = current_app.config["OPENDOSM_BASE_URL"]
#     dataset = current_app.config["OPENDOSM_AIR_DATASET"]
#     url     = f"{base}?id={dataset}&limit=12&sort=-date"

#     try:
#         resp = requests.get(url, timeout=8)
#         resp.raise_for_status()
#         rows = resp.json()
#         parsed = []
#         for row in rows:
#             date_str = row.get("date", "")       # e.g. "2024-05"
#             api_val  = row.get("api", None) or row.get("value", None)
#             if date_str and api_val is not None:
#                 year, month = int(date_str[:4]), int(date_str[5:7])
#                 parsed.append({"month": month, "year": year, "api": float(api_val)})
#         return parsed
#     except Exception as exc:
#         log.warning("OpenDOSM fetch failed, using static data: %s", exc)
#         return []


# def _build_static_records() -> list[dict[str, Any]]:
#     """Return static monthly records when OpenDOSM is unavailable."""
#     from datetime import datetime
#     current_year = datetime.now().year
#     records = []
#     for month in range(1, 13):
#         records.append({
#             "month": month,
#             "year":  current_year - 1 if month > datetime.now().month else current_year,
#             "api":   STATIC_MONTHLY_API[month],
#         })
#     return records


# # ── Public API ────────────────────────────────────────────────────────────────

# def get_seasonal_insights(city: str = "Malaysia") -> dict:
#     """
#     Return a 12-month seasonal risk dashboard with:
#     - Historical API values per month
#     - Seasonal context label
#     - Characteristic pollution driver
#     - Actionable protection tip
#     - Risk level colour
#     """
#     cache_key = f"historical:seasonal:{city.lower().replace(' ', '_')}"
#     cached = cache.get(cache_key)
#     if cached:
#         return cached

#     # Fetch real data or fall back to static
#     records = _fetch_opendosm()
#     if not records:
#         records = _build_static_records()

#     # Build a month → api lookup
#     month_api: dict[int, float] = {}
#     for rec in records:
#         month_api[rec["month"]] = rec["api"]

#     # Compose insight rows
#     monthly_insights = []
#     for m in range(1, 13):
#         api_val  = month_api.get(m, STATIC_MONTHLY_API[m])
#         ctx      = SEASONAL_CONTEXT[m]

#         # Determine colour band
#         if api_val <= 50:
#             color, risk_label = "#22c55e", "Good"
#         elif api_val <= 100:
#             color, risk_label = "#eab308", "Moderate"
#         elif api_val <= 200:
#             color, risk_label = "#f97316", "Unhealthy"
#         else:
#             color, risk_label = "#ef4444", "Very Unhealthy"

#         monthly_insights.append({
#             "month":          m,
#             "month_name":     MONTH_NAMES[m - 1],
#             "year":           records[0]["year"] if records else 2024,
#             "api":            round(api_val, 1),
#             "risk_label":     risk_label,
#             "color":          color,
#             "season":         ctx["season"],
#             "driver":         ctx["driver"],
#             "characteristic": ctx["characteristic"],
#             "tip":            ctx["tip"],
#         })

#     # Identify the highest-risk month
#     peak = max(monthly_insights, key=lambda x: x["api"])
#     safest = min(monthly_insights, key=lambda x: x["api"])

#     result = {
#         "city":             city,
#         "months":           monthly_insights,
#         "peak_month":       peak["month_name"],
#         "peak_api":         peak["api"],
#         "peak_season":      peak["season"],
#         "safest_month":     safest["month_name"],
#         "safest_api":       safest["api"],
#         "data_source":      "OpenDOSM" if len(month_api) > 0 else "Static Baseline",
#         "summary": (
#             f"Air quality peaks in {peak['month_name']} "
#             f"({peak['season']}, API {peak['api']:.0f}). "
#             f"Best conditions are in {safest['month_name']}. "
#             f"Key hazard: {peak['driver']}."
#         ),
#     }

#     ttl = current_app.config["HISTORICAL_CACHE_TTL"]
#     cache.set(cache_key, result, ttl)
#     return result


# def get_month_detail(month: int) -> dict:
#     """Return detailed context for a specific month (1-12)."""
#     if not 1 <= month <= 12:
#         raise ValueError("Month must be between 1 and 12")

#     ctx     = SEASONAL_CONTEXT[month]
#     api_val = STATIC_MONTHLY_API[month]

#     return {
#         "month":          month,
#         "month_name":     MONTH_NAMES[month - 1],
#         "api":            api_val,
#         "season":         ctx["season"],
#         "driver":         ctx["driver"],
#         "characteristic": ctx["characteristic"],
#         "tip":            ctx["tip"],
#     }
