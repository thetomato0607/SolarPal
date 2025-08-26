import { useEffect, useState } from "react";
import Card from "../ui/Card";

// Assumes backend /roi endpoint returns {
//   installCost: number,       // upfront cost in GBP
//   annualSaving: number,      // yearly energy generation in kWh
//   tariff: number             // feed-in tariff in GBP per kWh
// }
// A simple ROI is calculated as:
//   paybackYears = installCost / (annualSaving * tariff)
// ROI% is the yearly return relative to install cost.
export default function ROICard({ userId }) {
  const [roi, setRoi] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;

    const fetchRoi = async () => {
      try {
        setLoading(true);
        const res = await fetch(`http://localhost:8000/roi?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to fetch ROI data");
        const data = await res.json();
        setRoi(data);
      } catch (e) {
        console.warn("Failed to load ROI:", e);
        setRoi(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRoi();
  }, [userId]);

  let body;
  if (loading) {
    body = <p>Loading ROI…</p>;
  } else if (!roi || roi.installCost == null || roi.annualSaving == null || roi.tariff == null) {
    body = <p>ROI data unavailable.</p>;
  } else {
    const annualReturn = roi.annualSaving * roi.tariff;
    const paybackYears = annualReturn ? roi.installCost / annualReturn : Infinity;
    const roiPercent = roi.installCost ? (annualReturn / roi.installCost) * 100 : 0;

    body = (
      <ul style={{ lineHeight: 1.6 }}>
        <li><b>ROI:</b> {isFinite(roiPercent) ? `${roiPercent.toFixed(1)}%` : "—"}</li>
        <li><b>Payback:</b> {isFinite(paybackYears) ? `${paybackYears.toFixed(1)} yrs` : "—"}</li>
      </ul>
    );
  }

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Return on Investment</h2>
      {body}
    </Card>
  );
}
