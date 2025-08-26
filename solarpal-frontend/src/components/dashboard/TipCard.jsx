import Card from "../ui/Card";
import useTip from "../../hooks/useTip";

export default function TipCard({ userId }) {
  const { tip, loading, error } = useTip(userId);
import { fetchTip } from "../../services/solarApi";

export default function TipCard({ userId }) {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
