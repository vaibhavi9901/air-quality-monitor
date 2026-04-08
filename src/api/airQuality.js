import axios from "axios";
import BASE_URL from "./config";

const api = axios.create({ baseURL: BASE_URL });

// Real-time AQI for a city name
export const fetchAQIByCity = (city) =>
  api.get(`/air-quality/city/${encodeURIComponent(city)}`);

// Real-time AQI by GPS coordinates (browser geolocation)
export const fetchAQIByCoords = (lat, lon) =>
  api.get(`/air-quality/geo?lat=${lat}&lon=${lon}`);

// Alert status for a city
export const fetchAlert = (city) =>
  api.get(`/alerts/check/city/${encodeURIComponent(city)}`);

// Alert status by GPS
export const fetchAlertByCoords = (lat, lon) =>
  api.get(`/alerts/check/geo?lat=${lat}&lon=${lon}`);

// 24-hour forecast summary
export const fetchForecast = (city) =>
  api.get(`/forecast/${encodeURIComponent(city)}/summary`);

// Historical seasonal data (grouped by year)
export const fetchHistorical = (city, lat, lon, years = 3) =>
  api.get(`/historical/seasonal?city=${encodeURIComponent(city)}&lat=${lat}&lon=${lon}&years=${years}`);

// Popular Malaysian monitoring stations
export const fetchStations = () =>
  api.get(`/air-quality/stations`);