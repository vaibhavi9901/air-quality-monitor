import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'airquality.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENMETEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    OPENMETEO_GEOCODING_URL   = "https://geocoding-api.open-meteo.com/v1/search"
    OPENDOSM_BASE_URL         = "https://api.data.gov.my/data-catalogue"
    OPENDOSM_AIR_DATASET      = "air_pollution_malaysia"

    REALTIME_CACHE_TTL   = 60
    FORECAST_CACHE_TTL   = 180
    HISTORICAL_CACHE_TTL = 3600

    ALERT_THRESHOLD = 101
    DEFAULT_CITY    = os.getenv("DEFAULT_CITY", "Kuala Lumpur")

# """
# config.py — Application configuration.

# Set environment variables before running:
#     WAQI_API_TOKEN   — free token from https://aqicn.org/api/
#     OPENWEATHER_KEY  — optional OpenWeatherMap key for geocoding fallback
#     SECRET_KEY       — Flask secret key
# """

# import os


# class Config:
#     # Flask
#     SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
#     DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

#     # Open-Meteo — no token required
#     OPENMETEO_AIR_QUALITY_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
#     OPENMETEO_GEOCODING_URL:   str = "https://geocoding-api.open-meteo.com/v1/search"

#     # World Air Quality Index (WAQI) — primary real-time data source
#     # Sign up free at https://aqicn.org/api/
#     WAQI_API_TOKEN: str = os.getenv("WAQI_API_TOKEN", "demo")
#     WAQI_BASE_URL: str = "https://api.waqi.info"

#     # OpenWeatherMap — geocoding / reverse-geocode fallback
#     OPENWEATHER_KEY: str = os.getenv("OPENWEATHER_KEY", "")
#     OPENWEATHER_GEO_URL: str = "https://api.openweathermap.org/geo/1.0"

#     # OpenDOSM — Malaysia official open data portal
#     OPENDOSM_BASE_URL: str = "https://api.data.gov.my/data-catalogue"
#     OPENDOSM_AIR_DATASET: str = "air_pollution_malaysia"

#     # Cache TTL (seconds)
#     REALTIME_CACHE_TTL: int = 60          # 1 min for live readings
#     FORECAST_CACHE_TTL: int = 180         # 3 min for forecasts
#     HISTORICAL_CACHE_TTL: int = 3600      # 1 hr for historical

#     # Alert thresholds (Malaysian API / AQI scale)
#     AQI_THRESHOLDS: dict = {
#         "GOOD":       (0,   50),
#         "MODERATE":   (51,  100),
#         "UNHEALTHY":  (101, 200),
#         "VERY_UNHEALTHY": (201, 300),
#         "HAZARDOUS":  (301, 500),
#     }

#     # Default fallback city when geolocation is unavailable
#     DEFAULT_CITY: str = "Kuala Lumpur"


# class DevelopmentConfig(Config):
#     DEBUG = True


# class ProductionConfig(Config):
#     DEBUG = False
