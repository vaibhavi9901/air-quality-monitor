import { useEffect, useMemo, useRef, useState } from "react";
import { Combobox } from "@headlessui/react";
import { MagnifyingGlassIcon } from "@heroicons/react/20/solid";
import { getGeocode, getLatLng } from "use-places-autocomplete";
import { useDispatch } from "react-redux";
import { saveLocation } from "../../features/search/searchSlice";
import { saveGeoCode } from "../../features/geolocation/geolocationSlice";
import { MALAYSIA_CITIES } from "../../lib/malaysiaCities";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

function SearchBar() {
  const dispatch = useDispatch();
  const [selectedCity, setSelectedCity] = useState(null);
  const [query, setQuery] = useState("");
  const buttonRef = useRef(null);
  const inputRef = useRef(null);

  const filteredCities = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return MALAYSIA_CITIES;
    return MALAYSIA_CITIES.filter((c) => c.toLowerCase().includes(q));
  }, [query]);

  const handleChange = (city) => {
    setSelectedCity(city);
    setQuery("");
    dispatch(saveLocation(`${city}, Malaysia`));
    // Close the dropdown by blurring the input after selection
    inputRef.current?.blur();
  };

  const handleInputFocus = () => {
    buttonRef.current?.click();
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  useEffect(() => {
    if (!selectedCity) return;
    getGeocode({ address: `${selectedCity}, Malaysia` })
      .then((results) => {
        const { lat, lng } = getLatLng(results[0]);
        dispatch(saveGeoCode({ lat, lng }));
      })
      .catch(() => {});
  }, [selectedCity, dispatch]);

  return (
    <Combobox
      as="div"
      onChange={handleChange}
      value={selectedCity}
      className="relative z-50 w-full max-w-[18rem]"
      nullable
    >
      <div className="relative">
        <Combobox.Button
          ref={buttonRef}
          className="absolute inset-0 rounded-2xl"
          style={{ opacity: 0, cursor: "text" }}
          aria-hidden
        />
        <MagnifyingGlassIcon
          className="pointer-events-none absolute top-1/2 -translate-y-1/2 left-5 h-6 w-6 text-slate-400 z-10"
          aria-hidden="true"
        />
        <Combobox.Input
          ref={inputRef}
          type="text"
          autoComplete="off"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={handleInputFocus}
          placeholder="Search city..."
          className="relative z-10 w-full rounded-2xl bg-white py-3 pl-14 pr-4 text-lg font-medium text-slate-900 placeholder-slate-400 outline-none ring-1 ring-slate-200 focus:ring-2 focus:ring-emerald-200 dark:bg-neutral-900 dark:text-slate-100 dark:ring-neutral-700 dark:placeholder-slate-500"
          aria-label="Search city or station"
        />
      </div>
      <Combobox.Options className="absolute left-0 right-0 top-full mt-2 z-50 max-h-72 w-full origin-top overflow-auto scroll-py-2 rounded-2xl bg-white text-base font-medium text-slate-900 shadow-lg ring-1 ring-black/5 dark:bg-neutral-900 dark:ring-neutral-800">
        {filteredCities.length === 0 ? (
          <div className="px-5 py-3 text-slate-500 dark:text-slate-400">No city found.</div>
        ) : (
          filteredCities.map((city) => (
            <Combobox.Option
              key={city}
              value={city}
              className={({ active }) =>
                classNames(
                  "cursor-pointer select-none rounded-xl px-5 py-3",
                  active && "bg-emerald-50 text-slate-900 dark:bg-emerald-900/30 first:rounded-t-none"
                )
              }
            >
              {city}
            </Combobox.Option>
          ))
        )}
      </Combobox.Options>
    </Combobox>
  );
}

export default SearchBar;
