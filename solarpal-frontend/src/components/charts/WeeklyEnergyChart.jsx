import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import Card from "../ui/Card";

// If backend doesn’t provide 7-day data yet, we synthesize simple variation.
function synthesize(data) {
  const base = Number(data?.estimated_daily_kwh ?? 10);
  const factors = [0.95, 1.05, 1.0, 0.9, 1.1, 1.02, 0.98];
  const labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  return labels.map((d, i) => ({ day: d, kwh: Math.round(base * factors[i] * 10)/10 }));
}

export default function WeeklyEnergyChart({ summary }) {
  const points = synthesize(summary);
  return (
    <Card style={{ marginTop: 12 }}>
      <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
        <span>📈</span><strong>7‑day energy preview</strong>
      </div>
      <div style={{ width:"100%", height:260 }}>
        <ResponsiveContainer>
          <LineChart data={points} margin={{ top: 4, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis unit=" kWh" />
            <Tooltip formatter={(v)=>[`${v} kWh`,"Energy"]} />
            <Line type="monotone" dataKey="kwh" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
