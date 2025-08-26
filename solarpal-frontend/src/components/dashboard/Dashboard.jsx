// src/components/Dashboard.jsx
import { useEffect, useState } from "react";

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

// 3D scene
import HouseScene from "../HouseScene";

export default function Dashboard({ data, onReset }) {
  const [forecast, setForecast] = useState(null);
  const [weather, setWeather] = useState(null);

  const summary = data?.summary ?? data;
  const isPremium = false; // TODO: replace with real auth/subscription

  useEffect(() => {
    if (!data) {
      onReset?.();
      return;
    }

    (async () => {
      try {
        // 1) Fetch solar forecast for charts / future use
        const fc = await fetchForecast({
          location: summary.location ?? data.location ?? "",
          systemSize: summary.system_size_kw ?? 5,
        });
        setForecast(fc);
      } catch (e) {
        console.warn("Forecast failed:", e.message);
      }

      // 2) Fetch live weather for 3D scene (if user allows location)
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            try {
              const w = await getWeather(pos.coords.latitude, pos.coords.longitude);
              setWeather(w);
            } catch (err) {
              console.warn("getWeather failed:", err?.message);
            }
          },
          (err) => {
            console.warn("Geolocation denied:", err?.message);
            // Optional: fallback — use summary.location on backend to fetch weather by name
          },
          { enableHighAccuracy: false, timeout: 8000 }
        );
      }
    })();
  }, [data, onReset, summary?.location, summary?.system_size_kw]);

  if (!data) return null;

  return (
    <CloudBackground>
      <Header onReset={onReset} />

      <main className="max-w-screen-lg mx-auto mt-3 mb-10 px-4 sm:px-6">
        <h1 className="text-2xl sm:text-3xl mb-2">Dashboard</h1>

        <SummaryCard userId={summary.user_id} />
        <TipCard userId={summary.user_id} />


        {/* Free mini chart (synth or real when available) */}
        <WeeklyEnergyChart summary={summary} />

        {/* Interactive 3D house + weather animations */}
        <Card style={{ marginTop: 12, padding: 0 }}>
          <HouseScene height={380} forecast={forecast} weather={weather} />
        </Card>

        {!isPremium && <PremiumTeaser />}
      </main>
    </CloudBackground>
  );
}
