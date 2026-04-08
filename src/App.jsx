import { useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Header from "./components/header/Header";
import AirQualityMap from "./components/widgets/AirQualityMap";
import MapDisclaimerCard from "./components/widgets/MapDisclaimerCard";
import Footer from "./components/footer/Footer";

function App() {
  const location = useLocation();
  const isWidgetPage = ["/about", "/privacy", "/terms"].includes(location.pathname);

  useEffect(() => {
    document.documentElement.classList.remove("dark");
    document.documentElement.classList.add("light");
    localStorage.removeItem("theme");
  }, []);

  return (
    <>
      <div className="relative">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-50/75 via-emerald-50/30 to-transparent dark:from-emerald-900/15 dark:via-emerald-900/5" />
        <div className="relative max-w-[1500px] mx-auto px-12 text-[18px] leading-relaxed text-slate-900 dark:text-slate-100 flex flex-col gap-8">
          <Header />
        
          <div className={`flex flex-col gap-8 ${isWidgetPage ? 'w-full' : 'lg:grid lg:grid-cols-2 lg:items-start'}`}>
            <div className="min-w-0 w-full">
              <Outlet />
            </div>
            
            {!isWidgetPage && (
              <div className="min-w-0 flex flex-col gap-8">
                <AirQualityMap />
                {location.pathname !== "/forecast" && <MapDisclaimerCard />}
              </div>
            )}
          </div>

          <div className="pb-10">
            <Footer />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
