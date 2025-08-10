import Card from "../ui/Card";

export default function SummaryCard({ summary }) {
  const rows = [
    ["Location", summary?.location ?? "—"],
    ["System size", (summary?.system_size_kw ?? "—") + (summary?.system_size_kw ? " kW" : "")],
    ["Est. daily yield", (summary?.estimated_daily_kwh ?? "—") + (summary?.estimated_daily_kwh ? " kWh" : "")]
  ];
  return (
    <Card style={{ marginTop: 12 }}>
      <h2 style={{ marginBottom: 10 }}>Summary</h2>
      <div style={{ display:"grid", gap:10 }}>
        {rows.map(([k,v])=>(
          <div key={k} style={{ display:"flex", justifyContent:"space-between" }}>
            <span style={{ color:"var(--muted)" }}>{k}</span>
            <strong>{v}</strong>
          </div>
        ))}
      </div>
    </Card>
  );
}
