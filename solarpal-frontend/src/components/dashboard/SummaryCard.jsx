import Card from "../ui/Card";
import useSummary from "../../hooks/useSummary";

export default function SummaryCard({ userId }) {
  const { summary, loading, error } = useSummary(userId);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>System Summary</h2>
      {loading ? (
        <p>Loading summary…</p>
      ) : error || !summary ? (
        <p>⚠️ Couldn’t fetch your summary.</p>
      ) : (
        <ul style={{ lineHeight: 1.6 }}>
          <li><b>User ID:</b> {summary.user_id}</li>
          <li><b>Daily Savings:</b> £{summary.daily_saving_gbp}</li>
          <li><b>CO₂ Offset:</b> {summary.co2_offset_kg} kg</li>
          <li><b>Battery:</b> {summary.battery_status}</li>
          <li><b>Message:</b> {summary.message}</li>
        </ul>
      )}
    </Card>
  );
}
