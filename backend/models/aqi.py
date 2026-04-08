from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AQIRisk:
    label: str
    color: str
    icon: str
    guidance: str

class AQIClassifier:
    @staticmethod
    def classify(aqi: int) -> AQIRisk:
        if aqi <= 50:
            return AQIRisk("Good", "#22c55e", "🟢", "Air quality is considered satisfactory, and air pollution poses little or no risk.")
        elif aqi <= 100:
            return AQIRisk("Moderate", "#eab308", "🟡", "Air quality is acceptable; however, for some pollutants, there may be a moderate health concern for a very small number of people who are unusually sensitive to air pollution.")
        elif aqi <= 200:
            return AQIRisk("Unhealthy", "#f97316", "🟠", "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.")
        elif aqi <= 300:
            return AQIRisk("Very Unhealthy", "#ef4444", "🔴", "Health warnings of emergency conditions. The entire population is more likely to be affected.")
        else:
            return AQIRisk("Hazardous", "#7c3aed", "🟣", "Health alert: everyone may experience more serious health effects.")

@dataclass
class Pollutants:
    pm25: float
    pm10: float

@dataclass
class AirQualityData:
    aqi: int
    city: str
    timestamp: str
    pollutants: Pollutants
    risk: AQIRisk
    alert: Dict[str, Optional[str]]
