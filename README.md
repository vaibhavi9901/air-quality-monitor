# Air We Go ✨

**Air We Go** is a modern air quality monitoring assistant designed specifically for elderly urban residents in Malaysia. As air pollution remains a persistent public health concern in Malaysia’s urban areas (particularly during haze seasons), we aim to provide data-driven support to help vulnerable populations protect their health and maintain a safe, active lifestyle.

## Problem Statement

Air pollution remains a persistent public health concern in Malaysia’s urban areas, particularly during haze seasons. Elderly urban residents are especially vulnerable to respiratory and cardiovascular illnesses due to pre-existing conditions and increased age-related susceptibility. Despite this heightened risk, many continue engaging in outdoor activities such as morning walks, social gatherings, or running errands, often unaware of daily fluctuations in air quality and the associated health impacts.

## Solution

**Air We Go** supports elderly urban residents in proactively reducing their exposure to air pollution through:
* **Identifying High-Exposure Periods**: Real-time monitoring to pinpoint risky times of the day.
* **Estimating Health Risks**: Assessing relative risks based on susceptibility factors.
* **Providing Timely Guidance**: Practical and actionable advice for safe daily activity planning.

## Key Features

* **Elderly-Friendly Interface**: Large fonts and high contrast for readability under Malaysia's bright sunlight.
* **Haze Season Optimization**: Deep data analysis tailored to Malaysia's common haze conditions.
* **Health Risk Alerts**: Special focus on respiratory and cardiovascular preventative measures.
* **10-Day Forecast**: Plan safe morning walks and outdoor social gatherings in advance.
* **Interactive Maps**: Visualize pollution patterns in local urban areas.

## Tech Stack

### Frontend
* **React** + **Vite**
* **Tailwind CSS** (Styling)
* **Redux Toolkit** (State Management)
* **Headless UI** (Accessible Components)
* **Chart.js** (Data Visualization)
* **Leaflet** (Maps)

### APIs
* **OpenWeather API**: Core weather data and map layers.
* **Google Places API**: Location search and autocomplete for Malaysia.
* **OpenMeteo API**: UV Index data.
* **Stadia Maps API**: Custom map tiles.

## Getting Started

### 1. Backend Setup (Flask)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The backend will run on `http://localhost:5000`.

### 2. Frontend Setup (React)
Open a new terminal and run:
```bash
npm install
npm run dev
```
The frontend will run on `http://localhost:5173`.

## Environment Configuration
- **Backend**: Add your `WAQI_API_TOKEN` to `backend/.env` for real-time data.
- **Frontend**: The app is pre-configured to point to the local backend at `http://127.0.0.1:5000/api`.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
