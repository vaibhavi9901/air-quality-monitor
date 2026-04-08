"""
models/aqi.py — AQI data-classes and classification logic.

Malaysian API (Air Pollutant Index) uses a 0-500 scale similar to the
US AQI but with slightly different breakpoints.  We map both AQI and raw
PM2.5 µg/m³ to the same five-tier risk system used in the UI.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ── Risk tier definitions ────────────────────────────────────────────────────

RISK_TIERS = [
    {
        "label":        "Good",
        "code":         "GOOD",
        "aqi_range":    (0, 50),
        "pm25_range":   (0.0, 12.0),
        "color":        "#22c55e",   # green
        "icon":         "😊",
        "short_desc":   "Air quality is satisfactory.",
        "guidance":     "Suitable for normal outdoor walking and activities.",
        "alert":        False,
    },
    {
        "label":        "Moderate",
        "code":         "MODERATE",
        "aqi_range":    (51, 100),
        "pm25_range":   (12.1, 35.4),
        "color":        "#eab308",   # yellow
        "icon":         "😐",
        "short_desc":   "Air quality is acceptable.",
        "guidance":     "Unusually sensitive individuals should consider "
                        "limiting prolonged outdoor exertion.",
        "alert":        False,
    },
    {
        "label":        "Unhealthy",
        "code":         "UNHEALTHY",
        "aqi_range":    (101, 200),
        "pm25_range":   (35.5, 55.4),
        "color":        "#f97316",   # orange
        "icon":         "😷",
        "short_desc":   "Everyone may begin to experience health effects.",
        "guidance":     "Recommended to reduce outdoor activities. "
                        "Elderly and those with respiratory conditions "
                        "should stay indoors.",
        "alert":        True,
    },
    {
        "label":        "Very Unhealthy",
        "code":         "VERY_UNHEALTHY",
        "aqi_range":    (201, 300),
        "pm25_range":   (55.5, 150.4),
        "color":        "#ef4444",   # red
        "icon":         "🚫",
        "short_desc":   "Health warnings of emergency conditions.",
        "guidance":     "Avoid all outdoor activities. Wear an N95 mask "
                        "if you must go outside. Keep windows closed.",
        "alert":        True,
    },
    {
        "label":        "Hazardous",
        "code":         "HAZARDOUS",
        "aqi_range":    (301, 500),
        "pm25_range":   (150.5, 500.0),
        "color":        "#7c3aed",   # purple
        "icon":         "☠️",
        "short_desc":   "Health alert: everyone may experience serious effects.",
        "guidance":     "Stay indoors with air purifiers running. "
                        "Seek medical attention if experiencing symptoms.",
        "alert":        True,
    },
]


def classify_aqi(aqi: float) -> dict:
    """Return the risk-tier dict for a given AQI value."""
    for tier in RISK_TIERS:
        lo, hi = tier["aqi_range"]
        if lo <= aqi <= hi:
            return tier
    # If above 500, fall through to Hazardous
    return RISK_TIERS[-1]


def classify_pm25(pm25: float) -> dict:
    """Return the risk-tier dict for a raw PM2.5 µg/m³ value."""
    for tier in RISK_TIERS:
        lo, hi = tier["pm25_range"]
        if lo <= pm25 <= hi:
            return tier
    return RISK_TIERS[-1]


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Pollutants:
    pm25:  Optional[float] = None   # µg/m³
    pm10:  Optional[float] = None
    o3:    Optional[float] = None
    no2:   Optional[float] = None
    so2:   Optional[float] = None
    co:    Optional[float] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class AirQualityReading:
    aqi:          float
    station:      str
    city:         str
    country:      str
    latitude:     float
    longitude:    float
    timestamp:    str                       # ISO-8601
    pollutants:   Pollutants = field(default_factory=Pollutants)
    dominant_pollutant: str = "pm25"

    @property
    def risk(self) -> dict:
        return classify_aqi(self.aqi)

    @property
    def should_alert(self) -> bool:
        return self.risk["alert"]

    def to_dict(self) -> dict:
        risk = self.risk
        return {
            "aqi":                  self.aqi,
            "station":              self.station,
            "city":                 self.city,
            "country":              self.country,
            "latitude":             self.latitude,
            "longitude":            self.longitude,
            "timestamp":            self.timestamp,
            "dominant_pollutant":   self.dominant_pollutant,
            "pollutants":           self.pollutants.to_dict(),
            "risk": {
                "label":       risk["label"],
                "code":        risk["code"],
                "color":       risk["color"],
                "icon":        risk["icon"],
                "short_desc":  risk["short_desc"],
                "guidance":    risk["guidance"],
            },
            "alert": {
                "active":   self.should_alert,
                "message":  (
                    f"⚠️ Air quality in {self.city} is {risk['label']} "
                    f"(AQI {int(self.aqi)}). {risk['guidance']}"
                ) if self.should_alert else None,
            },
        }


@dataclass
class ForecastPoint:
    hour:      int        # 0-23
    aqi:       float
    pm25:      Optional[float] = None

    @property
    def risk(self) -> dict:
        return classify_aqi(self.aqi)

    def to_dict(self) -> dict:
        risk = self.risk
        return {
            "hour":   self.hour,
            "aqi":    self.aqi,
            "pm25":   self.pm25,
            "label":  risk["label"],
            "color":  risk["color"],
            "icon":   risk["icon"],
        }
