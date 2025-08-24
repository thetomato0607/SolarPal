import { useEffect, useState } from "react";
import Card from "../ui/Card";

export default function TipCard({ userId }) {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;

    const fetchTip = async () => {
      try {
        setLoading(true);
        const res = await fetch(`http://localhost:8000/tips?user_id=${userId}`);
        const data = await res.json();
        setTip(data.tip ?? "No tip available right now.");
      } catch (e) {
        console.warn("Failed to load tip:", e);
        setTip("⚠️ Couldn’t fetch your solar tip.");
      } finally {
        setLoading(false);
      }
    };

    fetchTip();
  }, [userId]);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Your Solar Tip</h2>
      {loading ? (
        <p>Loading tip…</p>
      ) : (
        <p>{tip}</p>
      )}
    </Card>
  );
}
