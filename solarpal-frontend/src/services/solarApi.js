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

async function retryRequest(fn, attempts = 3, delay = 500) {
  try {
    return await fn();
  } catch (err) {
    if (attempts <= 1) throw err;
    await new Promise((r) => setTimeout(r, delay));
    return retryRequest(fn, attempts - 1, delay * 2);
  }
}

// Used by Onboarding and Dashboard summary card
export async function fetchSummary(userId, attempts = 3) {
  return retryRequest(
    () =>
      api
        .get("/summary", { params: { user_id: userId } })
        .then((r) => r.data?.summary ?? r.data),
    attempts
  );
}

// Dashboard – helpful solar tip for the user
export async function fetchTip(userId, attempts = 3) {
  return retryRequest(
    () =>
      api
        .get("/tips", { params: { user_id: userId } })
        .then((r) => r.data?.tip ?? r.data),
    attempts
  );
}

// Dashboard – ROI metrics
export async function fetchRoi(userId, attempts = 3) {
  return retryRequest(
    () =>
      api
        .get("/roi", { params: { user_id: userId } })
        .then((r) => r.data),
    attempts
  );
}

// Used by Dashboard – solar forecast for charts / future use
export async function fetchForecast({ location, systemSize }, attempts = 3) {
  return retryRequest(
    () =>
      api
        .get("/forecast", { params: { location, system_size: systemSize } })
        .then((r) => r.data),
    attempts
  );
}

// Used by 3D weather scene – live weather by coordinates
export async function getWeather({ lat, lon, units }, attempts = 3) {
  return retryRequest(
    () => api.get("/weather", { params: { lat, lon, units } }).then((r) => r.data),
    attempts
  );
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