import { useEffect, useMemo, useState, useCallback } from "react";
import Card from "../ui/Card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
// If you prefer to call the backend via your service wrapper:
import { fetchForecast } from "../../services/solarApi";
import ErrorBoundary from "../ui/ErrorBoundary";

export default function WeeklyEnergyChart({ summary, userId, systemSize = 5 }) {
  const [daily, setDaily] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const uid = userId ?? summary?.user_id;

  const loadForecast = useCallback(async () => {
    if (!uid) return;
    setLoading(true);
    setErr("");
    try {
      // NOTE: Our backend currently accepts "location" — we’re passing userId as a stand-in.
      const data = await fetchForecast({ location: uid, systemSize });
      setDaily(Array.isArray(data?.daily) ? data.daily : []);
    } catch (e) {
      setErr(e?.message || "Failed to load forecast");
      setDaily([]);
    } finally {
      setLoading(false);
    }
  }, [uid, systemSize]);

  useEffect(() => {
    loadForecast();
  }, [loadForecast]);

  const chartData = useMemo(() => {
    // Normalize to { day: 'Mon', kwh: number }
    return daily.map((d) => ({
      day: formatDay(d.date),
      kwh: Number(d.kwh ?? d.energy_kwh ?? 0),
    }));
  }, [daily]);

  return (
    <ErrorBoundary>
      <Card>
        <h2 style={{ marginBottom: 8 }}>Weekly Energy Forecast</h2>

        {loading && <p>Loading forecast…</p>}
        {!loading && err && (
          <div>
            <p>⚠️ {err}</p>
            <button onClick={loadForecast}>Retry</button>
          </div>
        )}
        {!loading && !err && chartData.length === 0 && <p>No forecast available.</p>}

        {!loading && !err && chartData.length > 0 && (
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={chartData} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
                <defs>
                  <linearGradient id="kwhGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0ea5e9" stopOpacity={0.9} />
                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0.2} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.4} />
                <XAxis dataKey="day" />
                <YAxis tickFormatter={(v) => `${v}`} />
                <Tooltip formatter={(v) => [`${v} kWh`, "Energy"]} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="kwh"
                  stroke="#0ea5e9"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>
    </ErrorBoundary>
  );
}

function formatDay(dateStr) {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { weekday: "short" }); // Mon, Tue…
  } catch {
    return dateStr ?? "";
  }
}
