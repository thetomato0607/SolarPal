// src/components/Dashboard.jsx
import { useEffect, useState, useCallback } from "react";

// services
import { fetchForecast, getWeather } from "../../services/solarApi";

// layout / ui
import CloudBackground from "../CloudBackground";
import Header from "../Header";
import Card from "../ui/Card";

// dashboard pieces
import SummaryCard from "./SummaryCard";
import TipCard from "./TipCard";
import WeeklyEnergyChart from "../charts/WeeklyEnergyChart";
import PremiumTeaser from "./PremiumTeaser";
import ErrorBoundary from "../ui/ErrorBoundary";

// 3D scene
import HouseScene from "../HouseScene";

export default function Dashboard({ data, onReset }) {
  const [forecast, setForecast] = useState(null);
  const [weather, setWeather] = useState(null);
  const [forecastErr, setForecastErr] = useState("");
  const [weatherErr, setWeatherErr] = useState("");

  const summary = data?.summary ?? data;
  const isPremium = false; // TODO: replace with real auth/subscription

  const loadData = useCallback(async () => {
    if (!data) {
      onReset?.();
      return;
    }
    setForecastErr("");
    setWeatherErr("");
    try {
      const fc = await fetchForecast({
        location: summary.location ?? data.location ?? "",
        systemSize: summary.system_size_kw ?? 5,
      });
      setForecast(fc);
    } catch (e) {
      setForecastErr(e.message);
    }

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          try {
            const w = await getWeather(pos.coords.latitude, pos.coords.longitude);
            setWeather(w);
          } catch (err) {
            setWeatherErr(err.message);
          }
        },
        (err) => {
          setWeatherErr(err.message);
        },
        { enableHighAccuracy: false, timeout: 8000 }
      );
    }
  }, [data, onReset, summary?.location, summary?.system_size_kw]);

  useEffect(() => {
    if (data) loadData();
  }, [data, loadData]);

  if (!data) return null;

  return (
    <ErrorBoundary>
      <CloudBackground>
        <Header onReset={onReset} />

        <main style={{ maxWidth: 980, margin: "12px auto 40px", padding: "0 16px" }}>
          <h1 style={{ fontSize: 28, marginBottom: 8 }}>Dashboard</h1>

          <SummaryCard userId={summary.user_id} />
          <TipCard userId={summary.user_id} />

          {/* Free mini chart (synth or real when available) */}
          <WeeklyEnergyChart summary={summary} />

          {/* Interactive 3D house + weather animations */}
          <Card style={{ marginTop: 12, padding: 0 }}>
            {forecastErr || weatherErr ? (
              <div style={{ padding: 16 }}>
                <p>⚠️ {forecastErr || weatherErr}</p>
                <button onClick={loadData}>Retry</button>
              </div>
            ) : (
              <HouseScene height={380} forecast={forecast} weather={weather} />
            )}
          </Card>

          {!isPremium && <PremiumTeaser />}
        </main>
      </CloudBackground>
    </ErrorBoundary>
  );
}
