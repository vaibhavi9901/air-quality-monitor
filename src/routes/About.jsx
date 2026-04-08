function About() {
  return (
    <div className="w-full rounded-[2.5rem] bg-white shadow-sm border-2 border-emerald-200/80 dark:bg-neutral-900 dark:border-emerald-800/40 overflow-hidden">
        <div className="relative w-full p-10 text-xl flex flex-col">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/25 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5" />

          <div className="relative z-10 text-[2.5rem] font-black tracking-tight text-slate-900 dark:text-slate-100 text-center">
            About Air We Go
          </div>

          <div className="relative z-10 mt-8 text-xl font-bold leading-relaxed text-slate-700 dark:text-slate-200 text-center max-w-3xl mx-auto">
            Air We Go is an air quality monitoring assistant dedicated to Malaysia, specially designed for seniors. 
            We provide clear, real-time alerts and simple health guidance to help you navigate haze seasons safely.
          </div>

          <div className="relative z-10 mt-12 grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex flex-col">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Simple Visuals
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed flex-1 text-center">
                We use high-contrast colors and large text labels (Good to Hazardous) so you can understand the air quality at a glance without straining your eyes.
              </div>
            </div>

            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex flex-col">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Reliable Data
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed flex-1 text-center">
                Our data comes directly from established sources like WAQI and OpenDOSM, ensuring you receive the most accurate information available in Malaysia.
              </div>
            </div>

            <div className="rounded-[2rem] border-2 border-slate-200 bg-white/70 shadow-sm dark:bg-neutral-950 dark:border-neutral-800 overflow-hidden flex flex-col">
              <div className="px-6 py-5 bg-emerald-50 border-b border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800">
                <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 tracking-wide text-center">
                  Safety First
                </div>
              </div>
              <div className="px-6 py-6 text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed flex-1 text-center">
                Our priority is your health. We provide actionable advice on when to stay indoors and direct access to emergency services if you feel unwell.
              </div>
            </div>
          </div>

          <div className="relative z-10 mt-10 rounded-[2.5rem] bg-emerald-50/50 p-8 border-2 border-emerald-100 dark:bg-emerald-900/10 dark:border-emerald-900/20">
            <div className="text-xl font-black text-emerald-800 dark:text-emerald-300 mb-4">
              Our Mission
            </div>
            <p className="text-lg font-bold text-slate-700 dark:text-slate-200 leading-relaxed">
              We believe that information should be accessible to everyone. By simplifying complex air quality data into senior-friendly formats, 
              we empower our elders to maintain their independence and health during environmental challenges.
            </p>
          </div>
        </div>
      </div>
  );
}

export default About;

