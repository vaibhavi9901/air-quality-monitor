import { Link } from "react-router-dom";

function Footer() {
  const year = new Date().getFullYear();
  const LEVEL_COLORS = {
    Good: "#22c55e",
    Moderate: "#eab308",
    Unhealthy: "#f97316",
    "Very Unhealthy": "#ef4444",
    Hazardous: "#7c3aed",
  };

  return (
    <footer className="mt-10 pb-10">
      <div className="rounded-[2.5rem] border-2 border-emerald-200/80 bg-white px-8 py-10 shadow-sm dark:border-emerald-800/40 dark:bg-neutral-900">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-4 lg:gap-14">
          <div className="min-w-0">
            <div className="text-2xl font-black tracking-tight text-slate-900 dark:text-slate-100">
              Air We Go
            </div>
            <div className="mt-4 text-lg font-semibold leading-relaxed text-slate-700 dark:text-slate-200 text-left">
              Malaysia-focused air quality alerts for seniors — simple risk levels, short-term forecasts, and seasonal
              guidance for safer daily decisions.
            </div>
          </div>

          <div className="min-w-0">
            <div className="text-sm font-black uppercase tracking-[0.18em] text-slate-700 dark:text-slate-200">
              Risk Levels
            </div>
            <div className="mt-4 space-y-3 text-base font-semibold text-slate-700 dark:text-slate-200">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-3.5 w-3.5 rounded-full" style={{ background: LEVEL_COLORS["Good"] }} />
                  <div>Good</div>
                </div>
                <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">0–50</div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-3.5 w-3.5 rounded-full" style={{ background: LEVEL_COLORS["Moderate"] }} />
                  <div>Moderate</div>
                </div>
                <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">51–100</div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-3.5 w-3.5 rounded-full" style={{ background: LEVEL_COLORS["Unhealthy"] }} />
                  <div>Unhealthy</div>
                </div>
                <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">101–200</div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-3.5 w-3.5 rounded-full" style={{ background: LEVEL_COLORS["Very Unhealthy"] }} />
                  <div>Very Unhealthy</div>
                </div>
                <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">201–300</div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-3.5 w-3.5 rounded-full" style={{ background: LEVEL_COLORS["Hazardous"] }} />
                  <div>Hazardous</div>
                </div>
                <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">301–500</div>
              </div>
            </div>
          </div>

          <div className="min-w-0 flex flex-col items-center text-center">
            <div className="text-sm font-black uppercase tracking-[0.18em] text-slate-700 dark:text-slate-200">
              Links
            </div>
            <div className="mt-4 flex flex-col items-center gap-3 text-base font-semibold text-slate-700 dark:text-slate-200">
              <Link to="/about" className="w-fit hover:text-emerald-700 dark:hover:text-emerald-300">
                About Us
              </Link>
              <Link to="/privacy" className="w-fit hover:text-emerald-700 dark:hover:text-emerald-300">
                Privacy
              </Link>
              <Link to="/terms" className="w-fit hover:text-emerald-700 dark:hover:text-emerald-300">
                Terms
              </Link>
            </div>
          </div>

          <div className="min-w-0">
            <div className="text-sm font-black uppercase tracking-[0.18em] text-slate-700 dark:text-slate-200">
              Data Sources
            </div>
            <div className="mt-4 flex flex-col gap-3 text-base font-semibold text-slate-700 dark:text-slate-200">
              <a
                href="https://aqicn.org/api/"
                target="_blank"
                rel="noreferrer"
                className="w-fit hover:text-emerald-700 dark:hover:text-emerald-300"
              >
                World Air Quality Index (WAQI)
              </a>
              <a
                href="https://open.dosm.gov.my/"
                target="_blank"
                rel="noreferrer"
                className="w-fit hover:text-emerald-700 dark:hover:text-emerald-300"
              >
                OpenDOSM (Malaysia)
              </a>
              <div className="text-sm font-semibold leading-relaxed text-slate-500 dark:text-slate-400">
                WAQI access requires a token and is subject to quota. Attribution may be required by data providers.
              </div>
              <div className="pt-2 text-sm font-semibold text-slate-500 dark:text-slate-400">
                Air We Go | © Air We Go | © CARTO | © OpenStreetMap
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-slate-200 pt-6 text-base font-semibold text-slate-600 dark:border-neutral-800 dark:text-slate-300 md:flex-row md:items-center md:justify-between">
          <div>Copyright © {year} Air We Go. All rights reserved.</div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
