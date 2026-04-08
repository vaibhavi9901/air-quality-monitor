import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// VITE_API_URL must end with /api (e.g. https://your-backend.onrender.com/api)
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export const airQualityApi = createApi({
  reducerPath: "airQualityApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  endpoints: (builder) => ({

    // Real-time AQI + alert by GPS coordinates
    // Response: { data: { aqi, pollutants:{pm25,pm10}, risk:{label,color,guidance}, alert:{active,message}, timestamp } }
    getCurrentAirPollution: builder.query({
      query: ({ lat, lng }) => `/air-quality/geo?lat=${lat}&lon=${lng}`,
    }),

    // Same shape as above, by city name (fallback when geo fails or is delayed)
    getCurrentAirPollutionByCity: builder.query({
      query: ({ city }) => `/air-quality/city/${encodeURIComponent(city || "Kuala Lumpur")}`,
    }),

    // Alert evaluation by city
    getAirQuality: builder.query({
      query: ({ city }) => `/alerts/check/city/${encodeURIComponent(city || "Kuala Lumpur")}`,
    }),

    // 24-hour hourly forecast — requires city name from Redux state.search.location
    // Response: { data: { city, hourly:[{hour,time,aqi,pm25,label,color,icon}], max_aqi,min_aqi,avg_aqi,peak_hour } }
    getAirPollutionForecast: builder.query({
      query: ({ city }) =>
        `/forecast/${encodeURIComponent(city || "Kuala Lumpur")}/summary`,
    }),

    // Multi-year seasonal historical insights
    // Response: { data: { months:[{month,month_name,aqi,risk_label,color,season,tip}] } }
    getSeasonalInsights: builder.query({
      query: () => `/historical/seasonal`,
    }),

    // Station markers for the map
    getAirQualityMap: builder.query({
      query: () => `/air-quality/stations`,
    }),

  }),
});

export const {
  useGetAirQualityQuery,
  useGetCurrentAirPollutionQuery,
  useGetCurrentAirPollutionByCityQuery,
  useGetAirPollutionForecastQuery,
  useGetSeasonalInsightsQuery,
  useGetAirQualityMapQuery,
} = airQualityApi;

// import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// import mockAirPollutionCurrent from "../mocks/openWeatherAirPollution.current.json";
// import mockAirPollutionForecast from "../mocks/openWeatherAirPollution.forecast.json";

// const APIKey = import.meta.env.VITE_API_KEY_OPENWEATHERMAP;
// const USE_MOCK =
//   String(import.meta.env.VITE_USE_MOCK).toLowerCase() === "true" || !APIKey;

// const rawBaseQuery = fetchBaseQuery({
//   baseUrl: "https://pro.openweathermap.org",
// });

// const mockWeatherCurrent = {
//   wind: { speed: 2.6, deg: 140 },
// };

// const baseQuery = async (args, api, extraOptions) => {
//   if (!USE_MOCK) return rawBaseQuery(args, api, extraOptions);

//   const url = typeof args === "string" ? args : args?.url ?? "";

//   if (url.includes("data/2.5/air_pollution/forecast")) {
//     return { data: mockAirPollutionForecast };
//   }
//   if (url.includes("data/2.5/air_pollution")) {
//     return { data: mockAirPollutionCurrent };
//   }
//   if (url.includes("data/2.5/weather")) {
//     return { data: mockWeatherCurrent };
//   }

//   return { error: { status: 404, data: { message: "Mock route not found" } } };
// };

// export const airQualityApi = createApi({
//   reducerPath: "airQualityApi",
//   baseQuery,
//   endpoints: (builder) => ({
//     getAirQuality: builder.query({
//       query: ({ lat, lng }) =>
//         `data/2.5/weather?lat=${lat}&lon=${lng}&units=metric&appid=${APIKey}`,
//     }),
//     getCurrentAirPollution: builder.query({
//       query: ({ lat, lng }) =>
//         `data/2.5/air_pollution?lat=${lat}&lon=${lng}&appid=${APIKey}`,
//     }),
//     getAirPollutionForecast: builder.query({
//       query: ({ lat, lng }) =>
//         `data/2.5/air_pollution/forecast?lat=${lat}&lon=${lng}&appid=${APIKey}`,
//     }),
//     getAirQualityMap: builder.query({
//       query: ({ lat, lng }) =>
//         `maps/2.0/weather/PA0/2/${lat}/${lng}.png?appid=${APIKey}`,
//     }),
//   }),
// });

// export const {
//   useGetAirQualityQuery,
//   useGetCurrentAirPollutionQuery,
//   useGetAirPollutionForecastQuery,
//   useGetAirQualityMapQuery,
// } = airQualityApi;
