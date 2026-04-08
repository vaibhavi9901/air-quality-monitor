"""
populate_db.py — Fetch data from Open-Meteo and populate the database schema.

Run from your backend folder:
    python populate_db.py

What it populates:
  - air_quality_readings   current AQI reading per city
  - alerts                 alert evaluation per city
  - forecast_summary       24-hour forecast summary per city
  - forecast_hourly        hourly points linked to each forecast_summary
  - seasonal_summary       seasonal overview per city
  - seasonal_months        12 monthly rows linked to each seasonal_summary
  - risk_tiers             already seeded by schema (skipped if present)
"""

import sqlite3
import requests
import logging
from datetime import date, datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DB_PATH         = "airquality.db"
GEOCODING_URL   = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DATA_CUTOFF     = date(2026, 2, 28)

MALAYSIAN_CITIES = [
    "Kuala Lumpur", "Petaling Jaya", "Shah Alam", "Johor Bahru",
    "Penang", "Ipoh", "Kota Kinabalu", "Kuching", "Alor Setar",
    "Kuantan", "Seremban", "Melaka", "Kota Bharu", "Kuala Terengganu",
    "Sandakan", "Miri", "Sibu", "Tawau", "Butterworth", "Subang Jaya",
]

SEASONAL_CONTEXT = {
    1:  {"season": "Post-Monsoon Clearance",  "driver": "Northeast monsoon winds clearing residual urban haze",        "characteristic": "Transitional — improving air quality",           "tip": "Good time to resume outdoor exercise routines."},
    2:  {"season": "Dry Inter-Monsoon",        "driver": "Low wind, urban exhaust accumulation",                       "characteristic": "Moderate urban pollution, stagnant air",          "tip": "Avoid high-traffic roads during peak hours (7–9 am, 5–7 pm)."},
    3:  {"season": "Pre-Haze Season",          "driver": "Start of land-clearing burns in Sumatra & Borneo",          "characteristic": "Rising PM2.5, early transboundary haze",          "tip": "Monitor daily API readings; prepare N95 masks at home."},
    4:  {"season": "Haze Season (Early)",      "driver": "Regional agricultural burning (Sumatra, Kalimantan)",       "characteristic": "Transboundary haze episodes",                     "tip": "Use air purifiers indoors; limit morning outdoor walks."},
    5:  {"season": "Haze Season (Peak)",       "driver": "Peak biomass burning + hot, dry conditions",                "characteristic": "Highest annual PM2.5 concentrations",             "tip": "Use air purifiers; keep windows closed; wear N95 outdoors."},
    6:  {"season": "Haze Season (Late)",       "driver": "Residual burning + urban construction dust",                "characteristic": "Persistently elevated pollution",                  "tip": "Stay indoors during hazy afternoons; hydrate well."},
    7:  {"season": "Southwest Monsoon",        "driver": "Monsoon rains washing out pollutants, brief respite",       "characteristic": "Improved air quality between rain spells",         "tip": "Take advantage of post-rain windows for outdoor activity."},
    8:  {"season": "Monsoon Stagnation",       "driver": "Urban exhaust trapped by low inversion layer",              "characteristic": "Localised urban smog pockets",                    "tip": "Avoid high-traffic roads; use public transport where possible."},
    9:  {"season": "Inter-Monsoon",            "driver": "Thunderstorm activity, erratic wind patterns",              "characteristic": "Variable — sudden spikes possible",               "tip": "Check API before outdoor plans; carry a mask as precaution."},
    10: {"season": "Festive Haze (Deepavali)", "driver": "Fireworks + incense burning during festive season",         "characteristic": "Short-lived but intense PM2.5 spikes",            "tip": "Close windows during celebrations; run air purifiers."},
    11: {"season": "Northeast Monsoon Onset",  "driver": "Heavy rainfall bringing cleaner air",                       "characteristic": "Improving conditions; flood-related dust possible","tip": "Good air quality overall; watch for post-flood mold spores."},
    12: {"season": "Year-End Festive Season",  "driver": "Christmas / New Year fireworks + increased traffic",        "characteristic": "Moderate festive spikes",                         "tip": "Close windows on New Year's Eve; air out home the next morning."},
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ── Schema creation (with bug fix) ───────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS air_quality_readings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    city          VARCHAR(100) NOT NULL,
    timestamp     DATETIME NOT NULL,
    aqi           INTEGER,
    pm25          FLOAT,
    pm10          FLOAT,
    risk_label    VARCHAR(50),
    risk_color    VARCHAR(20),
    risk_icon     VARCHAR(20),
    risk_guidance TEXT,
    alert_active  BOOLEAN,
    alert_message TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    city        VARCHAR(100) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    active      BOOLEAN,
    alert_level VARCHAR(50),
    aqi         INTEGER,
    risk_label  VARCHAR(50),
    color       VARCHAR(20),
    message     TEXT,
    guidance    TEXT,
    notify      BOOLEAN
);

