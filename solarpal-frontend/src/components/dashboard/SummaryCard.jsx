import { useEffect, useState } from "react";
import Card from "../ui/Card";

export default function SummaryCard({ userId }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;

    const fetchSummary = async () => {
      try {
        setLoading(true);
        const res = await fetch(`http://localhost:8000/summary?user_id=${userId}`);
        const data = await res.json();
        setSummary(data.summary ?? data); // handle both wrapped & raw
      } catch (e) {
        console.warn("Failed to load summary:", e);
        setSummary(null);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [userId]);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>System Summary</h2>
      {loading ? (
        <p>Loading summary…</p>
      ) : !summary ? (
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
