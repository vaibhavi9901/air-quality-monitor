"""
routes/alerts.py — Alert endpoints with UPDATE_DELAYED handling (#8).
"""

from flask import Blueprint, request
import services.openmeteo_service as openmeteo
import services.alert_service as alerts
from utils.responses import success, error

alerts_bp  = Blueprint("alerts", __name__)
_subscribers: dict[str, dict] = {}


def _update_delayed():
    return success({
        "status":  "UPDATE_DELAYED",
        "message": "UPDATE DELAYED",
        "active":  False,
        "aqi":     None,
    }, message="UPDATE DELAYED")


@alerts_bp.get("/check/city/<path:city>")
def check_alert_city(city: str):
    reading = openmeteo.get_by_city(city)
    if reading is None:
        return _update_delayed()   # #8
    payload = alerts.evaluate_alert(reading)
    from services.openmeteo_service import _format_datetime
    dt = _format_datetime(reading.timestamp)
    payload["date"]         = dt["date"]
    payload["last_updated"] = dt["last_updated"]
    payload["data_source"]  = "Open-Meteo"
    return success(payload, message="Alert evaluation complete.")


@alerts_bp.get("/check/geo")
def check_alert_geo():
    try:
        lat = float(request.args["lat"])
        lon = float(request.args["lon"])
    except (KeyError, ValueError):
        return error("Parameters 'lat' and 'lon' are required.")
    reading = openmeteo.get_by_coordinates(lat, lon)
    if reading is None:
        return _update_delayed()   # #8
    payload = alerts.evaluate_alert(reading)
    from services.openmeteo_service import _format_datetime
    dt = _format_datetime(reading.timestamp)
    payload["date"]         = dt["date"]
    payload["last_updated"] = dt["last_updated"]
    payload["data_source"]  = "Open-Meteo"
    return success(payload, message="Alert evaluation complete.")


@alerts_bp.post("/subscribe")
def subscribe():
    data  = request.get_json(silent=True) or {}
    token = data.get("token", "").strip()
    if not token:
        return error("'token' field is required.")
    _subscribers[token] = {
        "token": token, "type": data.get("type", "fcm"),
        "city": data.get("city", "Kuala Lumpur"),
        "threshold": int(data.get("threshold", 101)),
    }
    return success({"token": token}, message="Subscribed.", status=201)


@alerts_bp.delete("/subscribe/<token>")
def unsubscribe(token: str):
    if token in _subscribers:
        del _subscribers[token]
        return success({"token": token}, message="Unsubscribed.")
    return error("Subscription not found.", 404)


@alerts_bp.get("/subscribers/count")
def subscriber_count():
    return success({"count": len(_subscribers)})


# """
# routes/alerts.py — Alert evaluation and notification management.

# GET /api/alerts/check/city/<city>
#     Evaluate current conditions for *city* and return alert status.

# GET /api/alerts/check/geo?lat=<lat>&lon=<lon>
#     Evaluate current conditions for coordinates and return alert status.

# POST /api/alerts/subscribe
#     Register a device/email for push notifications (stub — wire up FCM).

# DELETE /api/alerts/subscribe/<token>
#     Unsubscribe a device from push notifications.
# """

# from flask import Blueprint, request
# import waqi_service as waqi
# import alert_service as alerts
# from responses import success, error

# alerts_bp = Blueprint("alerts", __name__)

# # In-memory subscriber store (replace with DB in production)
# _subscribers: dict[str, dict] = {}


# @alerts_bp.get("/check/city/<path:city>")
# def check_alert_city(city: str):
#     """
#     Return a full alert evaluation for *city*.
#     The frontend should call this endpoint on page load and every 60 s
#     to satisfy the ≤5 second alert delivery SLA.

#     Response fields:
#       active      — bool, should alert banner be shown?
#       level       — INFO | WARNING | CRITICAL
#       aqi, pm25
#       risk_label, color, icon
#       message     — user-facing alert string (display verbatim)
#       guidance    — short health recommendation
#       timestamp
#       notify      — bool (server-side push was/would be dispatched)
#     """
#     reading = waqi.get_by_city(city)
#     if reading is None:
#         return error(f"Could not retrieve data for '{city}'.", 503)

#     payload = alerts.evaluate_alert(reading)
#     return success(payload, message="Alert evaluation complete.")


# @alerts_bp.get("/check/geo")
# def check_alert_geo():
#     """
#     Return alert evaluation for GPS coordinates.
#     Example: GET /api/alerts/check/geo?lat=3.1390&lon=101.6869
#     """
#     try:
#         lat = float(request.args["lat"])
#         lon = float(request.args["lon"])
#     except (KeyError, ValueError):
#         return error("Parameters 'lat' and 'lon' are required.")

#     reading = waqi.get_by_coordinates(lat, lon)
#     if reading is None:
#         return error("Could not retrieve data for the given coordinates.", 503)

#     payload = alerts.evaluate_alert(reading)
#     return success(payload, message="Alert evaluation complete.")


# @alerts_bp.post("/subscribe")
# def subscribe():
#     """
#     Register a push-notification subscription.

#     Expected JSON body:
#     {
#         "token":    "<FCM device token or email>",
#         "type":     "fcm" | "email",
#         "city":     "Kuala Lumpur",
#         "threshold": 101        (optional, default 101)
#     }

#     Production: persist to database and integrate with FCM / SendGrid.
#     """
#     data = request.get_json(silent=True) or {}
#     token = data.get("token", "").strip()
#     if not token:
#         return error("'token' field is required.")

#     _subscribers[token] = {
#         "token":     token,
#         "type":      data.get("type", "fcm"),
#         "city":      data.get("city", "Kuala Lumpur"),
#         "threshold": int(data.get("threshold", 101)),
#     }

#     return success(
#         {"token": token},
#         message="Subscribed to air quality alerts.",
#         status=201
#     )


# @alerts_bp.delete("/subscribe/<token>")
# def unsubscribe(token: str):
#     """Remove a push-notification subscription."""
#     if token in _subscribers:
#         del _subscribers[token]
#         return success({"token": token}, message="Unsubscribed successfully.")
#     return error("Subscription not found.", 404)


# @alerts_bp.get("/subscribers/count")
# def subscriber_count():
#     """Return the number of active alert subscribers (admin use)."""
#     return success({"count": len(_subscribers)})
