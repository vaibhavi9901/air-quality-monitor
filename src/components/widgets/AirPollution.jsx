import { useSelector } from "react-redux";
import { GiAbstract053 } from "react-icons/gi";
import { useGetCurrentAirPollutionQuery } from "../../services/AirQualityAPI";

// Convert 0-500 US AQI to 1-5 scale used by describeAirQuality
function toScale5(aqi) {
  if (!Number.isFinite(Number(aqi))) return null;
  if (aqi <= 50)  return 1;
  if (aqi <= 100) return 2;
  if (aqi <= 200) return 3;
  if (aqi <= 300) return 4;
  return 5;
}

function AirPollution() {
  const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
  const { data, isSuccess } = useGetCurrentAirPollutionQuery({ lat, lng });

  function describeAirQuality(scale) {
    const airQualityLevels = {
      1: {
        description: "GOOD AIR QUALITY",
        prevention: "Ideal for morning walks and outdoor activities!",
        color: "bg-green-500",
        text: "text-green-700",
      },
      2: {
        description: "MODERATE AIR QUALITY",
        prevention: "Safe for most, but sensitive individuals should take breaks and avoid heavy traffic roads.",
        color: "bg-yellow-500",
        text: "text-yellow-700",
      },
      3: {
        description: "UNHEALTHY AIR QUALITY",
        prevention: "Higher risk for elderly. Reduce outdoor exertion and prefer indoor activities.",
        color: "bg-orange-500",
        text: "text-orange-700",
      },
      4: {
        description: "VERY UNHEALTHY AIR QUALITY",
        prevention: "High risk. Avoid outdoor activities and keep windows closed when possible.",
        color: "bg-red-500",
        text: "text-red-700",
      },
      5: {
        description: "HAZARDOUS AIR QUALITY",
        prevention: "Health alert: Avoid outdoor exposure except emergencies. Consider a mask and air purifier.",
        color: "bg-violet-600",
        text: "text-violet-700",
      },
    };
    return airQualityLevels[scale] ?? {
      description: "Unknown",
      prevention: "Data unavailable.",
      color: "bg-gray-400",
      text: "text-gray-700",
    };
  }

  // NEW: read from backend shape → data.data.aqi (0-500)
  const rawAqi  = isSuccess ? data?.data?.aqi : null;
  const scale   = toScale5(rawAqi);
  const aqiInfo = scale ? describeAirQuality(scale) : null;

  return (
    <>
      {isSuccess && aqiInfo && (
        <div className="flex h-64 flex-col overflow-hidden rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200 dark:bg-neutral-900 dark:ring-neutral-800">
          {/* TITLE */}
          <div className="flex flex-row items-center gap-3 mb-4">
            <div className="bg-emerald-50 p-2 rounded-xl dark:bg-emerald-900/10">
              <GiAbstract053 className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-100">
              Live Air Status
            </div>
          </div>

          {/* MAIN CONTENT */}
          <div className="flex h-full flex-col justify-between">
            <div className="flex flex-col">
              <div className={`text-4xl font-bold tracking-tight ${aqiInfo.text}`}>
                {aqiInfo.description}
              </div>
              <div className="mt-3 text-lg font-semibold leading-tight text-slate-700 dark:text-slate-200">
                {aqiInfo.prevention}
              </div>
            </div>

            {/* AQI BAR INDICATOR — scaled from 0-500 */}
            <div className="mt-6">
              <div className="flex justify-between text-xs font-semibold text-slate-500 mb-2">
                <span>CLEAN AIR</span>
                <span>AQI {Math.round(rawAqi)}</span>
                <span>HAZARDOUS</span>
              </div>
              <div className="relative h-5 w-full rounded-full bg-slate-100 dark:bg-neutral-800 overflow-hidden">
                <div
                  className={`h-full transition-all duration-1000 ease-out ${aqiInfo.color}`}
                  style={{ width: `${Math.min((rawAqi / 500) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AirPollution;

// import { useSelector } from "react-redux";
// import { GiAbstract053 } from "react-icons/gi";
// import { useGetCurrentAirPollutionQuery } from "../../services/AirQualityAPI";

// function AirPollution() {
//   //   Access to RTX Query cached data
//   const { lat, lng } = useSelector((state) => state.geolocation.geolocation);
//   const { data, isSuccess } = useGetCurrentAirPollutionQuery({
//     lat,
//     lng,
//   });

//   function describeAirQuality(aqi) {
//     const airQualityLevels = {
//       1: {
//         description: "GOOD AIR QUALITY",
//         prevention: "Ideal for morning walks and outdoor activities!",
//         color: "bg-green-500",
//         text: "text-green-700",
//       },
//       2: {
//         description: "FAIR AIR QUALITY",
//         prevention:
//           "Safe for most, but those with respiratory issues should take breaks.",
//         color: "bg-yellow-400",
//         text: "text-yellow-700",
//       },
//       3: {
//         description: "MODERATE AIR QUALITY",
//         prevention:
//           "Vulnerable groups should reduce prolonged outdoor exertion.",
//         color: "bg-orange-500",
//         text: "text-orange-700",
//       },
//       4: {
//         description: "POOR AIR QUALITY",
//         prevention:
//           "High risk for elderly. Please move activities indoors or reschedule.",
//         color: "bg-red-500",
//         text: "text-red-700",
//       },
//       5: {
//         description: "VERY POOR AIR QUALITY",
//         prevention:
//           "Health Alert: Avoid all outdoor activities. Keep windows closed.",
//         color: "bg-purple-600",
//         text: "text-purple-700",
//       },
//     };

//     if (airQualityLevels[aqi]) {
//       return airQualityLevels[aqi];
//     } else {
//       return {
//         description: "Unknown",
//         prevention: "Data unavailable.",
//         color: "bg-gray-400",
//         text: "text-gray-700",
//       };
//     }
//   }

//   const aqiInfo = isSuccess ? describeAirQuality(data.list[0].main.aqi) : null;

//   return (
//     <>
//       {isSuccess && (
//         <div className="flex h-64 flex-col overflow-hidden rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200 dark:bg-neutral-900 dark:ring-neutral-800">
//           {/* TITLE */}
//           <div className="flex flex-row items-center gap-3 mb-4">
//             <div className="bg-emerald-50 p-2 rounded-xl dark:bg-emerald-900/10">
//               <GiAbstract053 className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
//             </div>
//             <div className="text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-100">
//               Live Air Status
//             </div>
//           </div>

//           {/* MAIN CONTENT */}
//           <div className="flex h-full flex-col justify-between">
//             <div className="flex flex-col">
//               <div className={`text-4xl font-bold tracking-tight ${aqiInfo.text}`}>
//                 {aqiInfo.description}
//               </div>
//               <div className="mt-3 text-lg font-semibold leading-tight text-slate-700 dark:text-slate-200">
//                 {aqiInfo.prevention}
//               </div>
//             </div>

//             {/* AQI BAR INDICATOR */}
//             <div className="mt-6">
//               <div className="flex justify-between text-xs font-semibold text-slate-500 mb-2">
//                 <span>CLEAN AIR</span>
//                 <span>HAZARDOUS</span>
//               </div>
//               <div className="relative h-5 w-full rounded-full bg-slate-100 dark:bg-neutral-800 overflow-hidden">
//                 <div
//                   className={`h-full transition-all duration-1000 ease-out ${aqiInfo.color}`}
//                   style={{ width: `${(data.list[0].main.aqi / 5) * 100}%` }}
//                 ></div>
//               </div>
//             </div>
//           </div>
//         </div>
//       )}
//     </>
//   );
// }

// export default AirPollution;
