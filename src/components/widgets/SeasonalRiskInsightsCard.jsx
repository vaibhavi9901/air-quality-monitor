import { useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import { useGetSeasonalInsightsQuery } from "../../services/AirQualityAPI";
import { ChartBarSquareIcon } from "@heroicons/react/24/outline";
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

function aqiToHex(aqi) {
  if (aqi <= 50)  return "#22c55e";
  if (aqi <= 100) return "#eab308";
  if (aqi <= 200) return "#f97316";
  if (aqi <= 300) return "#ef4444";
  return "#7c3aed";
}

// One solid colour per year for the multi-year line chart
const YEAR_COLORS = ["#6366f1", "#f59e0b", "#10b981", "#ef4444", "#06b6d4"];

function getSeasonInsight(monthData) {
  if (!monthData) return {
    title: "Seasonal data loading…",
    summary: "Historical air quality patterns will appear here.",
    dotClass: "bg-slate-400",
  };
  const { season, tip, aqi } = monthData;
  const dotClass =
    aqi > 300 ? "bg-violet-600"
    : aqi > 200 ? "bg-red-500"
    : aqi > 100 ? "bg-orange-500"
    : aqi > 50  ? "bg-yellow-500"
    : "bg-emerald-600";
  return { title: season, summary: tip, dotClass };
}

const MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function SeasonalRiskInsightsCard() {
  const { lat, lng }  = useSelector((state) => state.geolocation.geolocation);
  const city          = useSelector((state) => state.search.location) || "Kuala Lumpur";

  const { data, isSuccess } = useGetSeasonalInsightsQuery({ city, lat, lng, years: 5 });

  const barChartRef  = useRef(null);   // monthly AQI colour-coded bars (latest year)
  const lineChartRef = useRef(null);   // multi-year overlay lines
  const barInstance  = useRef(null);
  const lineInstance = useRef(null);

  const insightsData = data?.data;

  const now          = new Date();
  const currentMonth = now.getMonth() + 1;

  const currentMonthData = insightsData?.months?.find((m) => m.month === currentMonth);
  const season           = getSeasonInsight(currentMonthData);

  // Year-over-year trend - Backend now returns a single array of months
  const trend = { label: "Historical Insights", detail: "Monthly air quality patterns based on historical data.", level: null };

  const trendTheme = getAqiTheme(toScale5(trend.level));
  const trendDotClass = "bg-emerald-600";

  const yearsLabel = isSuccess
    ? `Based on OpenDOSM seasonal insights`
    : "Loading historical data…";

  // ── Bar chart: monthly AQI ──────────────────────────────────
  useEffect(() => {
    if (!barChartRef.current || !insightsData?.months) return;

    const months = MONTH_LABELS;
    const values = insightsData.months.map((m) => m.aqi ?? 0);
    const bgColors  = values.map((v) => aqiToHex(v) + "cc");
    const brdColors = values.map((v) => aqiToHex(v));

    if (barInstance.current) { barInstance.current.destroy(); barInstance.current = null; }

    barInstance.current = new Chart(barChartRef.current, {
      type: "bar",
      data: {
        labels: months,
        datasets: [{
          label: `Monthly Avg AQI`,
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
            ticks: { color: "#94a3b8", font: { size: 11, weight: "bold" } },
          },
          y: {
            min: 0,
            suggestedMax: 150,
            grid: { color: "#e2e8f015" },
            ticks: {
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
            },
            title: {
              display: true,
              text: "Avg AQI",
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
            },
          },
        },
      },
    });

    return () => { if (barInstance.current) { barInstance.current.destroy(); barInstance.current = null; } };
  }, [isSuccess, insightsData?.months]);

  // ── Line chart: monthly trend ───────────────────────────────
  useEffect(() => {
    if (!lineChartRef.current || !insightsData?.months) return;

    const datasets = [{
      label: "Seasonal Trend",
      data: insightsData.months.map((m) => m.aqi ?? null),
      borderColor: YEAR_COLORS[0],
      backgroundColor: YEAR_COLORS[0] + "22",
      borderWidth: 2.5,
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0.35,
      fill: false,
    }];

    if (lineInstance.current) { lineInstance.current.destroy(); lineInstance.current = null; }

    lineInstance.current = new Chart(lineChartRef.current, {
      type: "line",
      data: { labels: MONTH_LABELS, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              color: "#94a3b8",
              font: { size: 12, weight: "bold" },
              boxWidth: 14,
              padding: 12,
            },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const aqi = ctx.parsed.y;
                if (!Number.isFinite(aqi)) return ` ${ctx.dataset.label}: N/A`;
                const theme = getAqiTheme(toScale5(aqi));
                return ` ${ctx.dataset.label}: AQI ${Math.round(aqi)} (${theme.label})`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: "#94a3b8", font: { size: 11, weight: "bold" } },
          },
          y: {
            min: 0,
            suggestedMax: 150,
            grid: { color: "#e2e8f015" },
            ticks: { color: "#94a3b8", font: { size: 11, weight: "bold" } },
            title: {
              display: true,
              text: "Avg AQI",
              color: "#94a3b8",
              font: { size: 11, weight: "bold" },
            },
          },
        },
      },
    });

    return () => { if (lineInstance.current) { lineInstance.current.destroy(); lineInstance.current = null; } };
  }, [isSuccess, insightsData?.months]);

  return (
    <div className="relative min-h-[620px] h-auto w-full lg:w-[calc(200%+2rem)] rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative w-full p-6 text-xl flex flex-col gap-6">

        {/* Header */}
        <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
          <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
            <ChartBarSquareIcon className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
          </div>
          <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
            Seasonal & Historical Risk Insights
          </div>
        </div>

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ── Chart 1: Monthly bar chart ── */}
        <div className="relative z-10 flex-none rounded-[1.5rem] border-2 border-slate-200 bg-white/80 dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden shadow-sm">
          <div className="px-5 py-3 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
            <div className="text-lg font-black text-slate-700 dark:text-slate-200">
              Monthly Average AQI Pattern
            </div>
          </div>
          <div className="p-4" style={{ height: "200px" }}>
            {isSuccess && insightsData?.months
              ? <canvas ref={barChartRef} />
              : <div className="flex items-center justify-center h-full text-slate-400 font-bold">Loading…</div>
            }
          </div>
        </div>

        {/* ── Chart 2: Monthly Trend ── */}
        <div className="relative z-10 flex-none rounded-[1.5rem] border-2 border-slate-200 bg-white/80 dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden shadow-sm">
          <div className="px-5 py-3 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
            <div className="text-lg font-black text-slate-700 dark:text-slate-200">
              Seasonal Trend
            </div>
          </div>
          <div className="p-4" style={{ height: "220px" }}>
            {isSuccess && insightsData?.months
              ? <canvas ref={lineChartRef} />
              : <div className="flex items-center justify-center h-full text-slate-400 font-bold">Loading…</div>
            }
          </div>
        </div>

        </div>

        {/* AQI colour legend */}
        <div className="relative z-10 flex-none flex flex-wrap justify-center gap-3 text-xs font-bold text-slate-600 dark:text-slate-300">
          {[
            { label: "Good",      color: "#22c55e", range: "0–50" },
            { label: "Moderate",  color: "#eab308", range: "51–100" },
            { label: "Unhealthy", color: "#f97316", range: "101–200" },
            { label: "Very Unhealthy", color: "#ef4444", range: "201–300" },
            { label: "Hazardous", color: "#7c3aed", range: "301–500" },
          ].map((t) => (
            <div key={t.label} className="flex items-center gap-1.5">
              <div className="h-3 w-3 rounded-full" style={{ background: t.color }} />
              <span>{t.label} ({t.range})</span>
            </div>
          ))}
        </div>

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ── This month's seasonal context ── */}
        <div className="relative z-10 flex-none rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
          <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
            <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
              This Month's Pattern
              {currentMonthData && (
                <span className="ml-2 text-sm font-bold text-slate-500">
                  (Avg AQI {Math.round(currentMonthData.aqi)})
                </span>
              )}
            </div>
          </div>
          <div className="px-5 py-5">
            <div className="flex items-start gap-3">
              <div className={`mt-2 h-3 w-3 rounded-full ${season.dotClass}`} />
              <div>
                <div className="text-lg font-black text-slate-800 dark:text-slate-100">{season.title}</div>
                <div className="mt-2 text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">{season.summary}</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Year-over-year trend text ── */}
        <div className="relative z-10 flex-none rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
          <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
            <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">Year-on-Year Trend</div>
          </div>
          <div className="px-5 py-5">
            <div className="flex items-start gap-3">
              <div className={`mt-2 h-3 w-3 rounded-full ${trendDotClass}`} />
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="text-lg font-black text-slate-800 dark:text-slate-100">{trend.label}</div>
                  {Number.isFinite(Number(trend.level)) && (
                    <div className={["rounded-2xl px-4 py-2 text-base font-black shadow-md border-2 border-white/20", trendTheme.badgeClass].join(" ")}>
                      AQI {trend.level} · {trendTheme.label}
                    </div>
                  )}
                </div>
                <div className="mt-2 text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">{trend.detail}</div>
                <div className="mt-3 text-sm font-bold text-slate-500 dark:text-slate-400">{yearsLabel}</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Preventive planning ── */}
        <div className="relative z-10 flex-none rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
          <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
            <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">Preventive Planning</div>
          </div>
          <div className="px-5 py-5 flex flex-col gap-4">
            {[
              { dot: "bg-emerald-500", text: "Pick flexible outdoor plans: shorter walks, shaded routes, and avoid rush-hour traffic." },
              { dot: "bg-yellow-500",  text: 'Keep a "high-risk day kit": mask, water, medication/inhaler, and indoor exercise alternatives.' },
              { dot: "bg-orange-500",  text: "When haze rises: close windows, use an air purifier if available, and postpone non-essential errands." },
            ].map(({ dot, text }, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`mt-2 h-3 w-3 rounded-full ${dot}`} />
                <div className="text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">{text}</div>
              </div>
            ))}
          </div>
        </div>
        </div>

      </div>
    </div>
  );
}

