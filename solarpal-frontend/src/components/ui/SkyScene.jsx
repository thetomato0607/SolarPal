import { useEffect, useState } from "react";

export default function SkyScene() {
  const [hour, setHour] = useState(new Date().getHours());
  const [weather, setWeather] = useState("Clear"); // Placeholder
  const [windSpeed, setWindSpeed] = useState(1);

  // Update time every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setHour(new Date().getHours());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Example weather fetch (use your actual API logic here)
  useEffect(() => {
    async function fetchWeather() {
      try {
        const response = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?lat=51.5&lon=-0.12&appid=a30bc04d7493bfcd2df55de88529c4b0`
        );
        const data = await response.json();
        setWeather(data.weather[0].main); // e.g. Clear, Clouds, Rain
        setWindSpeed(data.wind?.speed || 1);
      } catch (error) {
        console.error("Weather fetch failed", error);
      }
    }

    fetchWeather();
  }, []);

  // Gradient by time
  const getGradient = () => {
    if (hour < 6 || hour > 19) return "from-[#23243C] to-[#373759]"; // Night
    if (hour < 9) return "from-[#FFF6CC] to-[#FFE9B0]"; // Morning
    if (hour < 16) return "from-[#FFDB7F] to-[#FFFAE1]"; // Day
    return "from-[#FFAD84] to-[#FCD7D7]"; // Sunset
  };

  // Sun position (0% = far left, 100% = far right)
  const sunPosition = `${((hour - 6) / 12) * 100}%`; // 6am–6pm

  const showClouds = weather.includes("Cloud") || weather === "Rain";

  return (
    <div
      className={`relative w-full min-h-[50vh] bg-gradient-to-b ${getGradient()} transition-all duration-1000 ease-in-out overflow-hidden`}
    >
      {/* ☀️ Sun */}
      <div
        className="absolute top-10 w-16 h-16 rounded-full bg-yellow-300 shadow-lg"
        style={{
          left: sunPosition,
          transition: "left 1s ease",
        }}
      ></div>

      {/* ☁️ Clouds */}
      {showClouds && (
        <div
          className="absolute top-16 left-0 w-full h-20 animate-clouds pointer-events-none"
          style={{
            animationDuration: `${20 - windSpeed * 2}s`,
          }}
        >
          <div className="w-24 h-12 bg-white rounded-full opacity-60 blur-sm mx-auto animate-pulse" />
        </div>
      )}

      {/* Optional rain overlay later */}
    </div>
  );
}
