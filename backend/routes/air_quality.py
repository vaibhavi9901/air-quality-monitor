from flask import Blueprint, jsonify, request
from services.waqi_service import WAQIService

air_quality_bp = Blueprint('air_quality', __name__)
waqi_service = WAQIService()

@air_quality_bp.route('/city/<city>', methods=['GET'])
def get_city_air_quality(city):
    data = waqi_service.get_city_aqi(city)
    return jsonify(data)

@air_quality_bp.route('/geo', methods=['GET'])
def get_geo_air_quality():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"success": False, "error": "Missing coordinates"}), 400
    
    data = waqi_service.get_geo_aqi(lat, lon)
    return jsonify(data)

@air_quality_bp.route('/stations', methods=['GET'])
def get_stations():
    stations = [
        {
            "station_id": "my-kul-001",
            "city_number": 1001,
            "state": "Kuala Lumpur",
            "city": "Kuala Lumpur",
            "lat": 3.1390,
            "lon": 101.6869,
            "aqi": 350,
            "risk": "Hazardous",
            "active": True,
        },
        {
            "station_id": "my-kul-002",
            "city_number": 1001,
            "state": "Kuala Lumpur",
            "city": "Kuala Lumpur",
            "lat": 3.1516,
            "lon": 101.7110,
            "aqi": 350,
            "risk": "Hazardous",
            "active": True,
        },
        {
            "station_id": "my-sel-001",
            "city_number": 2001,
            "state": "Selangor",
            "city": "Shah Alam",
            "lat": 3.0738,
            "lon": 101.5183,
            "aqi": 350,
            "risk": "Hazardous",
            "active": True,
        },
        {
            "station_id": "my-sel-002",
            "city_number": 2002,
            "state": "Selangor",
            "city": "Petaling PJ",
            "lat": 3.1073,
            "lon": 101.6067,
            "aqi": 350,
            "risk": "Hazardous",
            "active": True,
        },
        {
            "station_id": "my-pen-001",
            "city_number": 3001,
            "state": "Penang",
            "city": "George Town",
            "lat": 5.4141,
            "lon": 100.3288,
            "aqi": 350,
            "risk": "Hazardous",
            "active": True,
        },
        {
            "station_id": "my-joh-001",
            "city_number": 4001,
            "state": "Johor",
            "city": "Johor Bahru",
            "lat": 1.4854,
            "lon": 103.7618,
            "aqi": 65,
            "risk": "Moderate",
            "active": True,
        },
        {
            "station_id": "my-sar-001",
            "city_number": 5001,
            "state": "Sarawak",
            "city": "Kuching",
            "lat": 1.5533,
            "lon": 110.3592,
            "aqi": 35,
            "risk": "Good",
            "active": True,
        },
        {
            "station_id": "my-sar-002",
            "city_number": 5002,
            "state": "Sarawak",
            "city": "Miri",
            "lat": 4.3990,
            "lon": 113.9916,
            "aqi": 55,
            "risk": "Moderate",
            "active": False,
        },
    ]
    return jsonify({"success": True, "data": stations})
