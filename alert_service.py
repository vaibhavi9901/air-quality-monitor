"""
services/alert_service.py — Alert evaluation and notification dispatch.

This module:
  • Evaluates whether a reading crosses an alert threshold.
  • Builds structured alert payloads for the frontend.
  • Provides a hook (_send_push_notification) where a real push / email
    service (Firebase FCM, SendGrid, etc.) can be plugged in.
"""

from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

from models.aqi import AirQualityReading, classify_aqi

log = logging.getLogger(__name__)

# ── Alert threshold (AQI ≥ 101 triggers an alert) ────────────────────────────
ALERT_THRESHOLD = 101


def _format_time(ts: str) -> str:
    """Convert ISO timestamp to a human-friendly string."""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %I:%M %p UTC")
    except Exception:
        return ts


def evaluate_alert(reading: AirQualityReading) -> dict:
    """
    Evaluate a reading and return a full alert payload.

    Returns a dict with:
        active      — bool, whether an alert is warranted
        level       — "INFO" | "WARNING" | "CRITICAL"
        aqi         — current AQI
        risk_label  — e.g. "Unhealthy"
        color       — hex colour for the risk tier
        message     — user-facing alert string
        guidance    — health advice sentence
        timestamp   — formatted timestamp
        notify      — bool, whether a push notification should fire
    """
    aqi  = reading.aqi
    risk = reading.risk
    ts   = _format_time(reading.timestamp)

    active  = aqi >= ALERT_THRESHOLD
    notify  = active  # extend: check user prefs / cooldown

    if aqi >= 301:
        level = "CRITICAL"
    elif aqi >= 101:
        level = "WARNING"
    else:
        level = "INFO"

    if active:
        message = (
            f"Air quality alert for {reading.city}: "
            f"{risk['label']} (AQI {int(aqi)}). "
            f"{risk['short_desc']}"
        )
    else:
        message = (
            f"Air quality in {reading.city} is {risk['label']} "
            f"(AQI {int(aqi)}). {risk['short_desc']}"
        )

    payload = {
        "active":       active,
        "level":        level,
        "aqi":          aqi,
        "pm25":         reading.pollutants.pm25,
        "risk_label":   risk["label"],
        "risk_code":    risk["code"],
        "color":        risk["color"],
        "icon":         risk["icon"],
        "message":      message,
        "guidance":     risk["guidance"],
        "city":         reading.city,
        "station":      reading.station,
        "timestamp":    ts,
        "notify":       notify,
    }

    if notify:
        _send_push_notification(payload)

    return payload


def _send_push_notification(payload: dict) -> None:
    """
    Stub for real push notification dispatch.

    Replace the body of this function with your preferred provider:
      - Firebase FCM:   POST to https://fcm.googleapis.com/fcm/send
      - Twilio SMS:     client.messages.create(...)
      - SendGrid email: sg.send(message)
      - WebSocket push: emit("alert", payload)
    """
    log.info(
        "[PUSH NOTIFICATION] %s | AQI %s | %s",
        payload["city"],
        payload["aqi"],
        payload["message"],
    )
    # TODO: implement real push here


def build_alert_history(readings: list[dict]) -> list[dict]:
    """
    Given a list of historical reading dicts (each with 'aqi', 'timestamp',
    'city'), return only those that crossed the alert threshold, enriched
    with risk metadata.  Useful for the alert-history endpoint.
    """
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
