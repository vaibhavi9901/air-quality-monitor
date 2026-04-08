"""
services/alert_service.py — Alert evaluation.
Also persists alerts to the database alerts table.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

from models.aqi import AirQualityReading, classify_aqi

log = logging.getLogger(__name__)

ALERT_THRESHOLD = 101


def _format_time(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %I:%M %p UTC")
    except Exception:
        return ts


def evaluate_alert(reading: AirQualityReading) -> dict:
    aqi  = reading.aqi
    risk = reading.risk
    ts   = _format_time(reading.timestamp)

    active = aqi >= ALERT_THRESHOLD
    notify = active

    if aqi >= 301:   level = "CRITICAL"
    elif aqi >= 101: level = "WARNING"
    else:            level = "INFO"

    message = (
        f"⚠️ Air quality in {reading.city} is {risk['label']} (AQI {int(aqi)}). {risk['short_desc']}"
        if active else
        f"✅ Air quality in {reading.city} is {risk['label']} (AQI {int(aqi)}). {risk['short_desc']}"
    )

    payload = {
        "active":     active,
        "level":      level,
        "aqi":        aqi,
        "pm25":       reading.pollutants.pm25,
        "risk_label": risk["label"],
        "risk_code":  risk["code"],
        "color":      risk["color"],
        "icon":       risk["icon"],
        "message":    message,
        "guidance":   risk["guidance"],
        "city":       reading.city,
        "station":    reading.station,
        "timestamp":  ts,
        "notify":     notify,
    }

    # Persist to database
    _save_to_db(payload)

    if notify:
        _send_push_notification(payload)

    return payload


def _save_to_db(payload: dict) -> None:
    """Save alert to the alerts table."""
    try:
        from database.models import db, Alert
        alert = Alert(
            city        = payload["city"],
            created_at  = datetime.utcnow(),
            active      = payload["active"],
            alert_level = payload["level"],
            aqi         = int(payload["aqi"]) if payload["aqi"] else None,
            risk_label  = payload["risk_label"],
            color       = payload["color"],
            message     = payload["message"],
            guidance    = payload["guidance"],
            notify      = payload["notify"],
        )
        db.session.add(alert)
        db.session.commit()
    except Exception as exc:
        log.warning("Could not save alert to DB: %s", exc)


def _send_push_notification(payload: dict) -> None:
    log.info("[PUSH] %s | AQI %s | %s", payload["city"], payload["aqi"], payload["message"])


def build_alert_history(readings: list[dict]) -> list[dict]:
    alerts = []
    for r in readings:
        aqi = float(r.get("aqi", 0))
        if aqi >= ALERT_THRESHOLD:
            risk = classify_aqi(aqi)
            alerts.append({
                "city":       r.get("city", "Unknown"),
                "aqi":        aqi,
                "risk_label": risk["label"],
                "color":      risk["color"],
                "timestamp":  r.get("timestamp", ""),
                "guidance":   risk["guidance"],
            })
    return alerts