import React from "react";
import { ExclamationCircleIcon, PhoneIcon } from "@heroicons/react/24/outline";

function MapDisclaimerCard() {
  return (
    <div className="relative overflow-hidden h-[620px] rounded-[2.5rem] bg-white w-full max-w-full mx-auto p-6 shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5 dark:to-transparent" />
      
      <div className="relative z-10 h-full flex flex-col">
        {/* Header Section - Same as Health Advice */}
        <div className="flex items-center justify-center gap-3 flex-none">
          <div className="rounded-2xl bg-emerald-100 p-2 dark:bg-emerald-900/30">
            <ExclamationCircleIcon className="h-8 w-8 text-emerald-800 dark:text-emerald-400" />
          </div>
          <div className="text-[2.025rem] font-black tracking-tight text-slate-900 dark:text-slate-100">
            Important Notice
          </div>
        </div>
        
        <div className="mt-3 flex-1 flex flex-col gap-8 overflow-hidden">
          <div className="text-center flex-none">
            <div className="text-2xl font-black text-red-600 dark:text-red-400 uppercase tracking-tight">
              Not Medical Advice
            </div>
            <p className="mt-4 text-xl font-bold leading-relaxed text-slate-700 dark:text-slate-200">
              If you feel unwell or experience breathing difficulties,
              please seek medical help or emergency services immediately.
            </p>
          </div>

          {/* Emergency Contact Section for Malaysia */}
          <div className="rounded-3xl bg-red-50 py-10 px-6 border-2 border-red-100 dark:bg-red-900/10 dark:border-red-900/30 flex-none">
            <div className="flex items-center gap-4 mb-6">
              <div className="rounded-xl bg-red-100 p-2 dark:bg-red-900/30">
                <PhoneIcon className="h-6 w-6 text-red-700 dark:text-red-400" />
              </div>
              <div className="text-xl font-black text-red-800 dark:text-red-300">
                Malaysia Emergency Contacts
              </div>
            </div>
            
            <div className="flex flex-col gap-4">
              {/* 999 Call Box */}
              <a 
                href="tel:999" 
                className="flex items-center justify-between bg-white p-5 rounded-2xl border-2 border-red-200 shadow-sm hover:bg-red-50 transition-colors dark:bg-neutral-800 dark:border-red-900/50"
              >
                <div className="min-w-0">
                  <div className="text-xs font-bold text-red-600 uppercase tracking-widest mb-1">General Emergency</div>
                  <div className="text-4xl font-black text-slate-900 dark:text-white leading-none">999</div>
                </div>
                <div className="flex-none bg-red-600 text-white px-6 py-3 rounded-xl font-black text-lg shadow-md active:scale-95 transition-transform">
                  CALL NOW
                </div>
              </a>

              {/* Support Info Box */}
              <div className="bg-white p-5 rounded-2xl border-2 border-red-100 dark:bg-neutral-800 dark:border-red-900/40">
                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Police / Fire / Ambulance</div>
                <div className="text-lg font-black text-red-700 dark:text-red-400 text-center sm:text-left">Available 24/7 Nationwide</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapDisclaimerCard;
