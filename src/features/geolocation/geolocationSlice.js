import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  geolocation: { lat: 3.1390, lng: 101.6869 }, // Default: Kuala Lumpur, Malaysia
};

const geolocationSlice = createSlice({
  name: "geolocation",
  initialState,
  reducers: {
    saveGeoCode: (state, action) => {
      return { ...state, geolocation: action.payload };
    },
  },
});

export const { saveGeoCode } = geolocationSlice.actions;
export default geolocationSlice;
