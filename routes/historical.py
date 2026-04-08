"""
routes/historical.py — Historical trends and seasonal risk insights.
 
GET /api/historical/seasonal
GET /api/historical/seasonal?city=Penang&lat=5.4141&lon=100.3288&years=5
    Returns multi-year AQI data grouped by year.
 
GET /api/historical/month/<int:month>
    Detailed seasonal context for a specific month (1-12).
 
GET /api/historical/seasons
    Full seasonal context map — useful for UI dropdowns.
"""
 
from flask import Blueprint, request
import services.historical_service as historical
from utils.responses import success, error
 
historical_bp = Blueprint("historical", __name__)
 
DEFAULT_LAT   = 3.1390
DEFAULT_LON   = 101.6869
DEFAULT_YEARS = 5
 
 
@historical_bp.get("/seasonal")
def seasonal_insights():
    """
    Return multi-year seasonal risk data grouped by year (most recent first).
 
    Query params:
      city  — display label           (default: Malaysia)
      lat   — latitude                (default: 3.1390)
      lon   — longitude               (default: 101.6869)
      years — how many years to fetch (default: 3, max: 5)
 
    Example:
      GET /api/historical/seasonal?city=Penang&lat=5.4141&lon=100.3288&years=4
    """
    city = request.args.get("city", "Malaysia").strip()
    try:
        lat       = float(request.args.get("lat",   DEFAULT_LAT))
        lon       = float(request.args.get("lon",   DEFAULT_LON))
        num_years = min(int(request.args.get("years", DEFAULT_YEARS)), 5)
    except ValueError:
        return error("'lat', 'lon' must be numbers and 'years' must be an integer.")
 
    try:
        result = historical.get_seasonal_insights(city=city, lat=lat, lon=lon, num_years=num_years)
        return success(result, message="Seasonal risk insights retrieved.")
    except Exception as exc:
        return error(f"Could not load seasonal data: {exc}", 503)
 
 
@historical_bp.get("/month/<int:month>")
def month_detail(month: int):
    """Detailed seasonal context for a specific month (1–12)."""
    try:
        detail = historical.get_month_detail(month)
        return success(detail, message=f"Detail for month {month}.")
    except ValueError as exc:
        return error(str(exc))
    except Exception as exc:
        return error(f"Unexpected error: {exc}", 500)
 
 
@historical_bp.get("/seasons")
def season_list():
    """Full seasonal context map for all 12 months (no AQI values)."""
    from services.historical_service import SEASONAL_CONTEXT, MONTH_NAMES
    months = [
        {
            "month":          m,
            "month_name":     MONTH_NAMES[m - 1],
            "season":         ctx["season"],
            "driver":         ctx["driver"],
            "characteristic": ctx["characteristic"],
            "tip":            ctx["tip"],
        }
        for m, ctx in SEASONAL_CONTEXT.items()
    ]
    return success(months, message="Seasonal context for all 12 months.")

# """
# routes/historical.py — Historical trends and seasonal risk insights.

# GET /api/historical/seasonal
# GET /api/historical/seasonal?city=<city>
#     Return 12-month seasonal risk dashboard with OpenDOSM data.

# GET /api/historical/month/<int:month>
#     Return detailed context for a specific month (1-12).
# """

# from flask import Blueprint, request
# import historical_service as historical
# from responses import success, error

# historical_bp = Blueprint("historical", __name__)


# @historical_bp.get("/seasonal")
# def seasonal_insights():
#     """
#     Return the full 12-month seasonal risk dashboard.

#     Response includes:
#       - months[]   — one entry per month with api, risk_label, color,
#                      season, driver, characteristic, tip
#       - peak_month / safest_month
#       - summary    — narrative string for the dashboard header
#       - data_source — "OpenDOSM" or "Static Baseline"

#     The frontend must fully render this within 10 seconds (SLA).
#     """
#     city = request.args.get("city", "Malaysia").strip()
#     try:
#         result = historical.get_seasonal_insights(city)
#         return success(result, message="Seasonal risk insights retrieved.")
#     except Exception as exc:
#         return error(f"Could not load seasonal data: {exc}", 503)


# @historical_bp.get("/month/<int:month>")
# def month_detail(month: int):
#     """
#     Return detailed seasonal context for a specific month.
#     month — integer 1 (January) through 12 (December).
#     """
#     try:
#         detail = historical.get_month_detail(month)
#         return success(detail, message=f"Detail for month {month}.")
#     except ValueError as exc:
#         return error(str(exc))
#     except Exception as exc:
#         return error(f"Unexpected error: {exc}", 500)


# @historical_bp.get("/seasons")
# def season_list():
#     """
#     Return the full season context map (all 12 months) without API values.
#     Useful for populating dropdowns and educational content.
#     """
#     from historical_service import SEASONAL_CONTEXT, MONTH_NAMES
#     months = []
#     for m, ctx in SEASONAL_CONTEXT.items():
#         months.append({
#             "month":          m,
#             "month_name":     MONTH_NAMES[m - 1],
#             "season":         ctx["season"],
#             "driver":         ctx["driver"],
#             "characteristic": ctx["characteristic"],
#             "tip":            ctx["tip"],
#         })
#     return success(months, message="Seasonal context for all 12 months.")
