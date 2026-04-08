import { useSelector } from "react-redux";
import { useGetCurrentAirPollutionByCityQuery } from "../../services/AirQualityAPI";
import { CloudIcon } from "@heroicons/react/24/outline";
import { getAqiTheme, getPm25Theme, API_STANDARDS, PM25_STANDARDS } from "../../lib/aqi";

// "Kuala Lumpur, Malaysia" -> "Kuala Lumpur"
function cityFromLocation(loc) {
  if (!loc || typeof loc !== "string") return "Kuala Lumpur";
  const part = loc.split(",")[0]?.trim();
  return part || "Kuala Lumpur";
}

// Convert 0-500 US AQI → 1-5 scale for getAqiTheme compatibility
function toScale5(aqi) {
  if (!Number.isFinite(Number(aqi))) return null;
  if (aqi <= 50)  return 1;
  if (aqi <= 100) return 2;
  if (aqi <= 200) return 3;
  if (aqi <= 300) return 4;
  return 5;
}

function formatDateTime(isoString) {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    return d.toLocaleString("en-MY", {
      year: "numeric", month: "short", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function AirQualityInfoCard({ variant = "card" }) {
  const location = useSelector((state) => state.search.location);
  const city     = cityFromLocation(location);

  // Use selected city so search bar selection always refreshes data
  const pollution = useGetCurrentAirPollutionByCityQuery(
    { city },
    { pollingInterval: 60 * 60 * 1000, refetchOnMountOrArgChange: true }
  );

  const isSuccess = pollution.isSuccess;
  const isLoading = pollution.isLoading;
  const isError   = pollution.isError;

  const current   = pollution.data?.data;
  const rawAqi    = current?.aqi ?? null;
  const pm25      = current?.pollutants?.pm25 ?? null;
  const timestamp = current?.timestamp ?? null;

  const aqiTheme  = getAqiTheme(toScale5(rawAqi));
  const pm25Theme = getPm25Theme(pm25);

  const hasValidAqi = Number.isFinite(Number(rawAqi));
  const loading = pollution.isLoading;
  const isSuccessWithData = hasValidAqi && current;
  const isUpdateDelayed = !loading && !isSuccessWithData;

  // Use the alert block our backend already computed
  const backendAlert = current?.alert;

  const alert = (() => {
    if (!isSuccessWithData || !backendAlert?.active) return null;

    const themeMap = {
      "Good": { label: "Good", bgClass: "bg-emerald-200 dark:bg-emerald-400/20", borderClass: "border-emerald-400 dark:border-emerald-300/40", textClass: "text-emerald-950 dark:text-emerald-50", icon: "✅", animClass: "" },
      "Moderate": { label: "Moderate", bgClass: "bg-yellow-200 dark:bg-yellow-400/20", borderClass: "border-yellow-400 dark:border-yellow-300/40", textClass: "text-yellow-950 dark:text-yellow-50", icon: "⚠️", animClass: "" },
      "Unhealthy": { label: "Unhealthy", bgClass: "bg-orange-200 dark:bg-orange-400/20", borderClass: "border-orange-400 dark:border-orange-300/40", textClass: "text-orange-950 dark:text-orange-50", icon: "⚠️", animClass: "animate-pulse" },
      "Very Unhealthy": { label: "Very Unhealthy", bgClass: "bg-red-200 dark:bg-red-400/20", borderClass: "border-red-400 dark:border-red-300/40", textClass: "text-red-950 dark:text-red-50", icon: "⚠️", animClass: "animate-pulse" },
      "Hazardous": { label: "Hazardous", bgClass: "bg-violet-200 dark:bg-violet-400/20", borderClass: "border-violet-400 dark:border-violet-300/40", textClass: "text-violet-950 dark:text-violet-50", icon: "🚨", animClass: "animate-pulse" },
    };
    
    // If backend provides risk_label in alert, use it, otherwise fallback to level or default
    const riskLabel = backendAlert.risk_label || backendAlert.level || "Moderate";
    return { ...(themeMap[riskLabel] ?? themeMap["Moderate"]), message: backendAlert.message };
  })();

  const content = (
    <div className="relative h-full w-full p-6 text-xl flex flex-col overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
        <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
          <CloudIcon 
            className="h-8 w-8 text-emerald-800 dark:text-emerald-400" 
          />
        </div>
        <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
          Air Quality Info
        </div>
      </div>

      {!isUpdateDelayed && alert && (
        <div className={["relative z-10 -mx-6 mt-3 px-6 py-3 border-y-2", alert.bgClass, alert.borderClass, alert.textClass, alert.animClass].join(" ")}>
          <div className="flex items-center justify-center gap-3">
            <div className="text-2xl font-black">{alert.icon}</div>
            <div className="text-2xl font-black tracking-tight">{alert.label}</div>
          </div>
          <div className="mt-1 text-center text-xl font-black tracking-tight">
            AQI {Math.round(rawAqi)} ({aqiTheme.label})
            {pm25 != null && ` • PM2.5 ${pm25.toFixed(0)} (${pm25Theme.label})`}
          </div>
        </div>
      )}

      <div className="relative z-10 mt-2 flex flex-1 min-h-0 flex-col gap-2 overflow-hidden">
        <div className="text-xl font-semibold text-emerald-700 dark:text-emerald-400 flex-none">
          {location}
        </div>

        {loading ? (
          <div className="mt-4 rounded-2xl bg-slate-50 p-6 text-xl font-bold text-slate-600 border border-slate-200 dark:bg-neutral-950 dark:text-slate-300 dark:border-neutral-800">
            Fetching data for your location…
          </div>
        ) : isUpdateDelayed ? (
          <div className="mt-4 rounded-2xl bg-slate-100 p-6 text-center border border-slate-200 text-slate-700 dark:bg-neutral-950 dark:text-slate-300 dark:border-neutral-800">
            <div className="text-2xl font-black tracking-wide">UPDATE DELAYED</div>
          </div>
        ) : isSuccessWithData ? (
          <div className="flex-1 flex flex-col justify-start">
            <div className="flex flex-col gap-1 flex-none mb-3">
              <div className="text-2xl font-bold leading-snug text-slate-800 dark:text-slate-100">
                {aqiTheme.summary}
              </div>
            </div>

            <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2 flex-1 items-stretch origin-top scale-[0.9]">
              {/* AQI Box */}
              <div className="group relative flex h-full flex-col items-center justify-center rounded-[2.5rem] bg-white px-4 py-6 min-h-[260px] border-2 border-slate-300 shadow-lg dark:bg-neutral-950 dark:border-neutral-700">
                <div className="text-xl font-bold text-slate-500 uppercase tracking-[0.2em]">AQI</div>
                <div 
                  className="mt-1 text-7xl font-black leading-none transition-colors duration-500"
                  style={{ color: aqiTheme.color }}
                >
                  {rawAqi != null ? Math.round(rawAqi) : "—"}
                </div>
                <div className="mt-2 text-xl font-black text-slate-700 dark:text-slate-300">{aqiTheme.level}</div>
                <div className={`mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20 cursor-pointer hover:scale-[1.02] transition-transform ${aqiTheme.badgeClass}`}>
                  {aqiTheme.label}
                </div>
                <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                  <div className="h-full w-full rounded-[2.5rem] bg-slate-900/95 p-4 flex flex-col items-center justify-center text-white shadow-2xl backdrop-blur-sm border-2 border-emerald-500/30">
                    <p className="text-base font-black text-emerald-400 mb-2 tracking-widest uppercase">AQI Standards</p>
                    <div className="w-full space-y-1.5">
                      {API_STANDARDS.map((s) => (
                        <div key={s.level} className="flex justify-between items-center text-sm font-bold border-b border-white/10 pb-1 last:border-0">
                          <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white/70"}>{s.range}</span>
                          <span className={s.label === aqiTheme.label ? "text-emerald-400" : "text-white"}>{s.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-3 text-sm font-bold text-slate-400">{aqiTheme.motivation}</div>
              </div>

              {/* PM2.5 Box */}
              <div className="group relative flex h-full flex-col items-center justify-center rounded-[2.5rem] bg-white px-4 py-6 min-h-[260px] border-2 border-slate-300 shadow-lg dark:bg-neutral-900 dark:border-neutral-700">
                <div className="text-xl font-bold text-slate-500 uppercase tracking-[0.2em]">PM2.5</div>
                <div 
                  className="mt-1 text-7xl font-black leading-none transition-colors duration-500"
                  style={{ color: pm25Theme.color }}
                >
                  {pm25 != null ? pm25.toFixed(0) : "—"}
                </div>
                <div className="mt-2 text-xl font-black text-slate-700 dark:text-slate-300">{pm25Theme.level}</div>
                <div className={`mt-3 w-full text-center rounded-2xl px-4 py-2.5 text-lg font-black shadow-md border-2 border-white/20 cursor-pointer hover:scale-[1.02] transition-transform ${pm25Theme.badgeClass}`}>
                  {pm25Theme.label}
                </div>
                <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                  <div className="h-full w-full rounded-[2.5rem] bg-slate-900/95 p-4 flex flex-col items-center justify-center text-white shadow-2xl backdrop-blur-sm border-2 border-emerald-500/30">
                    <p className="text-base font-black text-emerald-400 mb-2 tracking-widest uppercase">PM2.5 Standards</p>
                    <div className="w-full space-y-1.5">
                      {PM25_STANDARDS.map((s) => (
                        <div key={s.level} className="flex justify-between items-center text-sm font-bold border-b border-white/10 pb-1 last:border-0">
                          <span className={s.label === pm25Theme.label ? "text-emerald-400" : "text-white/70"}>{s.range}</span>
                          <span className={s.label === pm25Theme.label ? "text-emerald-400" : "text-white"}>{s.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-3 text-sm font-bold text-slate-400">Particles (µg/m³)</div>
              </div>
            </div>

            <div className="flex flex-col gap-0.5 flex-none mt-2 text-center">
              <div className="text-sm font-bold text-slate-500 dark:text-slate-400">
                Updated: {formatDateTime(timestamp)}
              </div>
              <div className="text-sm font-bold text-slate-500 dark:text-slate-400">
                Source:{" "}
                <a
                  href="https://open-meteo.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-emerald-800 underline decoration-emerald-300 underline-offset-4 hover:text-emerald-900 dark:text-emerald-200 dark:hover:text-emerald-100"
                >
                  Open-Meteo
                </a>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-4 rounded-2xl bg-slate-50 p-6 text-xl font-bold text-slate-600 border border-slate-200 dark:bg-neutral-950 dark:text-slate-300 dark:border-neutral-800">
            Fetching data for your location…
          </div>
        )}
      </div>
    </div>
  );

  if (variant === "section") return content;

  return (
    <div className="h-[620px] w-full rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
      {content}
    </div>
  );
}

export default AirQualityInfoCard;