export default SeasonalRiskInsightsCard;

// import { useSelector } from "react-redux";
// import { useGetAirPollutionForecastQuery } from "../../services/AirQualityAPI";
// import { ChartBarSquareIcon } from "@heroicons/react/24/outline";
// import { getAqiTheme } from "../../lib/aqi";

// function getSeasonInsight(monthIndex) {
//   if (monthIndex >= 4 && monthIndex <= 8) {
//     return {
//       title: "Higher-risk season (haze-prone months)",
//       summary:
//         "In many parts of Malaysia, mid-year months can bring more haze episodes. Expect higher PM2.5 risk and plan more indoor options.",
//       dotClass: "bg-rose-600",
//     };
//   }
//   if (monthIndex === 9) {
//     return {
//       title: "Transition season (risk can fluctuate)",
//       summary:
//         "Air quality can swing quickly. Check daily conditions and keep flexible plans for outdoor activities.",
//       dotClass: "bg-amber-600",
//     };
//   }
//   if (monthIndex >= 10 || monthIndex <= 2) {
//     return {
//       title: "Generally cleaner season (more rain & ventilation)",
//       summary:
//         "Late-year to early-year periods often have more rain and better dispersion. Still watch for short haze events and traffic hotspots.",
//       dotClass: "bg-emerald-600",
//     };
//   }
//   return {
//     title: "Moderate season (stay alert)",
//     summary:
//       "Conditions are usually mixed. Use daily updates to choose safer times and avoid high-traffic routes.",
//     dotClass: "bg-teal-600",
//   };
// }

