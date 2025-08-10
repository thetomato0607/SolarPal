import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const api = axios.create({ baseURL, timeout: 15000 });

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

export async function fetchSummary({ location, systemSize }) {
  const res = await api.get("/summary", {
    params: { location, system_size: systemSize },
  });
  return res.data;
}

