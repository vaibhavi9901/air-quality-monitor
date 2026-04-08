import React, { useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapPinIcon } from "@heroicons/react/24/outline";
import { useGetAirQualityMapQuery } from "../../services/AirQualityAPI";

// Colour a marker based on AQI (0-500)
function aqiToColour(aqi) {
  if (!Number.isFinite(Number(aqi))) return "#9ca3af";
  if (aqi <= 50)  return "#22c55e";
  if (aqi <= 100) return "#eab308";
  if (aqi <= 200) return "#f97316";
  if (aqi <= 300) return "#ef4444";
  return "#7c3aed";
}

function makeIcon({ color, label }) {
  const safeLabel = label ?? "—";
  return L.divIcon({
    className: "",
    html: `<div style="min-width:34px;height:34px;border-radius:9999px;background:${color};border:3px solid #ffffff;box-shadow:0 6px 14px rgba(15,23,42,.22);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:14px;letter-spacing:-0.02em;color:#0f172a;line-height:1;padding:0 8px;">
      ${safeLabel}
    </div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

function AirQualityMap() {
  const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
  const mapRef       = useRef(null);
  const mapInstance  = useRef(null);

  // Fetch Malaysian station data from our backend
  const { data: stationsData, isSuccess: stationsLoaded } = useGetAirQualityMapQuery();

  // Initialise map once
  useEffect(() => {
    if (mapInstance.current) return;   // already initialised

    const map = L.map(mapRef.current, {
      center: [lat || 3.139, lng || 101.687],
      zoom: 10,
      layers: [
        L.tileLayer(
          "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
          {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
          }
        ),
      ],
    });

    map.attributionControl.setPrefix("Air We Go");
    map.zoomControl.remove();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();

    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);   // run once only

  // Add / update station markers when data arrives
  useEffect(() => {
    const map = mapInstance.current;
    if (!map || !stationsLoaded) return;

    const stations = stationsData?.data ?? [];
    stations.forEach((station) => {
      if (!Number.isFinite(station.lat) || !Number.isFinite(station.lon)) return;

      const aqi = Number.isFinite(Number(station.aqi)) ? Math.round(Number(station.aqi)) : null;
      const colour = aqiToColour(aqi);
      const marker = L.marker([station.lat, station.lon], { icon: makeIcon({ color: colour, label: aqi == null ? "—" : String(aqi) }) });
      
      // 针对老年人优化的弹出层内容：更大、更直观
      const popupContent = `
        <div style="font-family: sans-serif; padding: 4px; min-width: 140px;">
          <div style="font-size: 1.2rem; font-weight: 900; color: #1e293b; margin-bottom: 4px;">${station.city}</div>
          <div style="display: flex; items-center; gap: 8px; margin-bottom: 8px;">
            <span style="font-size: 2rem;">${station.icon || '📍'}</span>
            <div>
              <div style="font-size: 1.5rem; font-weight: 900; color: ${colour}; line-height: 1;">${Math.round(station.aqi)}</div>
              <div style="font-size: 0.875rem; font-weight: 700; color: ${colour}; text-transform: uppercase;">${station.risk_label || station.risk}</div>
            </div>
          </div>
          <div style="font-size: 0.95rem; font-weight: 600; line-height: 1.4; color: #475569; border-top: 1px solid #e2e8f0; pt: 8px;">
            ${station.guidance || 'Stay safe!'}
          </div>
        </div>
      `;

      marker.bindPopup(popupContent, { maxWidth: 220 });
      marker.addTo(map);
    });
  }, [stationsLoaded, stationsData]);

  // Pan to user location when it changes
  useEffect(() => {
    const map = mapInstance.current;
    if (!map || !lat || !lng) return;
    map.setView([lat, lng], map.getZoom());
  }, [lat, lng]);

  return (
    <div className="relative flex h-[620px] w-full max-w-full mx-auto flex-col gap-4 overflow-hidden rounded-[2.5rem] bg-white p-6 shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative z-10 flex items-center justify-center gap-3">
        <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
          <MapPinIcon className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
        </div>
        <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
          Air Quality Map
        </div>
      </div>

      <div className="relative z-10 flex-1 min-h-0">
        <div
          ref={mapRef}
          className="z-0 h-full w-full rounded-3xl shadow-sm ring-1 ring-emerald-100/60 dark:ring-emerald-900/20 contrast-[1.15] saturate-[1.1]"
        />
      </div>
    </div>
  );
}

export default AirQualityMap;

// import React, { useEffect, useRef } from "react";
// import { useSelector } from "react-redux";
// import L from "leaflet";
// import "leaflet/dist/leaflet.css";
// import { MapPinIcon } from "@heroicons/react/24/outline";

// function AirQualityMap() {
//   const { lat, lng } = useSelector((state) => state.geolocation.geolocation);

//   const mapRef = useRef(null);

//   useEffect(() => {
//     const map = L.map(mapRef.current, {
//       center: [lat, lng],
//       zoom: 6,
//       layers: [
//         L.tileLayer(
//           "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
//         ),
//       ],
//     });
//     map.attributionControl.setPrefix("Air We Go");
//     map.zoomControl.remove();
//     map.touchZoom.disable();
//     map.doubleClickZoom.disable();
//     map.scrollWheelZoom.disable();
//     map.boxZoom.disable();
//     map.keyboard.disable();

//     // add air quality layer to map
//     const airQualityLayer = L.tileLayer(
//       "https://maps.openweathermap.org/maps/2.0/weather/{op}/{z}/{x}/{y}?appid={API_KEY}",
//       {
//         op: "PR0",
//         API_KEY: "06d993a12ed23f678bfb54004bb0ad42",
//         attribution: "© Air We Go",
//       }
//     );

//     airQualityLayer.addTo(map);

//     return () => {
//       map.remove();
//     };
//   }, [lat, lng]);

//   return (
//     <div className="relative flex h-full w-full flex-col gap-4 overflow-hidden rounded-[2.5rem] bg-white p-6 shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40">
//       <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />
      
//       <div className="relative z-10 flex items-center justify-center gap-3">
//         <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
//           <MapPinIcon className="h-7 w-7 text-emerald-800 dark:text-emerald-400" />
//         </div>
//         <div className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
//           Regional Air Quality Map
//         </div>
//       </div>

//       <div className="relative z-10 flex-1 min-h-0">
//         <div
//           ref={mapRef}
//           className="z-0 h-full w-full rounded-3xl shadow-sm dark:hue-rotate-180 dark:invert ring-1 ring-emerald-100/60 dark:ring-emerald-900/20"
//         />
//       </div>
//     </div>
//   );
// }

// export default AirQualityMap;
