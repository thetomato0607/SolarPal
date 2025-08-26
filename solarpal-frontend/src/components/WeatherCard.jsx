import PropTypes from "prop-types";
import Card from "./ui/Card";
import Button from "./ui/Button";

/**
 * WeatherCard
 * Props:
 *  - weather: { tempC, condition, iconUrl, windKph?, humidity? }
 *  - loading: boolean
 *  - error: string | null
 */
export default function WeatherCard({ weather, loading, error, onRetry }) {
  let body;
  if (loading) {
    body = <p className="opacity-70">Loading weather…</p>;
  } else if (error) {
    body = (
      <div>
        <p className="text-red-600">Weather error: {String(error)}</p>
        {onRetry && (
          <Button style={{ marginTop: 8 }} onClick={onRetry}>
            Retry
          </Button>
        )}
      </div>
    );
  } else if (!weather) {
    body = <p className="opacity-70">No weather data.</p>;
  } else {
    body = (
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
  }

  return <Card title="Current Weather">{body}</Card>;
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
  onRetry: PropTypes.func,
};
