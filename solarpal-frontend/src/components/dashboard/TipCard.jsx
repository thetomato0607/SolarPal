import Card from "../ui/Card";
import Button from "../ui/Button";
import useTip from "../../hooks/useTip";

export default function TipCard({ userId }) {
  const { tip, loading, error, retry } = useTip(userId);

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Your Solar Tip</h2>
      {loading ? (
        <p>Loading tip…</p>
      ) : error ? (
        <div>
          <p>⚠️ {error?.message || "Couldn’t fetch your solar tip."}</p>
          <Button style={{ marginTop: 8 }} onClick={retry}>
            Retry
          </Button>
        </div>
      ) : (
        <p>{tip}</p>
      )}
    </Card>
  );
}
