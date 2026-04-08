import { useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import { useGetAirPollutionForecastQuery } from "../../services/AirQualityAPI";
import { CalendarDaysIcon } from "@heroicons/react/24/outline";
import { getAqiTheme } from "../../lib/aqi";
import Chart from "chart.js/auto";

function toScale5(aqi) {
  if (!Number.isFinite(Number(aqi))) return null;
  if (aqi <= 50)  return 1;
  if (aqi <= 100) return 2;
  if (aqi <= 200) return 3;
  if (aqi <= 300) return 4;
  return 5;
}

function formatDayLabel(date) {
  return date.toLocaleDateString("en-MY", { weekday: "long", month: "short", day: "numeric" });
}
function formatTimeLabel(date) {
  return date.toLocaleTimeString("en-MY", { hour: "2-digit", minute: "2-digit" });
}
function averageRounded(values) {
  if (!values.length) return null;
  return Math.round(values.reduce((a, b) => a + b, 0) / values.length);
}
function aqiToHex(aqi) {
  if (aqi <= 50)  return "#22c55e";
  if (aqi <= 100) return "#eab308";
  if (aqi <= 200) return "#f97316";
  if (aqi <= 300) return "#ef4444";
  return "#7c3aed";
}

function cityFromLocation(loc) {
  if (!loc || typeof loc !== "string") return "Kuala Lumpur";
  const part = loc.split(",")[0]?.trim();
  return part || "Kuala Lumpur";
}

function NextDayForecastCard() {
  const location = useSelector((state) => state.search.location);
  const city     = cityFromLocation(location);
  const { data, isSuccess } = useGetAirPollutionForecastQuery(
    { city },
    { refetchOnMountOrArgChange: true }
  );

  const chartRef     = useRef(null);
  const chartInstance = useRef(null);

  const hourly = isSuccess ? (data?.data?.hourly ?? []) : [];

  // Tomorrow date range
  const now           = new Date();
  const tomorrowStart = new Date(now);
  tomorrowStart.setDate(now.getDate() + 1);
  tomorrowStart.setHours(0, 0, 0, 0);
  const tomorrowEnd = new Date(tomorrowStart);
  tomorrowEnd.setDate(tomorrowStart.getDate() + 1);
  const tomorrowLabel = formatDayLabel(tomorrowStart);

  const itemsTomorrow = hourly.filter((pt) => {
    if (!pt.time) return false;
    const t = new Date(pt.time).getTime();
    return t >= tomorrowStart.getTime() && t < tomorrowEnd.getTime();
  });

  // Fall back to all 24 hours if tomorrow has no data yet
  const chartPoints = itemsTomorrow.length >= 4 ? itemsTomorrow : hourly.slice(0, 24);

  const aqiValues    = itemsTomorrow.map((pt) => pt.aqi).filter(Number.isFinite);
  const predictedAqi = averageRounded(aqiValues) ?? (hourly[0]?.aqi ?? null);
  const aqiTheme     = getAqiTheme(toScale5(predictedAqi));

  const bestItem = chartPoints.reduce((best, pt) => {
    if (!Number.isFinite(pt.aqi)) return best;
    if (!best) return pt;
    return pt.aqi < best.aqi ? pt : best;
  }, null);
  const bestTime  = bestItem?.time ? formatTimeLabel(new Date(bestItem.time)) : null;
  const bestAqi   = bestItem?.aqi ?? null;
  const bestTheme = getAqiTheme(toScale5(bestAqi ?? predictedAqi));

  const guidance = (() => {
    const aqi = Number(predictedAqi);
    if (!Number.isFinite(aqi)) return "Forecast is not available yet. Please try again in a moment.";
    if (aqi <= 50)  return "Likely safe for a short walk. Choose a cleaner hour and avoid heavy-traffic roads.";
    if (aqi <= 100) return "Mostly safe. Keep walks short and check conditions before heading out.";
    if (aqi <= 200) return "Higher risk. Reduce outdoor time and avoid heavy-traffic roads if possible.";
    if (aqi <= 300) return "Very high risk. Prefer indoor activities and postpone non-urgent trips.";
    return "Hazardous. Avoid outdoor exposure except emergencies.";
  })();

  const samplesLabel = itemsTomorrow.length
    ? `${itemsTomorrow.length} hourly samples`
    : "Showing next available 24 hours";

  const dotClass = (theme) =>
    theme.label === "Hazardous" ? "bg-violet-600"
    : theme.label === "Very Unhealthy" ? "bg-red-500"
    : theme.label === "Unhealthy" ? "bg-orange-500"
    : theme.label === "Moderate" ? "bg-yellow-500"
    : "bg-emerald-600";

  // Build / update chart
  useEffect(() => {
    if (!chartRef.current || !chartPoints.length) return;

    const labels = chartPoints.map((pt) => {
      if (!pt.time) return `${pt.hour}:00`;
      const d = new Date(pt.time);
      return d.toLocaleTimeString("en-MY", { hour: "2-digit", minute: "2-digit" });
    });
    const values    = chartPoints.map((pt) => pt.aqi ?? 0);
    const bgColors  = values.map((v) => aqiToHex(v) + "cc");  // 80% opacity
    const brdColors = values.map((v) => aqiToHex(v));

    // Destroy previous instance
    if (chartInstance.current) {
      chartInstance.current.destroy();
      chartInstance.current = null;
    }

    chartInstance.current = new Chart(chartRef.current, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "AQI",
          data: values,
          backgroundColor: bgColors,
          borderColor: brdColors,
          borderWidth: 1.5,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const aqi = ctx.parsed.y;
                const theme = getAqiTheme(toScale5(aqi));
                return ` AQI ${Math.round(aqi)} — ${theme.label}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
              maxRotation: 45,
              autoSkip: true,
              maxTicksLimit: 12,
            },
          },
          y: {
            min: 0,
            suggestedMax: 200,
            grid: { color: "#e2e8f020" },
            ticks: {
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
              callback: (v) => `${v}`,
            },
            title: {
              display: true,
              text: "AQI",
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, [chartPoints.length, isSuccess]);

  return (
    <div className="relative h-[840px] w-full rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative h-full w-full p-4 text-xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
          <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
            <CalendarDaysIcon className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
          </div>
          <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
            24-Hour Air Quality Forecast
          </div>
        </div>

        <div className="relative z-10 mt-1 text-center text-base font-black text-slate-600 dark:text-slate-300 flex-none">
          {tomorrowLabel}
        </div>

        {/* ── Hourly bar chart ── */}
        {isSuccess && chartPoints.length > 0 ? (
          <div className="relative z-10 mt-3 flex-none rounded-[1.5rem] border-2 border-slate-200 bg-white/80 dark:bg-neutral-950 dark:border-neutral-800 p-3 shadow-sm" style={{ height: "160px" }}>
            <canvas ref={chartRef} />
          </div>
        ) : (
          <div className="mt-4 rounded-2xl bg-slate-50 p-6 text-center text-lg font-bold text-slate-500 dark:bg-neutral-950 dark:text-slate-400">
            Loading forecast chart…
          </div>
        )}

        {/* ── AQI summary + guidance ── */}
        <div className="relative z-10 mt-3 grid grid-cols-1 gap-3 flex-1 min-h-0 items-stretch">

          {/* Predicted AQI */}
          <div className="group relative flex flex-col items-center justify-center rounded-[2.5rem] bg-white p-4 border-2 border-slate-300 shadow-lg dark:bg-neutral-950 dark:border-neutral-700">
            <div className="text-sm font-bold text-slate-500 tracking-[0.2em]">Forecast AQI</div>
            <div
              className="mt-1 text-5xl font-black leading-none transition-colors duration-500"
              style={{ color: aqiTheme.color }}
            >
              {Number.isFinite(Number(predictedAqi)) ? Math.round(predictedAqi) : "—"}
            </div>
            <div className="mt-2 text-xl font-black text-slate-700 dark:text-slate-300">{aqiTheme.level}</div>
            <div className={["mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20", aqiTheme.badgeClass].join(" ")}>
              {aqiTheme.label}
            </div>
            <div className="mt-3 text-sm font-bold text-slate-400">{samplesLabel}</div>
          </div>

          {/* Planning guidance */}
          <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
            <div className="px-5 py-3 bg-gradient-to-r from-emerald-200 via-emerald-100 to-emerald-50 border-b border-emerald-300 dark:from-emerald-900/35 dark:via-emerald-900/20 dark:to-emerald-900/5 dark:border-emerald-900/30">
              <div className="text-lg font-black text-emerald-950 dark:text-emerald-50 tracking-wide text-center">
                Planning Guidance
              </div>
            </div>
            <div className="px-5 py-3">
              <div className="mx-auto w-full max-w-[34rem]">
                <div className="text-lg font-black text-slate-900 dark:text-white leading-relaxed text-left">
                  {guidance}
                </div>
                <div className="mt-3 flex flex-col gap-3">
                  <div className="flex items-start gap-3">
                    <div className={`mt-2 h-3 w-3 rounded-full ${dotClass(bestTheme)}`} />
                    <div className="text-lg font-bold text-slate-600 dark:text-slate-300 text-left leading-relaxed">
                      {bestTime && Number.isFinite(Number(bestAqi))
                        ? `Cleanest hour: ${bestTime} (AQI ${Math.round(bestAqi)}).`
                        : "Cleaner-hour suggestion will appear when more data is available."}
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="mt-2 h-3 w-3 rounded-full bg-slate-400 dark:bg-slate-500" />
                    <div className="text-lg font-bold text-slate-600 dark:text-slate-300 text-left leading-relaxed">
                      Keep a backup plan: indoor walking, shopping earlier, and mask ready if air feels irritating.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default NextDayForecastCard;

////SWAN'S VERSION 


// import { useSelector } from "react-redux";
// import { useGetAirPollutionForecastQuery } from "../../services/AirQualityAPI";
// import { CalendarDaysIcon } from "@heroicons/react/24/outline";
// import { getAqiTheme } from "../../lib/aqi";

// function formatDayLabel(date) {
//   return date.toLocaleDateString("en-MY", {
//     weekday: "long",
//     month: "short",
//     day: "numeric",
//   });
// }

// function formatTimeLabel(date) {
//   return date.toLocaleTimeString("en-MY", { hour: "2-digit", minute: "2-digit" });
// }

// function getTomorrowRange() {
//   const now = new Date();
//   const start = new Date(now);
//   start.setDate(now.getDate() + 1);
//   start.setHours(0, 0, 0, 0);
//   const end = new Date(start);
//   end.setDate(start.getDate() + 1);
//   return { start, end };
// }

// function averageRounded(values) {
//   if (!values.length) return null;
//   const sum = values.reduce((a, b) => a + b, 0);
//   return Math.round(sum / values.length);
// }

// function NextDayForecastCard() {
//   const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
//   const { data, isSuccess } = useGetAirPollutionForecastQuery({ lat, lng });

//   const { start: tomorrowStart, end: tomorrowEnd } = getTomorrowRange();
//   const tomorrowLabel = formatDayLabel(tomorrowStart);

//   const itemsTomorrow = isSuccess
//     ? (data?.list ?? []).filter((x) => {
//         const t = (x?.dt ?? 0) * 1000;
//         return t >= tomorrowStart.getTime() && t < tomorrowEnd.getTime();
//       })
//     : [];

//   const aqiValues = itemsTomorrow
//     .map((x) => Number(x?.main?.aqi))
//     .filter((n) => Number.isFinite(n));

//   const fallbackItem = isSuccess ? data?.list?.[24] ?? data?.list?.[0] ?? null : null;
//   const predictedAqi = averageRounded(aqiValues) ?? Number(fallbackItem?.main?.aqi) ?? null;
//   const aqiTheme = getAqiTheme(predictedAqi);

//   const bestItem = (() => {
//     if (!itemsTomorrow.length) return null;
//     let best = null;
//     for (const item of itemsTomorrow) {
//       const aqi = Number(item?.main?.aqi);
//       if (!Number.isFinite(aqi)) continue;
//       if (!best) best = item;
//       else if (aqi < Number(best?.main?.aqi)) best = item;
//       else if (aqi === Number(best?.main?.aqi) && (item?.dt ?? 0) < (best?.dt ?? 0)) best = item;
//     }
//     return best;
//   })();

//   const bestTime = bestItem ? formatTimeLabel(new Date(bestItem.dt * 1000)) : null;
//   const bestAqi = bestItem ? Number(bestItem?.main?.aqi) : null;
//   const bestTheme = getAqiTheme(bestAqi ?? predictedAqi);

//   const guidance = (() => {
//     const aqi = Number(predictedAqi);
//     if (!Number.isFinite(aqi)) {
//       return "Forecast is not available yet. Please try again in a moment.";
//     }
//     if (aqi <= 2) return "Likely safe for a short walk. Choose a cleaner hour and avoid heavy-traffic roads.";
//     if (aqi === 3) return "Use caution. Keep walks short and prefer indoor alternatives if you feel discomfort.";
//     if (aqi === 4) return "High risk. Plan indoor activities and postpone outdoor errands if possible.";
//     return "Very high risk. Avoid outdoor exposure except emergencies.";
//   })();

//   const samplesLabel = itemsTomorrow.length ? `${itemsTomorrow.length} hourly samples` : "Limited forecast samples";

//   return (
//     <div className="relative h-full w-full rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
//       <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

//       <div className="relative h-full w-full p-6 text-xl flex flex-col overflow-hidden">
//         <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
//           <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
//             <CalendarDaysIcon className="h-7 w-7 text-emerald-800 dark:text-emerald-400" />
//           </div>
//           <div className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
//             The Next Day
//           </div>
//         </div>

//         <div className="relative z-10 mt-3 flex-1 flex flex-col gap-4 overflow-hidden">
//           <div className="flex items-center justify-center flex-none">
//             <div className="text-lg font-black text-slate-600 dark:text-slate-300 tracking-wide">
//               {tomorrowLabel}
//             </div>
//           </div>

//           <div className="grid grid-cols-1 gap-4 md:grid-cols-2 flex-none items-stretch">
//             <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
//               <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
//                 <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
//                   Predicted Air Quality
//                 </div>
//               </div>
//               <div className="px-5 py-5 flex flex-col items-center justify-center">
//                 <div className="text-5xl font-black text-slate-900 dark:text-white leading-none">
//                   {Number.isFinite(Number(predictedAqi)) ? `API ${predictedAqi}` : "—"}
//                 </div>
//                 <div
//                   className={[
//                     "mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20",
//                     aqiTheme.badgeClass,
//                   ].join(" ")}
//                 >
//                   {aqiTheme.label}
//                 </div>
//                 <div className="mt-3 text-sm font-bold text-slate-500 dark:text-slate-400 text-center">
//                   {samplesLabel}
//                 </div>
//               </div>
//             </div>

//             <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
//               <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
//                 <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
//                   Planning Guidance
//                 </div>
//               </div>
//               <div className="px-5 py-5">
//                 <div className="text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed">
//                   {guidance}
//                 </div>

//                 <div className="mt-4 flex flex-col gap-3">
//                   <div className="flex items-start gap-3">
//                     <div className={`mt-2 h-3 w-3 rounded-full ${bestTheme.label === "Very Poor" ? "bg-violet-600" : bestTheme.label === "Poor" ? "bg-rose-600" : bestTheme.label === "Moderate" ? "bg-amber-600" : bestTheme.label === "Fair" ? "bg-teal-600" : "bg-emerald-600"}`} />
//                     <div className="text-base font-bold text-slate-600 dark:text-slate-300">
//                       {bestTime && Number.isFinite(Number(bestAqi))
//                         ? `Cleaner hour likely around ${bestTime} (API ${bestAqi}).`
//                         : "Cleaner-hour suggestion will appear when more forecast data is available."}
//                     </div>
//                   </div>
//                   <div className="flex items-start gap-3">
//                     <div className="mt-2 h-3 w-3 rounded-full bg-slate-400 dark:bg-slate-500" />
//                     <div className="text-base font-bold text-slate-600 dark:text-slate-300">
//                       Keep a backup plan: indoor walking, shopping earlier, and mask ready if air feels irritating.
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default NextDayForecastCard;
