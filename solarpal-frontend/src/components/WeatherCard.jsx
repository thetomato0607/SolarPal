import { useMemo } from "react";
import PropTypes from "prop-types";
import Card from "./ui/Card";

/**
 * WeatherCard
 * Props:
 *  - weather: { tempC, condition, iconUrl, windKph?, humidity? }
 *  - loading: boolean
 *  - error: string | null
 */
export default function WeatherCard({ weather, loading, error }) {
  const body = useMemo(() => {
    if (loading) return <p className="opacity-70">Loading weather…</p>;
    if (error)   return <p className="text-red-600">Weather error: {String(error)}</p>;
    if (!weather) return <p className="opacity-70">No weather data.</p>;

    return (
      <div className="flex items-center gap-4">
        {weather.iconUrl && (
          <img
            src={weather.iconUrl}
            alt={weather.condition ?? "Weather"}
            width={56}
            height={56}
            loading="lazy"
          />
        )}
        <div className="flex-1">
          <div className="text-2xl font-semibold">
            {Number.isFinite(weather.tempC) ? Math.round(weather.tempC) : "–"}°C
          </div>
          <div className="text-sm opacity-80">{weather.condition ?? "—"}</div>
          <div className="text-xs opacity-60 mt-1">
            {Number.isFinite(weather.windKph) ? `Wind ${Math.round(weather.windKph)} kph` : null}
            {Number.isFinite(weather.windKph) && Number.isFinite(weather.humidity) ? " • " : null}
            {Number.isFinite(weather.humidity) ? `Humidity ${Math.round(weather.humidity)}%` : null}
          </div>
        </div>
      </div>
    );
  }, [loading, error, weather]);

  return (
    <Card title="Current Weather">
      {body}
    </Card>
  );
}

WeatherCard.propTypes = {
  weather: PropTypes.shape({
    tempC: PropTypes.number,
    condition: PropTypes.string,
    iconUrl: PropTypes.string,
    windKph: PropTypes.number,
    humidity: PropTypes.number,
  }),
  loading: PropTypes.bool,
  error: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};
