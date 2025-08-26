import { useEffect, useMemo, useState } from "react";
import Card from "../ui/Card";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from "recharts";
// If you prefer to call the backend via your service wrapper:
import { fetchForecast } from "../../services/solarApi";

export default function WeeklyEnergyChart({ summary }) {
  const userId = summary?.user_id;
  const systemSize = summary?.system_size_kw ?? 5;
  const [daily, setDaily] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [isNarrow, setIsNarrow] = useState(false);
  const [isShort, setIsShort] = useState(false);

  useEffect(() => {
    if (!userId) return;

    (async () => {
      setLoading(true);
      setErr("");
      try {
        // NOTE: Our backend currently accepts "location" — we’re passing userId as a stand-in.
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

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mqWidth = window.matchMedia("(max-width: 500px)");
    const mqHeight = window.matchMedia("(max-height: 400px)");
    const widthHandler = (e) => setIsNarrow(e.matches);
    const heightHandler = (e) => setIsShort(e.matches);
    widthHandler(mqWidth);
    heightHandler(mqHeight);
    mqWidth.addEventListener("change", widthHandler);
    mqHeight.addEventListener("change", heightHandler);
    return () => {
      mqWidth.removeEventListener("change", widthHandler);
      mqHeight.removeEventListener("change", heightHandler);
    };
  }, []);

  const chartData = useMemo(() => {
    // Normalize to { day: 'Mon', kwh: number }
    return daily.map((d) => ({
      day: formatDay(d.date),
      kwh: Number(d.kwh ?? d.energy_kwh ?? 0),
    }));
  }, [daily]);

  const avgKwh = useMemo(() => {
    if (chartData.length === 0) return 0;
    return (
      chartData.reduce((sum, d) => sum + d.kwh, 0) / chartData.length
    );
  }, [chartData]);

  return (
    <Card>
      <h2 className="mb-2">Weekly Energy Forecast</h2>

      {loading && <p>Loading forecast…</p>}
      {!loading && err && <p>⚠️ {err}</p>}
      {!loading && !err && chartData.length === 0 && <p>No forecast available.</p>}

      {!loading && !err && chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={isShort ? 160 : isNarrow ? 200 : 260}>
          <AreaChart data={chartData} margin={{ top: 10, right: 16, bottom: 0, left: -10 }}>
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
              <ReferenceLine y={avgKwh} stroke="#f87171" strokeDasharray="3 3" />
              <Area
                type="monotone"
                dataKey="kwh"
                stroke="#0ea5e9"
                strokeWidth={2.5}
                fill="url(#kwhGrad)"
              />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
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
