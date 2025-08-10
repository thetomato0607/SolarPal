import Card from "../ui/Card";

export default function TipCard({ tip }) {
  if (!tip) return null;
  return (
    <Card style={{ marginTop: 12 }}>
      <h3 style={{ marginBottom: 8 }}>Tip</h3>
      <p style={{ margin: 0, color: "var(--ink)" }}>{tip}</p>
    </Card>
  );
}
