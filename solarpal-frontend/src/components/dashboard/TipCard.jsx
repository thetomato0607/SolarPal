import Card from "../ui/Card";
import useTip from "../../hooks/useTip";

export default function TipCard({ userId }) {
  const { tip, loading, error } = useTip(userId);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Your Solar Tip</h2>
      {loading ? (
        <p>Loading tip…</p>
      ) : error ? (
        <p>⚠️ {error.message || "Couldn’t fetch your solar tip."}</p>
      ) : (
        <p>{tip}</p>
      )}
    </Card>
  );
}

