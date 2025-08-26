import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const api = axios.create({ baseURL, timeout: 15000 });

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg =
      err?.response?.data?.error ||
      err?.response?.data?.message ||
      err?.message ||
      "Network error";
    return Promise.reject(new Error(msg));
  }
);

// Used by Onboarding
export async function fetchSummary({ location, systemSize }) {
  const res = await api.get("/summary", {
    params: { location, system_size: systemSize },
  });
  return res.data;
}

// Used by Dashboard – solar forecast for charts / future use
export async function fetchForecast({ location, systemSize }) {
  const res = await api.get("/forecast", {
    params: { location, system_size: systemSize },
  });
  return res.data;
}

// Used by 3D weather scene – live weather by coordinates
export async function getWeather(lat, lon) {
  const res = await api.get("/weather", { params: { lat, lon } });
  return res.data;
}

export async function fetchForecast({ location, systemSize }) {
  // If your router is prefixed (e.g., /solar/forecast), update the path here.
  const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  const res = await fetch(
    `${baseURL}/forecast?location=${encodeURIComponent(location)}&system_size=${systemSize}`
  );
  if (!res.ok) throw new Error("Forecast request failed");
  return res.json();
}

export function normalizeWeather(openWeatherJson) {
  if (!openWeatherJson) return null;
  const ow = openWeatherJson;

  const icon = ow?.weather?.[0]?.icon; // e.g. "10d"
  const iconUrl = icon ? `https://openweathermap.org/img/wn/${icon}@2x.png` : null;

  return {
    tempC: typeof ow?.main?.temp === "number" ? ow.main.temp : undefined,
    condition: ow?.weather?.[0]?.main || ow?.weather?.[0]?.description || "—",
    iconUrl,
    windKph: typeof ow?.wind?.speed === "number" ? ow.wind.speed * 3.6 : undefined, // m/s → kph
    humidity: typeof ow?.main?.humidity === "number" ? ow.main.humidity : undefined,
  };
}