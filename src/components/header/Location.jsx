import { Popover, Transition } from "@headlessui/react";
import { MapPinIcon } from "@heroicons/react/24/outline";
import { Fragment, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { saveGeoCode } from "../../features/geolocation/geolocationSlice";
import { saveLocation } from "../../features/search/searchSlice";
import { useGetAirQualityMapQuery } from "../../services/AirQualityAPI";

function Location() {
  const dispatch = useDispatch();
  const selectedLocation = useSelector((state) => state.search.location);
  const { data: stationsData, isSuccess } = useGetAirQualityMapQuery();
  const [selectedState, setSelectedState] = useState(null);

  const activeStations = useMemo(() => {
    const stations = stationsData?.data ?? [];
    return stations.filter((s) => s?.active !== false);
  }, [stationsData]);

  const states = useMemo(() => {
    const uniq = new Set();
    activeStations.forEach((s) => {
      if (s?.state) uniq.add(s.state);
    });
    return Array.from(uniq).sort((a, b) => a.localeCompare(b));
  }, [activeStations]);

  const citiesForSelectedState = useMemo(() => {
    if (!selectedState) return [];

    const byCityNumber = new Map();
    for (const s of activeStations) {
      if (s?.state !== selectedState) continue;
      const cityNumber = s?.city_number;
      if (!Number.isFinite(cityNumber)) continue;
      if (!byCityNumber.has(cityNumber)) {
        byCityNumber.set(cityNumber, {
          city_number: cityNumber,
          city: s.city,
          lat: s.lat,
          lon: s.lon,
        });
      }
    }

    return Array.from(byCityNumber.values()).sort((a, b) =>
      String(a.city).localeCompare(String(b.city))
    );
  }, [activeStations, selectedState]);

  const openLabel = selectedState ? "Select City" : "Select State";

  return (
    <Popover className="relative">
      {({ close }) => (
        <>
          <Popover.Button className="flex w-fit flex-row content-center items-center justify-center gap-3 rounded-2xl bg-white px-5 py-3 text-lg font-semibold text-slate-900 ring-1 ring-slate-200 dark:bg-neutral-900 dark:text-slate-100 dark:ring-neutral-700">
            <MapPinIcon className="h-7 w-7 flex-none text-emerald-600 dark:text-emerald-400" />
            <div className="max-w-[18rem] overflow-hidden text-ellipsis whitespace-nowrap">
              {selectedLocation || "Location"}
            </div>
          </Popover.Button>

          <Transition
            as={Fragment}
            enter="transition ease-out duration-150"
            enterFrom="opacity-0 translate-y-1"
            enterTo="opacity-100 translate-y-0"
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100 translate-y-0"
            leaveTo="opacity-0 translate-y-1"
          >
            <Popover.Panel className="absolute left-0 top-full mt-3 z-50 w-[22rem] rounded-2xl bg-white p-4 shadow-lg ring-1 ring-black/5 dark:bg-neutral-900 dark:ring-neutral-800">
              <div className="flex items-center justify-between">
                <div className="text-sm font-black text-slate-700 dark:text-slate-200">
                  {openLabel}
                </div>
                {selectedState && (
                  <button
                    type="button"
                    onClick={() => setSelectedState(null)}
                    className="text-sm font-bold text-emerald-700 hover:text-emerald-800 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    Back
                  </button>
                )}
              </div>

              {!isSuccess ? (
                <div className="mt-3 rounded-xl bg-slate-50 px-4 py-3 text-sm font-bold text-slate-500 dark:bg-neutral-950 dark:text-slate-400">
                  Loading locations…
                </div>
              ) : !selectedState ? (
                <div className="mt-3 max-h-72 overflow-auto">
                  {states.length ? (
                    states.map((stateName) => (
                      <button
                        key={stateName}
                        type="button"
                        onClick={() => setSelectedState(stateName)}
                        className="w-full text-left rounded-xl px-4 py-3 text-sm font-bold text-slate-800 hover:bg-emerald-50 dark:text-slate-100 dark:hover:bg-emerald-900/20"
                      >
                        {stateName}
                      </button>
                    ))
                  ) : (
                    <div className="rounded-xl bg-slate-50 px-4 py-3 text-sm font-bold text-slate-500 dark:bg-neutral-950 dark:text-slate-400">
                      No active stations found.
                    </div>
                  )}
                </div>
              ) : (
                <div className="mt-3 max-h-72 overflow-auto">
                  {citiesForSelectedState.length ? (
                    citiesForSelectedState.map((c) => (
                      <button
                        key={c.city_number}
                        type="button"
                        onClick={() => {
                          dispatch(saveLocation(`${c.city}, Malaysia`));
                          if (Number.isFinite(c.lat) && Number.isFinite(c.lon)) {
                            dispatch(saveGeoCode({ lat: c.lat, lng: c.lon }));
                          }
                          close();
                          setSelectedState(null);
                        }}
                        className="w-full text-left rounded-xl px-4 py-3 text-sm font-bold text-slate-800 hover:bg-emerald-50 dark:text-slate-100 dark:hover:bg-emerald-900/20"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="min-w-0 overflow-hidden text-ellipsis whitespace-nowrap">
                            {c.city}
                          </div>
                          <div className="flex-none text-xs font-black text-slate-400 dark:text-slate-500">
                            #{c.city_number}
                          </div>
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="rounded-xl bg-slate-50 px-4 py-3 text-sm font-bold text-slate-500 dark:bg-neutral-950 dark:text-slate-400">
                      No cities with active stations.
                    </div>
                  )}
                </div>
              )}
            </Popover.Panel>
          </Transition>
        </>
      )}
    </Popover>
  );
}
export default Location;
