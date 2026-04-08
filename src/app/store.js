import { configureStore } from "@reduxjs/toolkit";
import searchSlice from "../features/search/searchSlice";
import geolocationSlice from "../features/geolocation/geolocationSlice";
import { airQualityApi } from "../services/AirQualityAPI";

export const store = configureStore({
  reducer: {
    search: searchSlice.reducer,
    geolocation: geolocationSlice.reducer,
    [airQualityApi.reducerPath]: airQualityApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(airQualityApi.middleware),
});
