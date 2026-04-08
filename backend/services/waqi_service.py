import requests
import os
from datetime import datetime
from models.aqi import AQIClassifier, Pollutants, AirQualityData

class WAQIService:
    def __init__(self, token=None):
        self.token = token or os.getenv("WAQI_API_TOKEN")
        self.base_url = "https://api.waqi.info"

    def get_city_aqi(self, city):
        # 强制使用模拟数据以测试 Hazardous 级别
        return self._mock_data(city)
        
        if not self.token:
            return self._mock_data(city)

    def get_geo_aqi(self, lat, lon):
        # 强制使用模拟数据以测试 Hazardous 级别
        return self._mock_data(f"GPS:{lat},{lon}")
        
        if not self.token:
            return self._mock_data(f"GPS:{lat},{lon}")

    def _parse_waqi_data(self, data, city_name):
        aqi = data.get("aqi", 0)
        risk = AQIClassifier.classify(aqi)
        pollutants = Pollutants(
            pm25=data.get("iaqi", {}).get("pm25", {}).get("v", 0),
            pm10=data.get("iaqi", {}).get("pm10", {}).get("v", 0)
        )
        return {
            "success": True,
            "data": {
                "aqi": aqi,
                "city": city_name,
                "timestamp": data.get("time", {}).get("s", datetime.now().isoformat()),
                "pollutants": {
                    "pm25": pollutants.pm25,
                    "pm10": pollutants.pm10
                },
                "risk": {
                    "label": risk.label,
                    "color": risk.color,
                    "icon": risk.icon,
                    "guidance": risk.guidance
                },
                "alert": {
                    "active": aqi >= 101,
                    "risk_label": risk.label,
                    "message": f"Air quality in {city_name} is {risk.label} (AQI {aqi})." if aqi >= 101 else None
                }
            }
        }

    def _mock_data(self, city):
        import random
        # 强制设置为 Hazardous 级别 (301-500)
        aqi = 350
        risk = AQIClassifier.classify(aqi)
        return {
            "success": True,
            "data": {
                "aqi": aqi,
                "city": city,
                "timestamp": datetime.now().isoformat(),
                "pollutants": {"pm25": aqi * 0.45, "pm10": aqi * 0.75},
                "risk": {
                    "label": risk.label,
                    "color": risk.color,
                    "icon": risk.icon,
                    "guidance": risk.guidance
                },
                "alert": {
                    "active": aqi >= 101,
                    "risk_label": risk.label,
                    "message": f"Air quality in {city} is {risk.label} (AQI {aqi})." if aqi >= 101 else None
                }
            }
        }
