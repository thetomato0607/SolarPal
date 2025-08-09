// src/services/solarApi.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta?.env?.VITE_API_BASE_URL || process.env.REACT_APP_API_BASE_URL || "http://localhost:8000", // adjust if needed
  timeout: 15000,
});

// OPTIONAL: axios error normalization
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err?.response?.data?.error ||
      err?.response?.data?.message ||
      err?.message ||
      "Network error";
    return Promise.reject(new Error(message));
  }
);

// Adjust endpoint to your FastAPI route
export async function fetchSummary({ location, systemSize }) {
  // You can convert "location" to lat/lon in backend or send as-is.
  // Example: GET /summary?location=...&system_size=...
  const res = await api.get("/summary", {
    params: { location, system_size: systemSize },
  });
  return res.data; // should be the "dashboardData"
}