CREATE TABLE IF NOT EXISTS forecast_summary (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    city               VARCHAR(100) NOT NULL,
    forecast_date      DATE,
    max_aqi            FLOAT,
    min_aqi            FLOAT,
    avg_aqi            FLOAT,
    peak_hour          INTEGER,
    peak_risk          VARCHAR(50),
    alert_recommended  BOOLEAN
);

CREATE TABLE IF NOT EXISTS forecast_hourly (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_id INTEGER NOT NULL,
    hour        INTEGER NOT NULL,
    aqi         FLOAT,
    risk_label  VARCHAR(50),
    color       VARCHAR(20),
    FOREIGN KEY (forecast_id) REFERENCES forecast_summary(id)
);

CREATE TABLE IF NOT EXISTS seasonal_summary (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    city         VARCHAR(100) NOT NULL,
    peak_month   VARCHAR(20),
    safest_month VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS seasonal_months (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    seasonal_id    INTEGER NOT NULL,
    month          INTEGER,
    month_name     VARCHAR(20),
    api            FLOAT,
    risk_label     VARCHAR(50),
    color          VARCHAR(20),
    season         VARCHAR(100),
    driver         TEXT,
    characteristic TEXT,
    tip            TEXT,
    FOREIGN KEY (seasonal_id) REFERENCES seasonal_summary(id)
);

CREATE TABLE IF NOT EXISTS risk_tiers (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    label   VARCHAR(50)  NOT NULL,
    min_aqi INTEGER      NOT NULL,
    max_aqi INTEGER      NOT NULL,
    color   VARCHAR(20)  NOT NULL,
    alert   BOOLEAN      NOT NULL
);
"""

RISK_TIERS = [
    ("Good",          0,   50,  "#22c55e", 0),
    ("Moderate",      51,  100, "#eab308", 0),
    ("Unhealthy",     101, 200, "#f97316", 1),
    ("Very Unhealthy",201, 300, "#ef4444", 1),
    ("Hazardous",     301, 500, "#7c3aed", 1),
]


# ── Risk helpers ──────────────────────────────────────────────────────────────

def aqi_to_risk(aqi):
    if aqi is None: return ("Unknown", "#9ca3af", "❓", "Data unavailable.", False)
    if aqi <= 50:   return ("Good",          "#22c55e", "😊", "Suitable for normal outdoor walking.", False)
    if aqi <= 100:  return ("Moderate",      "#eab308", "😐", "Limit prolonged exertion if sensitive.", False)
    if aqi <= 200:  return ("Unhealthy",     "#f97316", "😷", "Reduce outdoor activities. Elderly should stay indoors.", True)
    if aqi <= 300:  return ("Very Unhealthy","#ef4444", "🚫", "Avoid all outdoor activities. Wear N95 if you must go out.", True)
    return               ("Hazardous",      "#7c3aed", "☠️", "Stay indoors. Seek medical help if symptomatic.", True)

def alert_level(aqi):
    if aqi is None or aqi < 101: return "INFO"
    if aqi < 301: return "WARNING"
    return "CRITICAL"


# ── Open-Meteo helpers ────────────────────────────────────────────────────────

def geocode(city_name):
    try:
        r = requests.get(GEOCODING_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=8)
        results = r.json().get("results", [])
        if results:
            return results[0]["latitude"], results[0]["longitude"]
    except Exception as e:
        log.warning("Geocode failed for %s: %s", city_name, e)
    return None, None


def fetch_current(lat, lon):
    """Fetch the current hour's AQI and pollutants."""
    try:
        r = requests.get(AIR_QUALITY_URL, params={
            "latitude": lat, "longitude": lon,
            "hourly": "us_aqi,pm2_5,pm10",
            "forecast_days": 1,
            "timezone": "Asia/Kuala_Lumpur",
        }, timeout=10)
        hourly = r.json().get("hourly", {})
        times  = hourly.get("time", [])
        aqi_arr  = hourly.get("us_aqi", [])
        pm25_arr = hourly.get("pm2_5", [])
        pm10_arr = hourly.get("pm10", [])

        # Find index closest to now
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        best_idx = 0
        best_diff = float("inf")
        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
                diff = abs((dt - now).total_seconds())
                if diff < best_diff:
                    best_diff = diff
                    best_idx = i
            except: continue

        return {
            "timestamp": times[best_idx] if best_idx < len(times) else datetime.utcnow().isoformat(),
            "aqi":  aqi_arr[best_idx]  if best_idx < len(aqi_arr)  else None,
            "pm25": pm25_arr[best_idx] if best_idx < len(pm25_arr) else None,
            "pm10": pm10_arr[best_idx] if best_idx < len(pm10_arr) else None,
        }
    except Exception as e:
        log.warning("fetch_current failed: %s", e)
        return None


def fetch_forecast(lat, lon):
    """Fetch 24 hourly AQI values starting from the current hour."""
    try:
        r = requests.get(AIR_QUALITY_URL, params={
            "latitude": lat, "longitude": lon,
            "hourly": "us_aqi",
            "forecast_days": 2,
            "timezone": "Asia/Kuala_Lumpur",
        }, timeout=10)
        hourly = r.json().get("hourly", {})
        times  = hourly.get("time", [])
        aqi_arr = hourly.get("us_aqi", [])

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        start_idx = 0
        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
                if dt >= now:
                    start_idx = i
                    break
            except: continue

        points = []
        for i in range(start_idx, min(start_idx + 24, len(times))):
            try:
                hour = int(times[i][11:13])
            except: hour = i % 24
            points.append({"hour": hour, "aqi": aqi_arr[i] if i < len(aqi_arr) else None})

        return points
    except Exception as e:
        log.warning("fetch_forecast failed: %s", e)
        return []


def fetch_monthly_aqi(lat, lon, year, month):
    """Fetch monthly average AQI (capped at DATA_CUTOFF)."""
    effective_today = min(date.today(), DATA_CUTOFF)
    start = date(year, month, 1)
    end   = (date(year, month+1, 1) if month < 12 else date(year+1, 1, 1)) - timedelta(days=1)
    if start > effective_today: return None
    if end > effective_today: end = effective_today

    try:
        r = requests.get(AIR_QUALITY_URL, params={
            "latitude": lat, "longitude": lon,
            "hourly": "us_aqi",
            "start_date": start.isoformat(),
            "end_date":   end.isoformat(),
            "timezone": "Asia/Kuala_Lumpur",
        }, timeout=15)
        aqi_arr = [v for v in r.json().get("hourly", {}).get("us_aqi", []) if v is not None]
        if not aqi_arr: return None
        return round(sum(aqi_arr) / len(aqi_arr), 1)
    except Exception as e:
        log.warning("fetch_monthly failed (%d-%02d): %s", year, month, e)
        return None


# ── Populate functions ────────────────────────────────────────────────────────

def populate_air_quality(conn, city, lat, lon):
    current = fetch_current(lat, lon)
    if not current:
        log.warning("  Skipping air_quality_readings for %s", city)
        return

    aqi = current["aqi"]
    label, color, icon, guidance, alert_active = aqi_to_risk(aqi)
    message = f"⚠️ Air quality in {city} is {label} (AQI {aqi}). {guidance}" if alert_active else None

    conn.execute("""
        INSERT INTO air_quality_readings
            (city, timestamp, aqi, pm25, pm10, risk_label, risk_color,
             risk_icon, risk_guidance, alert_active, alert_message)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (city, current["timestamp"], aqi, current["pm25"], current["pm10"],
          label, color, icon, guidance, alert_active, message))
    log.info("  air_quality_readings: AQI %s (%s)", aqi, label)


def populate_alerts(conn, city, lat, lon):
    current = fetch_current(lat, lon)
    if not current:
        return
    aqi = current["aqi"]
    label, color, icon, guidance, active = aqi_to_risk(aqi)
    level   = alert_level(aqi)
    message = f"⚠️ {city} is {label} (AQI {aqi}). {guidance}" if active else f"✅ {city} is {label} (AQI {aqi})."

    conn.execute("""
        INSERT INTO alerts
            (city, created_at, active, alert_level, aqi, risk_label,
             color, message, guidance, notify)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (city, datetime.utcnow().isoformat(), active, level,
          aqi, label, color, message, guidance, active))
    log.info("  alerts: %s active=%s", level, active)


def populate_forecast(conn, city, lat, lon):
    points = fetch_forecast(lat, lon)
    if not points:
        log.warning("  Skipping forecast for %s", city)
        return

    aqi_vals = [p["aqi"] for p in points if p["aqi"] is not None]
    if not aqi_vals: return

    max_aqi   = max(aqi_vals)
    min_aqi   = min(aqi_vals)
    avg_aqi   = round(sum(aqi_vals) / len(aqi_vals), 1)
    peak_idx  = aqi_vals.index(max_aqi)
    peak_hour = points[peak_idx]["hour"]
    peak_label, *_ = aqi_to_risk(max_aqi)
    alert_rec = max_aqi >= 101

    cursor = conn.execute("""
        INSERT INTO forecast_summary
            (city, forecast_date, max_aqi, min_aqi, avg_aqi,
             peak_hour, peak_risk, alert_recommended)
        VALUES (?,?,?,?,?,?,?,?)
    """, (city, date.today().isoformat(), max_aqi, min_aqi, avg_aqi,
          peak_hour, peak_label, alert_rec))

    forecast_id = cursor.lastrowid

    for p in points:
        label, color, *_ = aqi_to_risk(p["aqi"])
        conn.execute("""
            INSERT INTO forecast_hourly (forecast_id, hour, aqi, risk_label, color)
            VALUES (?,?,?,?,?)
        """, (forecast_id, p["hour"], p["aqi"], label, color))

    log.info("  forecast: avg=%.1f max=%.1f (%d hourly pts)", avg_aqi, max_aqi, len(points))


def populate_seasonal(conn, city, lat, lon):
    today      = min(date.today(), DATA_CUTOFF)
    start_year = today.year - 2   # 3 years back

    monthly_aqi = {}
    for year in range(start_year, today.year + 1):
        for month in range(1, 13):
            if date(year, month, 1) > today: continue
            avg = fetch_monthly_aqi(lat, lon, year, month)
            import time; time.sleep(0.3)
            if avg is not None:
                monthly_aqi[month] = avg   # last year wins (most recent)

    # Fill missing with static fallback
    STATIC = {1:52,2:58,3:65,4:72,5:85,6:78,7:60,8:63,9:61,10:70,11:55,12:60}
    for m in range(1, 13):
        if m not in monthly_aqi:
            monthly_aqi[m] = STATIC[m]

    def risk_color(aqi):
        if aqi <= 50:  return "#22c55e", "Good"
        if aqi <= 100: return "#eab308", "Moderate"
        if aqi <= 150: return "#f97316", "Unhealthy for Sensitive Groups"
        if aqi <= 200: return "#ef4444", "Unhealthy"
        return "#7c3aed", "Very Unhealthy"

    peak_m   = max(monthly_aqi, key=monthly_aqi.get)
    safest_m = min(monthly_aqi, key=monthly_aqi.get)

    cursor = conn.execute("""
        INSERT INTO seasonal_summary (city, peak_month, safest_month)
        VALUES (?,?,?)
    """, (city, MONTH_NAMES[peak_m - 1], MONTH_NAMES[safest_m - 1]))

    seasonal_id = cursor.lastrowid

    for m in range(1, 13):
        aqi_val = monthly_aqi[m]
        color, label = risk_color(aqi_val)
        ctx = SEASONAL_CONTEXT[m]
        conn.execute("""
            INSERT INTO seasonal_months
                (seasonal_id, month, month_name, api, risk_label, color,
                 season, driver, characteristic, tip)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (seasonal_id, m, MONTH_NAMES[m-1], aqi_val, label, color,
              ctx["season"], ctx["driver"], ctx["characteristic"], ctx["tip"]))

    log.info("  seasonal: peak=%s safest=%s", MONTH_NAMES[peak_m-1], MONTH_NAMES[safest_m-1])


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)

    # Seed risk_tiers if empty
    if conn.execute("SELECT COUNT(*) FROM risk_tiers").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO risk_tiers (label,min_aqi,max_aqi,color,alert) VALUES (?,?,?,?,?)",
            RISK_TIERS
        )
        log.info("Seeded risk_tiers.")

    conn.commit()

    total = len(MALAYSIAN_CITIES)
    for idx, city in enumerate(MALAYSIAN_CITIES, 1):
        log.info("[%d/%d] Processing %s…", idx, total, city)

        lat, lon = geocode(city)
        if lat is None:
            log.warning("  Could not geocode %s — skipping.", city)
            continue

        populate_air_quality(conn, city, lat, lon)
        populate_alerts(conn, city, lat, lon)
        populate_forecast(conn, city, lat, lon)
        populate_seasonal(conn, city, lat, lon)   # slowest — 36 API calls per city

        conn.commit()
        log.info("  ✓ %s done.", city)

    # Final counts
    for table in ["air_quality_readings","alerts","forecast_summary",
                  "forecast_hourly","seasonal_summary","seasonal_months","risk_tiers"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        log.info("%-25s %d rows", table, count)

    conn.close()
    log.info("=== Done. Database saved to %s ===", DB_PATH)


if __name__ == "__main__":
    main()
