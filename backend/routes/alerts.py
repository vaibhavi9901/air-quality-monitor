from flask import Blueprint, jsonify, request
import random

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/check/city/<city>', methods=['GET'])
def check_city_alert(city):
    # 强制设置为 Hazardous 级别 (301-500)
    aqi = 350
    if aqi <= 50:
        risk_label, color = "Good", "#22c55e"
    elif aqi <= 100:
        risk_label, color = "Moderate", "#eab308"
    elif aqi <= 200:
        risk_label, color = "Unhealthy", "#f97316"
    elif aqi <= 300:
        risk_label, color = "Very Unhealthy", "#ef4444"
    else:
        risk_label, color = "Hazardous", "#7c3aed"
    
    is_alert = aqi >= 101
    return jsonify({
        "success": True,
        "data": {
            "active": is_alert,
            "level": "WARNING" if is_alert else "NORMAL",
            "aqi": aqi,
            "risk_label": risk_label,
            "color": color,
            "message": f"⚠️ Air quality in {city} is {risk_label} (AQI {aqi})." if is_alert else None,
            "guidance": "Recommended to reduce outdoor activities." if is_alert else "Normal activities allowed.",
            "notify": is_alert
        }
    })
