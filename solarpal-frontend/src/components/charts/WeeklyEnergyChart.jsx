import { useEffect, useMemo, useState } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
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

export default function WeeklyEnergyChart({ userId, systemSize, forecast }) {
  const [daily, setDaily] = useState(
    () => (Array.isArray(forecast?.daily) ? forecast.daily : [])
  );
  const [loading, setLoading] = useState(!Array.isArray(forecast?.daily));
  const [err, setErr] = useState("");
  const [isNarrow, setIsNarrow] = useState(false);
  const [isPhone, setIsPhone] = useState(false);
  const [isShort, setIsShort] = useState(false);

  const load = async () => {
    if (!userId) return;
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
  };

  useEffect(() => {
    if (Array.isArray(forecast?.daily)) {
      setDaily(forecast.daily);
      setLoading(false);
    } else {
      load();
    }
  }, [userId, systemSize, forecast]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mqPhone = window.matchMedia("(max-width: 375px)");
    const mqWidth = window.matchMedia("(max-width: 500px)");
    const mqHeight = window.matchMedia("(max-height: 400px)");
    const phoneHandler = (e) => setIsPhone(e.matches);
    const widthHandler = (e) => setIsNarrow(e.matches);
    const heightHandler = (e) => setIsShort(e.matches);
    phoneHandler(mqPhone);
    widthHandler(mqWidth);
    heightHandler(mqHeight);
    mqPhone.addEventListener("change", phoneHandler);
    mqWidth.addEventListener("change", widthHandler);
    mqHeight.addEventListener("change", heightHandler);
    return () => {
      mqPhone.removeEventListener("change", phoneHandler);
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
      {!loading && err && (
        <div>
          <p>⚠️ {err}</p>
          <Button style={{ marginTop: 8 }} onClick={load}>
            Retry
          </Button>
        </div>
      )}
      {!loading && !err && chartData.length === 0 && <p>No forecast available.</p>}

      {!loading && !err && chartData.length > 0 && (
        <ResponsiveContainer
          width="100%"
          height={isShort ? 160 : isPhone ? 180 : isNarrow ? 200 : 260}
        >
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
