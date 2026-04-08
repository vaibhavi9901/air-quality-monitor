"""
routes/cities.py — Serve data stored in the database tables.

GET /api/cities/readings?city=<city>      latest air quality readings
GET /api/cities/alerts?city=<city>        recent alerts from DB
GET /api/cities/forecast?city=<city>      latest forecast from DB
GET /api/cities/seasonal?city=<city>      seasonal data from DB
GET /api/cities/risk-tiers                risk tier definitions from DB
"""

from flask import Blueprint, request
from database.models import (
    AirQualityReading, Alert, ForecastSummary, SeasonalSummary, RiskTier
)
from utils.responses import success, error

cities_bp = Blueprint("cities", __name__)


@cities_bp.get("/readings")
def get_readings():
    city  = request.args.get("city", "").strip()
    limit = min(int(request.args.get("limit", 10)), 100)
    query = AirQualityReading.query.order_by(AirQualityReading.timestamp.desc())
    if city:
        query = query.filter(AirQualityReading.city.ilike(f"%{city}%"))
    rows = query.limit(limit).all()
    return success([r.to_dict() for r in rows], message=f"{len(rows)} reading(s) found.")


@cities_bp.get("/alerts")
def get_alerts():
    city  = request.args.get("city", "").strip()
    limit = min(int(request.args.get("limit", 20)), 200)
    query = Alert.query.order_by(Alert.created_at.desc())
    if city:
        query = query.filter(Alert.city.ilike(f"%{city}%"))
    rows = query.limit(limit).all()
    return success([r.to_dict() for r in rows], message=f"{len(rows)} alert(s) found.")


@cities_bp.get("/forecast")
def get_forecast():
    city = request.args.get("city", "").strip()
    if not city:
        return error("'city' query parameter is required.")
    row = ForecastSummary.query.filter(
        ForecastSummary.city.ilike(f"%{city}%")
    ).order_by(ForecastSummary.id.desc()).first()
    if row is None:
        return error(f"No forecast found for '{city}'.", 404)
    return success(row.to_dict(include_hourly=True), message="Forecast retrieved from database.")


@cities_bp.get("/seasonal")
def get_seasonal():
    city = request.args.get("city", "").strip()
    if not city:
        return error("'city' query parameter is required.")
    row = SeasonalSummary.query.filter(
        SeasonalSummary.city.ilike(f"%{city}%")
    ).order_by(SeasonalSummary.id.desc()).first()
    if row is None:
        return error(f"No seasonal data found for '{city}'.", 404)
    return success(row.to_dict(include_months=True), message="Seasonal data retrieved from database.")


@cities_bp.get("/risk-tiers")
def get_risk_tiers():
    tiers = RiskTier.query.order_by(RiskTier.min_aqi).all()
    return success([t.to_dict() for t in tiers], message="Risk tiers from database.")


# ── State → City filtering with monitoring station validation (#7) ──────────

# Malaysian states with their major monitored cities
# Only cities with known Open-Meteo coverage are listed
MALAYSIA_STATES: dict[str, list[dict]] = {
    "Kuala Lumpur":     [{"name": "Kuala Lumpur",  "lat": 3.1390,  "lon": 101.6869}],
    "Selangor":         [{"name": "Petaling Jaya",  "lat": 3.1073,  "lon": 101.6067},
                         {"name": "Shah Alam",       "lat": 3.0853,  "lon": 101.5325},
                         {"name": "Klang",           "lat": 3.0449,  "lon": 101.4459},
                         {"name": "Subang Jaya",     "lat": 3.0565,  "lon": 101.5851},
                         {"name": "Sepang",          "lat": 2.7300,  "lon": 101.7000}],
    "Johor":            [{"name": "Johor Bahru",     "lat": 1.4927,  "lon": 103.7414},
                         {"name": "Batu Pahat",      "lat": 1.8557,  "lon": 102.9340},
                         {"name": "Muar",            "lat": 2.0442,  "lon": 102.5689}],
    "Penang":           [{"name": "George Town",     "lat": 5.4141,  "lon": 100.3288},
                         {"name": "Butterworth",     "lat": 5.3992,  "lon": 100.3639}],
    "Perak":            [{"name": "Ipoh",            "lat": 4.5975,  "lon": 101.0901},
                         {"name": "Taiping",         "lat": 4.8499,  "lon": 100.7404}],
    "Kedah":            [{"name": "Alor Setar",      "lat": 6.1184,  "lon": 100.3685},
                         {"name": "Sungai Petani",   "lat": 5.6470,  "lon": 100.4888}],
    "Kelantan":         [{"name": "Kota Bharu",      "lat": 6.1254,  "lon": 102.2381}],
    "Terengganu":       [{"name": "Kuala Terengganu","lat": 5.3296,  "lon": 103.1370}],
    "Pahang":           [{"name": "Kuantan",         "lat": 3.8077,  "lon": 103.3260}],
    "Negeri Sembilan":  [{"name": "Seremban",        "lat": 2.7297,  "lon": 101.9381}],
    "Melaka":           [{"name": "Melaka",          "lat": 2.1896,  "lon": 102.2501}],
    "Sabah":            [{"name": "Kota Kinabalu",   "lat": 5.9788,  "lon": 116.0753},
                         {"name": "Sandakan",        "lat": 5.8402,  "lon": 118.1179},
                         {"name": "Tawau",           "lat": 4.2449,  "lon": 117.8910}],
    "Sarawak":          [{"name": "Kuching",         "lat": 1.5533,  "lon": 110.3592},
                         {"name": "Miri",            "lat": 4.3995,  "lon": 113.9914},
                         {"name": "Sibu",            "lat": 2.2976,  "lon": 111.8262}],
    "Putrajaya":        [{"name": "Putrajaya",       "lat": 2.9264,  "lon": 101.6964}],
    "Labuan":           [{"name": "Labuan",          "lat": 5.2767,  "lon": 115.2417}],
    "Perlis":           [{"name": "Kangar",          "lat": 6.4414,  "lon": 100.1986}],
}


@cities_bp.get("/states")
def list_states():
    """Return all Malaysian states available for monitoring (#7)."""
    states = [
        {"state": state, "city_count": len(cities)}
        for state, cities in sorted(MALAYSIA_STATES.items())
    ]
    return success(states, message=f"{len(states)} states available.")


@cities_bp.get("/by-state/<path:state>")
def cities_by_state(state: str):
    """
    Return all monitored cities for a given state (#7).
    Each city includes has_monitoring_station: true (all listed cities have one).
    """
    # Case-insensitive match
    matched_state = next(
        (s for s in MALAYSIA_STATES if s.lower() == state.lower()), None
    )
    if matched_state is None:
        available = list(MALAYSIA_STATES.keys())
        return error(f"State '{state}' not found. Available: {available}", 404)

    cities_list = [
        {**city, "state": matched_state, "has_monitoring_station": True}
        for city in MALAYSIA_STATES[matched_state]
    ]
    return success(cities_list, message=f"{len(cities_list)} monitored cities in {matched_state}.")