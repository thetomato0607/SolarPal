import { useEffect, useState } from "react";
import Card from "../ui/Card";
import { fetchTip } from "../../services/solarApi";

export default function TipCard({ userId }) {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    const loadTip = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchTip(userId);
        setTip(data ?? "No tip available right now.");
      } catch (e) {
        console.warn("Failed to load tip:", e);
        setError(e.message || "Couldn’t fetch your solar tip.");
        setTip(null);
      } finally {
        setLoading(false);
      }
    };

    loadTip();
  }, [userId]);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Your Solar Tip</h2>
      {loading ? (
        <p>Loading tip…</p>
      ) : error ? (
        <p>⚠️ {error}</p>
      ) : (
        <p>{tip}</p>
      )}
    </Card>
  );
}
