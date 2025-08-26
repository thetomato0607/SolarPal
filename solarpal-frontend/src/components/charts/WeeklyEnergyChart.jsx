import { useEffect, useMemo, useState } from "react";
import Card from "../ui/Card";
import {
  ResponsiveContainer,
  LineChart, Line,
  XAxis, YAxis,
  Tooltip, CartesianGrid
} from "recharts";
import { fetchForecast } from "../../services/solarApi";

export default function WeeklyEnergyChart({ userId, systemSize = 5 }) {
  const [daily, setDaily] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!userId) return;
    (async () => {
      setLoading(true); setErr("");
      try {
        // If your FastAPI router is mounted at /solar, change to call that in solarApi.js
        const data = await fetchForecast({ location: userId, systemSize });
        setDaily(Array.isArray(data?.daily) ? data.daily : []);
      } catch (e) {
        setErr(e?.message || "Failed to load forecast");
        setDaily([]);
      } finally {
        setLoading(false);
      }
    })();
  }, [userId, systemSize]);

  const chartData = useMemo(() => (
    daily.map(d => ({
      day: toWeekday(d.date),
      kwh: Number(d.kwh ?? 0)
    }))
  ), [daily]);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Weekly Energy Forecast</h2>

      {loading && <p>Loading forecast…</p>}
      {!loading && err && <p>⚠️ {err}</p>}
      {!loading && !err && chartData.length === 0 && <p>No forecast available.</p>}

      {!loading && !err && chartData.length > 0 && (
        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.35} />
              <XAxis dataKey="day" />
              <YAxis tickFormatter={(v) => `${v}`} />
              <Tooltip formatter={(v) => [`${v} kWh`, "Energy"]} />
              <Line
                type="monotone"
                dataKey="kwh"
                stroke="#0ea5e9"
                strokeWidth={2.2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}

function toWeekday(dateStr) {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { weekday: "short" }); // Mon, Tue …
  } catch { return dateStr || ""; }
}
