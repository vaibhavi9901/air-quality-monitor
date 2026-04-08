import { Link, NavLink } from "react-router-dom";
import Location from "./Location";
import SearchBar from "./SearchBar";
import { CloudIcon } from "@heroicons/react/24/outline";

function AirFlowIcon({ className, animated = true }) {
  return (
    <div className={className}>
      <svg
        viewBox="0 0 64 64"
        className="h-full w-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <g opacity="0.95">
          <path
            d="M6 22 C 16 14, 28 14, 38 22 S 58 30, 58 22"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="64 18"
          >
            {animated && (
              <animate
                attributeName="stroke-dashoffset"
                values="0;-82"
                dur="8s"
                repeatCount="indefinite"
              />
            )}
          </path>
          <path
            d="M6 34 C 18 26, 30 26, 40 34 S 58 42, 58 34"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="56 16"
            opacity="0.75"
          >
            {animated && (
              <animate
                attributeName="stroke-dashoffset"
                values="0;-72"
                dur="9s"
                repeatCount="indefinite"
              />
            )}
          </path>
          <path
            d="M10 46 C 20 40, 30 40, 40 46 S 54 52, 54 46"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="44 14"
            opacity="0.55"
          >
            {animated && (
              <animate
                attributeName="stroke-dashoffset"
                values="0;-62"
                dur="11s"
                repeatCount="indefinite"
              />
            )}
          </path>
        </g>
      </svg>
    </div>
  );
}

function ForecastAirFlowIcon({ className, animated = true }) {
  return (
    <div className={className}>
      <svg
        viewBox="0 0 64 64"
        className="h-full w-full"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <g opacity="0.95">
          <rect x="10" y="16" width="6" height="32" rx="3" fill="currentColor" opacity="0.45" />
          <rect x="21" y="20" width="6" height="28" rx="3" fill="currentColor" opacity="0.6" />
          <rect x="32" y="24" width="6" height="24" rx="3" fill="currentColor" opacity="0.75" />
          <path
            d="M14 28 C 22 22, 30 22, 38 28 S 56 34, 56 28"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="58 18"
          >
            {animated && (
              <animate
                attributeName="stroke-dashoffset"
                values="0;-76"
                dur="10s"
                repeatCount="indefinite"
              />
            )}
          </path>
          <path
            d="M14 40 C 24 34, 32 34, 42 40 S 56 46, 56 40"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="50 16"
            opacity="0.8"
          >
            {animated && (
              <animate
                attributeName="stroke-dashoffset"
                values="0;-68"
                dur="12s"
                repeatCount="indefinite"
              />
            )}
          </path>
        </g>
      </svg>
    </div>
  );
}

function Header() {
  return (
    <>
      <nav className="relative z-50 pt-6 pb-4 grid grid-cols-3 items-center gap-6">
        <div className="w-full flex justify-start">
          <Link
            to="/"
            className="flex items-center gap-3 text-4xl font-black tracking-tight text-slate-900 dark:text-white"
          >
            <CloudIcon className="h-12 w-12 text-emerald-600 dark:text-emerald-400" />
            <span className="inline">Air We Go</span>
          </Link>
        </div>
        <div className="flex w-full justify-center invisible md:visible">
          <Location />
        </div>
        <div className="w-full flex items-center justify-end gap-4">
          <SearchBar />
        </div>
      </nav>
      <div className="mt-12 flex justify-center pb-10">
        <div className="grid w-full max-w-[68rem] grid-cols-2 gap-8 px-2">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              [
                "relative overflow-hidden w-full min-h-[7.25rem] rounded-[2.5rem] py-4 px-8 transition-all active:scale-95 flex items-center justify-center",
                isActive
                  ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md shadow-emerald-200/60 dark:shadow-none"
                  : "bg-white text-slate-900 hover:bg-emerald-50/60 border-2 border-emerald-200/80 dark:bg-neutral-900 dark:text-slate-100 dark:border-emerald-800/40 dark:hover:bg-neutral-800",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                {!isActive && (
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />
                )}
                <div className="relative z-10 flex items-center justify-center gap-5">
                  <AirFlowIcon className="h-14 w-14 motion-reduce:hidden" animated />
                  <AirFlowIcon className="h-14 w-14 hidden motion-reduce:block" animated={false} />
                  <div className="text-3xl font-black tracking-tight">Today's Air Quality</div>
                </div>
              </>
            )}
          </NavLink>

          <NavLink
            to="/forecast"
            className={({ isActive }) =>
              [
                "relative overflow-hidden w-full min-h-[7.25rem] rounded-[2.5rem] py-4 px-8 transition-all active:scale-95 flex items-center justify-center",
                isActive
                  ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-md shadow-emerald-200/60 dark:shadow-none"
                  : "bg-white text-slate-900 hover:bg-emerald-50/60 border-2 border-emerald-200/80 dark:bg-neutral-900 dark:text-slate-100 dark:border-emerald-800/40 dark:hover:bg-neutral-800",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                {!isActive && (
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />
                )}
                <div className="relative z-10 flex items-center justify-center gap-5">
                  <ForecastAirFlowIcon className="h-14 w-14 motion-reduce:hidden" animated />
                  <ForecastAirFlowIcon className="h-14 w-14 hidden motion-reduce:block" animated={false} />
                  <div className="text-3xl font-black tracking-tight">Air Quality Forecast</div>
                </div>
              </>
            )}
          </NavLink>
        </div>
      </div>
    </>
  );
}
export default Header;
