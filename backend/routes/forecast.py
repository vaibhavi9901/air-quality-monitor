from flask import Blueprint, jsonify, request
import random
from datetime import datetime, timedelta

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/<city>/summary', methods=['GET'])
def get_forecast_summary(city):
    now = datetime.now()
    hourly = []
    for i in range(24):
        time = now + timedelta(hours=i)
        # 强制设置为 Hazardous 级别 (301-500)
        aqi = 350
        if aqi <= 50:
            label, color, icon = "Good", "#22c55e", "🟢"
        elif aqi <= 100:
            label, color, icon = "Moderate", "#eab308", "🟡"
        elif aqi <= 200:
            label, color, icon = "Unhealthy", "#f97316", "🟠"
        elif aqi <= 300:
            label, color, icon = "Very Unhealthy", "#ef4444", "🔴"
        else:
            label, color, icon = "Hazardous", "#7c3aed", "🟣"
            
        hourly.append({
            "hour": time.hour,
            "time": time.isoformat(),
            "aqi": aqi,
            "pm25": aqi * 0.5,
            "label": label,
            "color": color,
            "icon": icon
        })
    
    return jsonify({
        "success": True,
        "data": {
            "city": city,
            "max_aqi": max(h["aqi"] for h in hourly),
            "min_aqi": min(h["aqi"] for h in hourly),
            "avg_aqi": sum(h["aqi"] for h in hourly) / len(hourly),
            "peak_hour": next(h["hour"] for h in hourly if h["aqi"] == max(h["aqi"] for h in hourly)),
            "peak_risk": "Hazardous",
            "alert_recommended": True,
            "hourly": hourly
        }
    })
