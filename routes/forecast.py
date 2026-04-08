"""
routes/forecast.py — 24-hour air quality forecast endpoints.

GET /api/forecast/<city>
    Return 24 hourly AQI forecast points for *city*.

GET /api/forecast/<city>/summary
    Return a condensed forecast summary (min/max/peak hour/alert).
"""

from flask import Blueprint
import services.forecast_service as forecast
from utils.responses import success, error

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.get("/<path:city>")
def hourly_forecast(city: str):
    """
    Return 24 hourly AQI forecast points, starting from the current hour.
    Each point includes: hour, aqi, pm25, label, color, icon.

    The frontend can render these as a bar / line chart with colour bands:
      Green  (#22c55e) — Good (AQI 0-50)
      Yellow (#eab308) — Moderate (AQI 51-100)
      Orange (#f97316) — Unhealthy (AQI 101-200)
      Red    (#ef4444) — Very Unhealthy (AQI 201-300)
      Purple (#7c3aed) — Hazardous (AQI 301+)
    """
    try:
        points = forecast.get_24h_forecast(city)
        return success(
            {"city": city, "hourly": points},
            message=f"24-hour forecast for {city} retrieved."
        )
    except Exception as exc:
        return error(f"Forecast unavailable: {exc}", 503)


@forecast_bp.get("/<path:city>/summary")
def forecast_summary(city: str):
    """
    Return a condensed forecast summary for quick-glance display.
    Includes: peak_hour, min_aqi, max_aqi, avg_aqi, overall_risk,
    alert_recommended, and the full hourly array.
    """
    try:
        summary = forecast.get_forecast_summary(city)
        return success(summary, message=f"Forecast summary for {city}.")
    except Exception as exc:
        return error(f"Forecast summary unavailable: {exc}", 503)
