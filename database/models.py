"""
database/models.py — SQLAlchemy models matching database.sql schema.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AirQualityReading(db.Model):
    __tablename__ = "air_quality_readings"

    id            = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    city          = db.Column(db.String(100), nullable=False)
    timestamp     = db.Column(db.DateTime,    nullable=False)
    aqi           = db.Column(db.Integer,  nullable=True)
    pm25          = db.Column(db.Float,    nullable=True)
    pm10          = db.Column(db.Float,    nullable=True)
    risk_label    = db.Column(db.String(50),  nullable=True)
    risk_color    = db.Column(db.String(20),  nullable=True)
    risk_icon     = db.Column(db.String(20),  nullable=True)
    risk_guidance = db.Column(db.Text,        nullable=True)
    alert_active  = db.Column(db.Boolean,     default=False)
    alert_message = db.Column(db.Text,        nullable=True)

    def to_dict(self):
        return {
            "id":            self.id,
            "city":          self.city,
            "timestamp":     self.timestamp.isoformat() if self.timestamp else None,
            "aqi":           self.aqi,
            "pm25":          self.pm25,
            "pm10":          self.pm10,
            "risk_label":    self.risk_label,
            "risk_color":    self.risk_color,
            "risk_icon":     self.risk_icon,
            "risk_guidance": self.risk_guidance,
            "alert_active":  self.alert_active,
            "alert_message": self.alert_message,
        }


class Alert(db.Model):
    __tablename__ = "alerts"

    id          = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    city        = db.Column(db.String(100), nullable=False)
    created_at  = db.Column(db.DateTime,   default=datetime.utcnow)
    active      = db.Column(db.Boolean,    default=False)
    alert_level = db.Column(db.String(50), nullable=True)
    aqi         = db.Column(db.Integer,    nullable=True)
    risk_label  = db.Column(db.String(50), nullable=True)
    color       = db.Column(db.String(20), nullable=True)
    message     = db.Column(db.Text,       nullable=True)
    guidance    = db.Column(db.Text,       nullable=True)
    notify      = db.Column(db.Boolean,    default=False)

    def to_dict(self):
        return {
            "id":          self.id,
            "city":        self.city,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "active":      self.active,
            "alert_level": self.alert_level,
            "aqi":         self.aqi,
            "risk_label":  self.risk_label,
            "color":       self.color,
            "message":     self.message,
            "guidance":    self.guidance,
            "notify":      self.notify,
        }


class ForecastSummary(db.Model):
    __tablename__ = "forecast_summary"

    id                = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    city              = db.Column(db.String(100), nullable=False)
    forecast_date     = db.Column(db.Date,        nullable=True)
    max_aqi           = db.Column(db.Float,       nullable=True)
    min_aqi           = db.Column(db.Float,       nullable=True)
    avg_aqi           = db.Column(db.Float,       nullable=True)
    peak_hour         = db.Column(db.Integer,     nullable=True)
    peak_risk         = db.Column(db.String(50),  nullable=True)
    alert_recommended = db.Column(db.Boolean,     default=False)

    hourly = db.relationship("ForecastHourly", back_populates="summary",
                             cascade="all, delete-orphan")

    def to_dict(self, include_hourly=True):
        d = {
            "id":                self.id,
            "city":              self.city,
            "forecast_date":     self.forecast_date.isoformat() if self.forecast_date else None,
            "max_aqi":           self.max_aqi,
            "min_aqi":           self.min_aqi,
            "avg_aqi":           self.avg_aqi,
            "peak_hour":         self.peak_hour,
            "peak_risk":         self.peak_risk,
            "alert_recommended": self.alert_recommended,
        }
        if include_hourly:
            d["hourly"] = [h.to_dict() for h in
                           sorted(self.hourly, key=lambda x: x.hour)]
        return d


class ForecastHourly(db.Model):
    __tablename__ = "forecast_hourly"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    forecast_id = db.Column(db.Integer, db.ForeignKey("forecast_summary.id"), nullable=False)
    hour        = db.Column(db.Integer, nullable=False)
    aqi         = db.Column(db.Float,   nullable=True)
    risk_label  = db.Column(db.String(50), nullable=True)
    color       = db.Column(db.String(20), nullable=True)

    summary = db.relationship("ForecastSummary", back_populates="hourly")

    def to_dict(self):
        return {
            "hour":       self.hour,
            "aqi":        self.aqi,
            "risk_label": self.risk_label,
            "color":      self.color,
        }


class SeasonalSummary(db.Model):
    __tablename__ = "seasonal_summary"

    id           = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    city         = db.Column(db.String(100), nullable=False)
    peak_month   = db.Column(db.String(20),  nullable=True)
    safest_month = db.Column(db.String(20),  nullable=True)

    months = db.relationship("SeasonalMonth", back_populates="summary",
                             cascade="all, delete-orphan")

    def to_dict(self, include_months=True):
        d = {
            "id":           self.id,
            "city":         self.city,
            "peak_month":   self.peak_month,
            "safest_month": self.safest_month,
        }
        if include_months:
            d["months"] = [m.to_dict() for m in
                           sorted(self.months, key=lambda x: x.month)]
        return d


class SeasonalMonth(db.Model):
    __tablename__ = "seasonal_months"

    id             = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    seasonal_id    = db.Column(db.Integer,    db.ForeignKey("seasonal_summary.id"), nullable=False)
    month          = db.Column(db.Integer,    nullable=True)
    month_name     = db.Column(db.String(20), nullable=True)
    api            = db.Column(db.Float,      nullable=True)
    risk_label     = db.Column(db.String(50), nullable=True)
    color          = db.Column(db.String(20), nullable=True)
    season         = db.Column(db.String(100),nullable=True)
    driver         = db.Column(db.Text,       nullable=True)
    characteristic = db.Column(db.Text,       nullable=True)
    tip            = db.Column(db.Text,       nullable=True)

    summary = db.relationship("SeasonalSummary", back_populates="months")

    def to_dict(self):
        return {
            "month":          self.month,
            "month_name":     self.month_name,
            "aqi":            self.api,
            "risk_label":     self.risk_label,
            "color":          self.color,
            "season":         self.season,
            "driver":         self.driver,
            "characteristic": self.characteristic,
            "tip":            self.tip,
        }


class RiskTier(db.Model):
    __tablename__ = "risk_tiers"

    id      = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    label   = db.Column(db.String(50), nullable=False)
    min_aqi = db.Column(db.Integer,    nullable=False)
    max_aqi = db.Column(db.Integer,    nullable=False)
    color   = db.Column(db.String(20), nullable=False)
    alert   = db.Column(db.Boolean,    nullable=False)

    def to_dict(self):
        return {
            "label":   self.label,
            "min_aqi": self.min_aqi,
            "max_aqi": self.max_aqi,
            "color":   self.color,
            "alert":   self.alert,
        }