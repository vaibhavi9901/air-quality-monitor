import { useSelector } from "react-redux";
import { useGetAirPollutionForecastQuery } from "../../services/AirQualityAPI";
import { HiCalendar } from "react-icons/hi";
import { getAqiTheme, API_STANDARDS } from "../../lib/aqi";

// Convert 0-500 US AQI → 1-5 scale for getAqiTheme compatibility
function toScale5(aqi) {
  if (!Number.isFinite(Number(aqi))) return null;
  if (aqi <= 50)  return 1;
  if (aqi <= 100) return 2;
  if (aqi <= 200) return 3;
  if (aqi <= 300) return 4;
  return 5;
}

// Parse ISO time string "2026-03-14T15:00" into a Date object
function parseISOHour(timeStr) {
  if (!timeStr) return null;
  try { return new Date(timeStr); } catch { return null; }
}

function cityFromLocation(loc) {
  if (!loc || typeof loc !== "string") return "Kuala Lumpur";
  const part = loc.split(",")[0]?.trim();
  return part || "Kuala Lumpur";
}

function PollutionForecast() {
  const location = useSelector((state) => state.search.location);
  const city     = cityFromLocation(location);
  const { data, isSuccess } = useGetAirPollutionForecastQuery(
    { city },
    { refetchOnMountOrArgChange: true }
  );

  // NEW response shape: data.data.hourly — array of 24 hourly points
  // Each point: { hour, time, aqi, pm25, label, color, icon }
  const hourly = isSuccess ? (data?.data?.hourly ?? []) : [];

  // Pick one reading per "day" — take the noon-ish hour (12:00) for each future day
  const getDailyForecast = () => {
    if (!hourly.length) return [];
    const seen = new Set();
    const daily = [];
    for (const point of hourly) {
      const d = parseISOHour(point.time);
      if (!d) continue;
      const dateKey = d.toISOString().slice(0, 10); // "2026-03-14"
      const today   = new Date().toISOString().slice(0, 10);
      if (dateKey === today) continue;             // skip today
      if (!seen.has(dateKey)) {
        seen.add(dateKey);
        daily.push({ ...point, date: d });
        if (daily.length === 3) break;
      }
    }
    return daily;
  };

  const forecastData = getDailyForecast();

  return (
    <div className="relative flex h-full w-full flex-col gap-6 rounded-[2.5rem] bg-white p-8 shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative z-10 flex items-center justify-center gap-3">
        <div className="bg-emerald-100 p-2 rounded-xl dark:bg-emerald-900/30">
          <HiCalendar className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Air Quality Forecast
        </h2>
      </div>

      <div className="relative z-10 grid grid-cols-1 gap-4 md:grid-cols-3 flex-none items-stretch">
        {isSuccess && forecastData.length > 0 ? (
          forecastData.map((item, index) => {
            const aqiTheme = getAqiTheme(toScale5(item.aqi));
            return (
              <div key={index} className="group relative flex flex-col items-center justify-center rounded-[2.5rem] bg-white p-5 border-2 border-slate-300 shadow-lg dark:bg-neutral-950 dark:border-neutral-700">
                <div className="text-sm font-bold text-slate-500 uppercase tracking-[0.2em]">
                  {item.date?.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}
                </div>
                <div className="mt-1 text-5xl font-black text-slate-900 dark:text-white leading-none">
                  AQI {Math.round(item.aqi)}
                </div>
                <div className="mt-2 text-xl font-black text-slate-700 dark:text-slate-300">{aqiTheme.level}</div>
                <div className={`mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20 cursor-pointer hover:scale-[1.02] transition-transform ${aqiTheme.badgeClass}`}>
                  {aqiTheme.label}
                </div>

                {/* Tooltip */}
                <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                  <div className="h-full w-full rounded-[2.5rem] bg-slate-900/95 p-3 flex flex-col items-center justify-center text-white shadow-2xl backdrop-blur-sm border-2 border-emerald-500/30">
                    <p className="text-[11px] font-black text-emerald-400 mb-2 tracking-widest uppercase">AQI Standards</p>
                    <div className="w-full space-y-1">
                      {API_STANDARDS.map((s) => (
                        <div key={s.level} className="flex justify-between items-center text-[11px] font-bold border-b border-white/10 pb-0.5 last:border-0">
                          <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white/70"}>{s.range}</span>
                          <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white"}>{s.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-3 text-sm font-bold text-slate-400">{aqiTheme.motivation}</div>
              </div>
            );
          })
        ) : (
          <div className="col-span-3 py-10 text-center text-gray-400 font-bold">
            Fetching forecast data…
          </div>
        )}
      </div>
    </div>
  );
}

export default PollutionForecast;

// import { useSelector } from "react-redux";
// import { useGetAirPollutionForecastQuery } from "../../services/AirQualityAPI";
// import { HiCalendar } from "react-icons/hi";
// import { getAqiTheme, API_STANDARDS, WIND_STANDARDS } from "../../lib/aqi";

// function getWindLevel(speed) {
//   if (speed === null) return "Level 0";
//   if (speed < 1.5) return "Level 1";
//   if (speed < 3.3) return "Level 2";
//   if (speed < 5.5) return "Level 3";
//   if (speed < 8.0) return "Level 4";
//   return "Level 5";
// }

// function PollutionForecast() {
//   const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
//   const { data, isSuccess } = useGetAirPollutionForecastQuery({
//     lat,
//     lng,
//   });

//   // Get next 3 days (roughly every 24th item as data is hourly)
//   const getDailyForecast = () => {
//     if (!isSuccess || !data.list) return [];
    
//     const daily = [];
//     // Skip today (index 0) and take next 3 days
//     for (let i = 24; i < data.list.length; i += 24) {
//       if (daily.length < 3) {
//         daily.push(data.list[i]);
//       }
//     }
//     return daily;
//   };

//   const forecastData = getDailyForecast();

//   return (
//     <div className="relative flex h-full w-full flex-col gap-6 rounded-[2.5rem] bg-white p-8 shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
//       <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />
      
//       <div className="relative z-10 flex items-center justify-center gap-3">
//         <div className="bg-emerald-100 p-2 rounded-xl dark:bg-emerald-900/30">
//           <HiCalendar className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
//         </div>
//         <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
//           Air Quality Forecast
//         </h2>
//       </div>

//       <div className="relative z-10 grid grid-cols-1 gap-4 md:grid-cols-3 flex-none items-stretch">
//         {isSuccess && forecastData.length > 0 ? (
//           forecastData.map((item, index) => {
//             const date = new Date(item.dt * 1000);
//             const aqi = item.main.aqi;
//             const aqiTheme = getAqiTheme(aqi);
//             return (            
//               <div
//                 key={index}
//                 className="group relative flex flex-col items-center justify-center rounded-[2.5rem] bg-white p-5 border-2 border-slate-300 shadow-lg dark:bg-neutral-950 dark:border-neutral-700"
//               >
//                 <div className="text-sm font-bold text-slate-500 uppercase tracking-[0.2em]">
//                   {date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}
//                 </div>
//                 <div className="mt-1 text-5xl font-black text-slate-900 dark:text-white leading-none">
//                   API {aqi}
//                 </div>
//                 <div className="mt-2 text-xl font-black text-slate-700 dark:text-slate-300">{aqiTheme.level}</div>
                
//                 <div className={`mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20 cursor-pointer hover:scale-[1.02] transition-transform ${aqiTheme.badgeClass}`}>
//                   {aqiTheme.label}
//                 </div>

//                 {/* Custom Instant Tooltip - Standard List */}
//                 <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
//                   <div className="h-full w-full rounded-[2.5rem] bg-slate-900/95 p-3 flex flex-col items-center justify-center text-white shadow-2xl backdrop-blur-sm border-2 border-emerald-500/30">
//                     <p className="text-[11px] font-black text-emerald-400 mb-2 tracking-widest uppercase">API Standards</p>
//                     <div className="w-full space-y-1">
//                       {API_STANDARDS.map((s) => (
//                         <div key={s.level} className="flex justify-between items-center text-[11px] font-bold border-b border-white/10 pb-0.5 last:border-0">
//                           <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white/70"}>{s.range}</span>
//                           <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white"}>{s.label}</span>
//                         </div>
//                       ))}
//                     </div>
//                   </div>
//                 </div>

//                 <div className="mt-3 text-sm font-bold text-slate-400">
//                   {aqiTheme.motivation}
//                 </div>
//               </div>
//             );
//           })
//         ) : (
//           <div className="col-span-3 py-10 text-center text-gray-400 font-bold">
//             Fetching forecast data...
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default PollutionForecast;
