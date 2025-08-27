import { useEffect, useState } from "react";

import CloudBackground from "../CloudBackground";
import Header from "../Header";
import Card from "../ui/Card";
import ErrorBoundary from "../ui/ErrorBoundary";

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

  const fetchWeatherData = async () => {
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
      await loadByLatLon(lat, lon);
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
  };

  useEffect(() => {
    fetchWeatherData();
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

      <main className="mx-auto max-w-screen-lg px-4 mt-3 mb-10 space-y-4 md:space-y-6">
        <h1 className="mb-2 text-2xl md:text-[28px]">Dashboard</h1>

        {/* Summary + current weather */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ErrorBoundary>
            <SummaryCard userId={summary.user_id} />
          </ErrorBoundary>
          <ErrorBoundary>
            <WeatherCard
              weather={weather}
              loading={weatherLoading}
              error={weatherError}
              onRetry={fetchWeatherData}
            />
          </ErrorBoundary>
        </div>

        <ErrorBoundary>
          <TipCard userId={summary.user_id} />
        </ErrorBoundary>

        <ErrorBoundary>
          <ROICard userId={summary.user_id} />
        </ErrorBoundary>

        {/* Free mini chart */}
        <ErrorBoundary>
          <WeeklyEnergyChart
            userId={summary.user_id}
            systemSize={summary.system_size_kw ?? 5}
          />
        </ErrorBoundary>

        {/* Interactive 3D house + weather animations */}
        <ErrorBoundary>
          <Card style={{ padding: 0 }}>
            <HouseScene height={380} forecast={forecast} weather={weather} />
          </Card>
        </ErrorBoundary>

        {!isPremium && <PremiumTeaser />}
      </main>
    </CloudBackground>
  );
}

export default Dashboard;
