import { useSelector } from "react-redux";
import { useGetCurrentAirPollutionByCityQuery } from "../../services/AirQualityAPI";
import { ShieldCheckIcon } from "@heroicons/react/24/outline";
import { getAqiTheme } from "../../lib/aqi";

// Convert 0-500 US AQI → 1-5 scale for getAqiTheme + getAdvice compatibility
function toScale5(aqi) {
  if (!Number.isFinite(Number(aqi))) return null;
  if (aqi <= 50)  return 1;
  if (aqi <= 100) return 2;
  if (aqi <= 200) return 3;
  if (aqi <= 300) return 4;
  return 5;
}

function getAdvice(scale) {
  if (scale === 1) return {
    headline: "Safe to walk (stay hydrated)",
    items: [
      "Walking: Normal routine is OK. Prefer parks/green paths; avoid heavy traffic roads.",
      "Going out: Mask not needed. If you have cough/shortness of breath, keep your inhaler/meds handy.",
      "At home: Short ventilation (10–15 minutes) is usually enough.",
    ],
  };
  if (scale === 2) return {
    headline: "Mostly safe (reduce intensity)",
    items: [
      "Walking: Slow pace. Avoid hills and long brisk walks.",
      "Going out: If you smell smoke/dust or your throat feels irritated, wear a mask and head home early.",
      "At home: Ventilate during cleaner hours and keep windows closed during traffic peaks.",
    ],
  };
  if (scale === 3) return {
    headline: "Limit outdoor exposure",
    items: [
      "Walking: Switch to indoor walking or shorten to 10–20 minutes.",
      "Going out: If you must go, wear a mask and avoid intersections and construction areas.",
      "Health: If you feel chest tightness, shortness of breath, or dizziness — stop and rest immediately.",
    ],
  };
  if (scale === 4) return {
    headline: "Avoid going out (high risk)",
    items: [
      "Walking: Pause outdoor walks. Do light indoor movement instead.",
      "Going out: Postpone if possible. If urgent, wear a mask and minimize time outside.",
      "At home: Keep windows closed. Use an air purifier if available. Avoid smoke from cooking.",
    ],
  };
  if (scale === 5) return {
    headline: "Do not go out (very high risk)",
    items: [
      "Walking: Avoid all outdoor activity and keep windows closed.",
      "Going out: Only for emergencies. Wear a mask and return indoors quickly.",
      "Health: Seniors with hypertension or respiratory history should be extra careful. Seek medical help if symptoms worsen.",
    ],
  };
  return {
    headline: "Advice unavailable",
    items: ["Please try again in a moment or change location to refresh data."],
  };
}

function cityFromLocation(loc) {
  if (!loc || typeof loc !== "string") return "Kuala Lumpur";
  const part = loc.split(",")[0]?.trim();
  return part || "Kuala Lumpur";
}

function ProtectionAdviceCard({ variant = "card" }) {
  const location = useSelector((state) => state.search.location);
  const city     = cityFromLocation(location);
  const { data, isSuccess } = useGetCurrentAirPollutionByCityQuery(
    { city },
    { refetchOnMountOrArgChange: true }
  );

  // NEW: read from backend shape → data.data.aqi (0-500)
  const rawAqi  = isSuccess ? data?.data?.aqi : null;
  const scale   = toScale5(rawAqi);
  const aqiTheme = getAqiTheme(scale);
  const advice   = getAdvice(scale);
  const isUnavailable = !scale;

  const accentDotClass =
    aqiTheme.label === "Hazardous" ? "bg-violet-600"
    : aqiTheme.label === "Very Unhealthy" ? "bg-red-500"
    : aqiTheme.label === "Unhealthy" ? "bg-orange-500"
    : aqiTheme.label === "Moderate" ? "bg-yellow-500"
    : "bg-emerald-600";

  const content = (
    <div className="relative h-full w-full p-6 text-xl flex flex-col overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />

      <div className="relative z-10 flex items-center justify-center gap-3 flex-none">
        <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
          <ShieldCheckIcon className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
        </div>
        <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
          Health Protection Advice
        </div>
      </div>

      <div className="relative z-10 mt-3 flex-1 min-h-0 flex flex-col gap-4 overflow-hidden">
        <div className="flex flex-wrap items-center justify-center gap-4 flex-none">
          <div className={isUnavailable
            ? "text-2xl font-bold text-slate-900 dark:text-white"
            : "text-3xl font-black tracking-tight text-slate-900 dark:text-white"}>
            {advice.headline}
          </div>
        </div>

        <div className="rounded-[2rem] overflow-hidden border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 flex-1 flex flex-col min-h-0">
          <div className="px-5 py-3 bg-gradient-to-r from-emerald-200 via-emerald-100 to-emerald-50 border-b border-emerald-300 dark:from-emerald-900/35 dark:via-emerald-900/20 dark:to-emerald-900/5 dark:border-emerald-900/30 flex-none">
            <div className="text-lg font-black text-emerald-950 dark:text-emerald-50 tracking-wide text-center">Quick Tips</div>
          </div>
          <div className="divide-y divide-slate-200 dark:divide-neutral-800 overflow-auto flex-1 flex flex-col">
            {advice.items.map((t, index) => (
              <div key={index} className="px-5 py-4 flex gap-4 items-start flex-1 flex-col justify-center border-b last:border-0 border-slate-100 dark:border-neutral-800">
                <div className="flex gap-4 items-start w-full">
                  <div className={`mt-2 h-4 w-4 rounded-full ${accentDotClass} shadow-sm flex-none`} />
                  <div className="text-xl font-black text-slate-800 dark:text-slate-100 leading-snug">{t}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
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

export default ProtectionAdviceCard;
