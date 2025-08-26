import { useEffect, useState } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

export default function TipCard({ userId }) {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    if (!userId) return;
    try {
      setLoading(true);
      setError("");
      const res = await fetch(`http://localhost:8000/tips?user_id=${userId}`);
      const data = await res.json();
      setTip(data.tip ?? "No tip available right now.");
    } catch (e) {
      console.warn("Failed to load tip:", e);
      setError("Couldn’t fetch your solar tip.");
      setTip(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [userId]);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Your Solar Tip</h2>
      {loading ? (
        <p>Loading tip…</p>
      ) : error ? (
        <div>
          <p>⚠️ {error}</p>
          <Button style={{ marginTop: 8 }} onClick={load}>
            Retry
          </Button>
        </div>
      ) : (
        <p>{tip}</p>
      )}
    </Card>
  );
}
