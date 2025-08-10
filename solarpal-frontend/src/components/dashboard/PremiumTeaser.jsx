import Card from "../ui/Card";
import LockBadge from "../ui/LockBadge";

export default function PremiumTeaser() {
  return (
    <Card style={{ marginTop: 12 }}>
      <div style={{ display:"flex", alignItems:"center", gap:10 }}>
        <LockBadge text="Premium" />
        <strong>Unlock full ROI & 30‑day/hourly charts</strong>
      </div>
      <p style={{ margin:"8px 0 0", color:"var(--muted)" }}>
        Try Premium to get detailed cashflow, weather source selection, PDF export, and more.
      </p>
    </Card>
  );
}