// function average(values) {
//   if (!values.length) return null;
//   const sum = values.reduce((a, b) => a + b, 0);
//   return sum / values.length;
// }

// function getDayWindowFromNow(daysAhead) {
//   const now = new Date();
//   const start = new Date(now);
//   start.setDate(now.getDate() + daysAhead);
//   start.setHours(0, 0, 0, 0);
//   const end = new Date(start);
//   end.setDate(start.getDate() + 1);
//   return { start, end };
// }

// function SeasonalRiskInsightsCard() {
//   const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
//   const { data, isSuccess } = useGetAirPollutionForecastQuery({ lat, lng });

//   const season = getSeasonInsight(new Date().getMonth());

//   const dayStats = (daysAhead) => {
//     if (!isSuccess) return { mean: null, count: 0 };
//     const { start, end } = getDayWindowFromNow(daysAhead);
//     const items = (data?.list ?? []).filter((x) => {
//       const t = (x?.dt ?? 0) * 1000;
//       return t >= start.getTime() && t < end.getTime();
//     });
//     const values = items
//       .map((x) => Number(x?.main?.aqi))
//       .filter((n) => Number.isFinite(n));
//     return { mean: average(values), count: values.length };
//   };

//   const tomorrow = dayStats(1);
//   const day2 = dayStats(2);
//   const day3 = dayStats(3);

//   const trend = (() => {
//     const first = tomorrow.mean;
//     const last = day3.mean ?? day2.mean;
//     if (!Number.isFinite(first) || !Number.isFinite(last)) return { label: "Trend unavailable", detail: "Not enough forecast data to detect a trend.", level: null };
//     const delta = last - first;
//     if (delta > 0.35) return { label: "Worsening trend", detail: "Risk may increase over the next few days. Reduce outdoor time and keep indoor backup plans.", level: Math.round(last) };
//     if (delta < -0.35) return { label: "Improving trend", detail: "Conditions may get better. Still avoid traffic hotspots and watch for sudden haze events.", level: Math.round(last) };
//     return { label: "Stable trend", detail: "Conditions look steady. Choose cleaner hours and keep routines flexible.", level: Math.round(first) };
//   })();

