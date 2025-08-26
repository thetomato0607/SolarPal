import { useEffect, useState } from "react";

import CloudBackground from "../CloudBackground";
import Header from "../Header";
import Card from "../ui/Card";

import SummaryCard from "./SummaryCard";
import TipCard from "./TipCard";
import ROICard from "./ROICard";
import WeeklyEnergyChart from "../charts/WeeklyEnergyChart";
import PremiumTeaser from "./PremiumTeaser";
import HouseScene from "../HouseScene";
import WeatherCard from "../WeatherCard";

// ✅ single import for services
import { fetchForecast, getWeather, normalizeWeather } from "../../services/solarApi";


function Dashboard({ data, onReset }) {
  const [forecast, setForecast] = useState(null);

  const [weather, setWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState(null);

  const summary = data?.summary ?? data;
  const isPremium = false; // TODO: replace with real auth/subscription

  // ---------------------------
  // 1) WEATHER EFFECT
  // ---------------------------
  useEffect(() => {
    if (!data) return;
    const s = data.summary ?? data;

    // Prefer explicit lat/lon from onboarding; otherwise try browser geolocation
    const lat = s?.lat ?? s?.latitude ?? null;
    const lon = s?.lon ?? s?.longitude ?? null;

    const loadByLatLon = async (lat, lon) => {
      try {
        setWeatherLoading(true);
        setWeatherError(null);
        const raw = await getWeather({ lat, lon, units: "metric" });
        setWeather(normalizeWeather(raw));
      } catch (e) {
        setWeatherError(e?.message || "Failed to load weather");
      } finally {
        setWeatherLoading(false);
      }
    };

    if (typeof lat === "number" && typeof lon === "number") {
      // Use provided coordinates
      loadByLatLon(lat, lon);
      return;
    }

    // Fallback: ask browser for coords
    if ("geolocation" in navigator) {
      setWeatherLoading(true);
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          await loadByLatLon(pos.coords.latitude, pos.coords.longitude);
        },
        (err) => {
          setWeatherLoading(false);
          setWeatherError(err?.message || "Geolocation denied");
        },
        { enableHighAccuracy: false, timeout: 8000 }
      );
    } else {
      setWeatherError("Geolocation unavailable");
    }
  }, [data]);

  // ---------------------------
  // 2) FORECAST EFFECT
  // ---------------------------
  useEffect(() => {
    if (!data) return;
    const s = data.summary ?? data;

    (async () => {
      try {
        const fc = await fetchForecast({
          location: s.location ?? data.location ?? "",
          systemSize: s.system_size_kw ?? 5,
        });
        setForecast(fc);
      } catch (e) {
        console.warn("Forecast failed:", e?.message);
      }
    })();
  }, [data]);

  if (!data) return null;

  return (
    <CloudBackground>
      <Header onReset={onReset} />

      <main style={{ maxWidth: 980, margin: "12px auto 40px", padding: "0 16px" }}>
        <h1 style={{ fontSize: 28, marginBottom: 8 }}>Dashboard</h1>

        {/* Summary + current weather */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SummaryCard userId={summary.user_id} />
          <WeatherCard weather={weather} loading={weatherLoading} error={weatherError} />
        </div>

        <TipCard userId={summary.user_id} />

        <ROICard userId={summary.user_id} />

        {/* Free mini chart */}
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

export default Dashboard;
