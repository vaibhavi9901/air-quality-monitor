function Privacy() {
  return (
    <div className="w-full rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
        <div className="relative w-full p-10 text-xl flex flex-col">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5" />

          <div className="relative z-10 text-[2.5rem] font-black tracking-tight text-slate-900 dark:text-slate-100 text-center">
            Privacy Policy
          </div>

          <div className="relative z-10 mt-12 grid grid-cols-1 gap-8 md:grid-cols-2">
            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Data Collection
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed text-center">
                Air We Go is designed with privacy as a core principle. We do not require account registration, and we do not collect any personal identifiers such as names, email addresses, or phone numbers.
              </div>
            </div>

            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Location Usage
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed text-center">
                Your location is used solely to provide relevant local air quality information. This location data is processed locally on your device and is not stored on our servers.
              </div>
            </div>

            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Transparency
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed text-center">
                We believe in full transparency. All data requests are made directly from your browser to trusted public APIs. We do not sell or share any information with third-party advertisers.
              </div>
            </div>

            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Local Processing
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed text-center">
                If you are running the application locally, all data remains within your local environment, ensuring maximum security and control over your information.
              </div>
            </div>
          </div>
        </div>
      </div>
  );
}

export default Privacy;

