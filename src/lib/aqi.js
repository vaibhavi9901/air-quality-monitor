export function normalizeAqi(aqi) {
  const n = Number(aqi);
  if (!Number.isFinite(n)) return null;
  if (n < 1 || n > 5) return null;
  return n;
}

export const API_STANDARDS = [
  { level: "Level 1", label: "Good", range: "0 - 50", color: "#22c55e" },
  { level: "Level 2", label: "Moderate", range: "51 - 100", color: "#eab308" },
  { level: "Level 3", label: "Unhealthy", range: "101 - 200", color: "#f97316" },
  { level: "Level 4", label: "Very Unhealthy", range: "201 - 300", color: "#ef4444" },
  { level: "Level 5", label: "Hazardous", range: "301 - 500", color: "#7c3aed" },
];

export const PM25_STANDARDS = [
  { level: "Level 1", label: "Good", range: "0.0 - 12.0", color: "#22c55e" },
  { level: "Level 2", label: "Moderate", range: "12.1 - 35.4", color: "#eab308" },
  { level: "Level 3", label: "Unhealthy", range: "35.5 - 55.4", color: "#f97316" },
  { level: "Level 4", label: "Very Unhealthy", range: "55.5 - 150.4", color: "#ef4444" },
  { level: "Level 5", label: "Hazardous", range: "> 150.4", color: "#7c3aed" },
];

export const WIND_STANDARDS = [
  { level: "Level 1", label: "Calm Air", range: "0 - 1.5" },
  { level: "Level 2", label: "Light Breeze", range: "1.6 - 3.3" },
  { level: "Level 3", label: "Gentle Wind", range: "3.4 - 5.4" },
  { level: "Level 4", label: "Moderate Wind", range: "5.5 - 7.9" },
  { level: "Level 5", label: "Strong Wind", range: "> 8.0" },
];

export function getPm25Theme(pm25) {
  const value = Number(pm25);
  let n = 1;
  if (!Number.isFinite(value)) n = 1;
  else if (value > 150.4) n = 5;
  else if (value > 55.4) n = 4;
  else if (value > 35.4) n = 3;
  else if (value > 12.0) n = 2;

  const base = getAqiTheme(n);
  return { ...base, ...PM25_STANDARDS[n - 1] };
}

export function getAqiTheme(aqi) {
  const themes = {
    1: {
      ...API_STANDARDS[0],
      motivation: "Ideal for walk!",
      summary: "Clean air. Outdoor activities are generally safe.",
      badgeClass:
        "bg-emerald-200 text-emerald-950 ring-2 ring-emerald-300 dark:bg-emerald-400/20 dark:text-emerald-100 dark:ring-emerald-300/40",
    },
    2: {
      ...API_STANDARDS[1],
      motivation: "Safe to go out",
      summary: "Mostly safe. Sensitive seniors should pace themselves.",
      badgeClass:
        "bg-yellow-200 text-yellow-950 ring-2 ring-yellow-300 dark:bg-yellow-400/20 dark:text-yellow-100 dark:ring-yellow-300/40",
    },
    3: {
      ...API_STANDARDS[2],
      motivation: "Be cautious",
      summary: "Reduce outdoor time, especially near traffic.",
      badgeClass:
        "bg-orange-200 text-orange-950 ring-2 ring-orange-300 dark:bg-orange-400/20 dark:text-orange-100 dark:ring-orange-300/40",
    },
    4: {
      ...API_STANDARDS[3],
      motivation: "Stay indoors",
      summary: "Not recommended to go out for walks or errands.",
      badgeClass:
        "bg-red-200 text-red-950 ring-2 ring-red-300 dark:bg-red-400/20 dark:text-red-100 dark:ring-red-300/40",
    },
    5: {
      ...API_STANDARDS[4],
      motivation: "Highly unsafe",
      summary: "Avoid going outdoors. Higher respiratory & cardiovascular risk.",
      badgeClass:
        "bg-violet-200 text-violet-950 ring-2 ring-violet-300 dark:bg-violet-400/20 dark:text-violet-100 dark:ring-violet-300/40",
    },
  };

  return themes[aqi] || themes[1];
}