//   const trendTheme = getAqiTheme(trend.level);
//   const trendDotClass =
//     trendTheme.label === "Very Poor"
//       ? "bg-violet-600"
//       : trendTheme.label === "Poor"
//         ? "bg-rose-600"
//         : trendTheme.label === "Moderate"
//           ? "bg-amber-600"
//           : trendTheme.label === "Fair"
//             ? "bg-teal-600"
//             : "bg-emerald-600";

//   const forecastCoverageLabel = (() => {
//     const total = tomorrow.count + day2.count + day3.count;
//     if (!isSuccess) return "Forecast samples: —";
//     if (total === 0) return "Forecast samples: limited";
//     return `Forecast samples (next 3 days): ${total}`;
//   })();

//   return (
//    <div className="relative w-full mx-auto max-w-[1200px] rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
//       <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

//       <div className="relative h-full w-full p-6 text-xl flex flex-col overflow-hidden">
//         <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
//           <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
//             <ChartBarSquareIcon className="h-7 w-7 text-emerald-800 dark:text-emerald-400" />
//           </div>
//           <div className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
//             Seasonal & Trend-Based Risk Insights
//           </div>
//         </div>

//         <div className="relative z-10 mt-4 flex-1 flex flex-col gap-4 overflow-hidden">
//           <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex-none">
//             <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
//               <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
//                 Seasonal Pattern
//               </div>
//             </div>
//             <div className="px-5 py-5">
//               <div className="flex items-start gap-3">
//                 <div className={`mt-2 h-3 w-3 rounded-full ${season.dotClass}`} />
//                 <div>
//                   <div className="text-lg font-black text-slate-800 dark:text-slate-100">{season.title}</div>
//                   <div className="mt-2 text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">
//                     {season.summary}
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>

//           <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex-none">
//             <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
//               <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
//                 Short Trend (Next 3 Days)
//               </div>
//             </div>
//             <div className="px-5 py-5">
//               <div className="flex items-start gap-3">
//                 <div className={`mt-2 h-3 w-3 rounded-full ${trendDotClass}`} />
//                 <div className="min-w-0">
//                   <div className="flex flex-wrap items-center gap-3">
//                     <div className="text-lg font-black text-slate-800 dark:text-slate-100">{trend.label}</div>
//                     {Number.isFinite(Number(trend.level)) ? (
//                       <div className={["rounded-2xl px-4 py-2 text-base font-black shadow-md border-2 border-white/20", trendTheme.badgeClass].join(" ")}>
//                         API {trend.level} • {trendTheme.label}
//                       </div>
//                     ) : null}
//                   </div>
//                   <div className="mt-2 text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">
//                     {trend.detail}
//                   </div>
//                   <div className="mt-3 text-sm font-bold text-slate-500 dark:text-slate-400">
//                     {forecastCoverageLabel}
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>

//           <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex-1 min-h-0">
//             <div className="px-5 py-4 bg-slate-50/80 border-b border-slate-200 dark:bg-neutral-900/40 dark:border-neutral-800">
//               <div className="text-lg font-black text-slate-700 dark:text-slate-200 tracking-wide">
//                 Preventive Planning
//               </div>
//             </div>
//             <div className="px-5 py-5 flex flex-col gap-4">
//               <div className="flex items-start gap-3">
//                 <div className="mt-2 h-3 w-3 rounded-full bg-emerald-600" />
//                 <div className="text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">
//                   Pick flexible outdoor plans: shorter walks, shaded routes, and avoid rush-hour traffic.
//                 </div>
//               </div>
//               <div className="flex items-start gap-3">
//                 <div className="mt-2 h-3 w-3 rounded-full bg-amber-600" />
//                 <div className="text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">
//                   Keep a “high-risk day kit”: mask, water, medication/inhaler, and indoor exercise alternatives.
//                 </div>
//               </div>
//               <div className="flex items-start gap-3">
//                 <div className="mt-2 h-3 w-3 rounded-full bg-rose-600" />
//                 <div className="text-lg font-bold text-slate-600 dark:text-slate-300 leading-relaxed">
//                   When haze rises: close windows, use an air purifier if available, and postpone non-essential errands.
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default SeasonalRiskInsightsCard;
