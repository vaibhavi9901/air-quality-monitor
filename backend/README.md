# 🌬️ Air We Go — Backend (Flask)

This is the Python/Flask backend for the Air We Go air quality monitoring assistant.

## Quick Start

### 1. Set up Python Environment
Make sure you have Python installed. Then, run:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` and add your `WAQI_API_TOKEN` if you have one. If not, it will use mock data.
Get a free token here: https://aqicn.org/api/

### 3. Run the Backend
```bash
python app.py
```
The backend will run at http://localhost:5000.

## API Endpoints
- Real-time AQI: `GET /api/air-quality/city/<city>`
- Real-time Geo: `GET /api/air-quality/geo?lat=&lon=`
- Alert Check: `GET /api/alerts/check/city/<city>`
- 24h Forecast: `GET /api/forecast/<city>/summary`
- Seasonal Insights: `GET /api/historical/seasonal`
- Station Map: `GET /api/air-quality/stations`
