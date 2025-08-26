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
export async function fetchSummary(userId) {
  const res = await api.get("/summary", {
    params: { user_id: userId },
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
