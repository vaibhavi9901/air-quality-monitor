from flask import Blueprint, jsonify, request
import random

historical_bp = Blueprint('historical', __name__)

@historical_bp.route('/seasonal', methods=['GET'])
def get_seasonal_insights():
    months = [
        {"month": 1, "month_name": "Jan", "aqi": 45.0, "risk_label": "Good", "color": "#22c55e", "season": "Cool Season", "driver": "Monsoon ventilation", "characteristic": "Generally clean", "tip": "Enjoy outdoor activities!"},
        {"month": 2, "month_name": "Feb", "aqi": 55.0, "risk_label": "Moderate", "color": "#eab308", "season": "Dry Season Start", "driver": "Reduced rain", "characteristic": "Slightly hazy", "tip": "Watch for short haze spikes."},
        {"month": 3, "month_name": "Mar", "aqi": 65.0, "risk_label": "Moderate", "color": "#eab308", "season": "Dry Season", "driver": "Hot & Dry", "characteristic": "Occasional haze", "tip": "Stay hydrated and check daily AQI."},
        {"month": 4, "month_name": "Apr", "aqi": 75.0, "risk_label": "Moderate", "color": "#eab308", "season": "Inter-monsoon", "driver": "Calm winds", "characteristic": "Trapped pollutants", "tip": "Exercise early in the morning."},
        {"month": 5, "month_name": "May", "aqi": 85.0, "risk_label": "Unhealthy", "color": "#f97316", "season": "Haze Season (Peak)", "driver": "Peak biomass burning", "characteristic": "Highest annual PM2.5", "tip": "Use air purifiers; keep windows closed."},
        {"month": 6, "month_name": "Jun", "aqi": 80.0, "risk_label": "Moderate", "color": "#eab308", "season": "Dry Season", "driver": "Biomass burning", "characteristic": "Smoky conditions", "tip": "Wear N95 masks outdoors."},
        {"month": 7, "month_name": "Jul", "aqi": 40.0, "risk_label": "Good", "color": "#22c55e", "season": "Monsoon Shift", "driver": "Rainy days", "characteristic": "Safest month", "tip": "Best time for nature walks."},
        {"month": 8, "month_name": "Aug", "aqi": 50.0, "risk_label": "Good", "color": "#22c55e", "season": "Wet Season", "driver": "Frequent storms", "characteristic": "Good ventilation", "tip": "Cleanest air during monsoon peaks."},
        {"month": 9, "month_name": "Sep", "aqi": 70.0, "risk_label": "Moderate", "color": "#eab308", "season": "Monsoon End", "driver": "Dry spells", "characteristic": "Unpredictable haze", "tip": "Stay flexible with plans."},
        {"month": 10, "month_name": "Oct", "aqi": 60.0, "risk_label": "Moderate", "color": "#eab308", "season": "Monsoon Return", "driver": "Rainy weather", "characteristic": "Washed air", "tip": "Good overall air quality."},
        {"month": 11, "month_name": "Nov", "aqi": 48.0, "risk_label": "Good", "color": "#22c55e", "season": "Wet Season", "driver": "Heavy rain", "characteristic": "Very clean", "tip": "Rain clears pollutants effectively."},
        {"month": 12, "month_name": "Dec", "aqi": 42.0, "risk_label": "Good", "color": "#22c55e", "season": "Cool Season", "driver": "Strong ventilation", "characteristic": "Pristine air", "tip": "Ideal for holiday outings."}
    ]
    return jsonify({
        "success": True,
        "data": {
            "months": months,
            "peak_month": "May",
            "safest_month": "Jul"
        }
    })
