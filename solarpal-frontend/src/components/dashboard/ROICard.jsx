import Card from "../ui/Card";
import useRoi from "../../hooks/useRoi";

// Assumes backend /roi endpoint returns {
//   installCost: number,       // upfront cost in GBP
//   annualSaving: number,      // yearly energy generation in kWh
//   tariff: number             // feed-in tariff in GBP per kWh
// }
// A simple ROI is calculated as:
//   paybackYears = installCost / (annualSaving * tariff)
// ROI% is the yearly return relative to install cost.
export default function ROICard({ userId }) {
  const { roi, loading, error } = useRoi(userId);

  const annualReturn = roi?.annualSaving * roi?.tariff;
  const paybackYears = annualReturn ? roi?.installCost / annualReturn : Infinity;
  const roiPercent = roi?.installCost
    ? (annualReturn / roi.installCost) * 100
    : 0;

  return (
    <Card>
      <h2 style={{ marginBottom: 8 }}>Return on Investment</h2>
      {loading ? (
        <p>Loading ROI…</p>
      ) : error ? (
        <p>⚠️ {error?.message || "Couldn’t fetch ROI data."}</p>
      ) : !roi ||
        roi.installCost == null ||
        roi.annualSaving == null ||
        roi.tariff == null ? (
        <p>ROI data unavailable.</p>
      ) : (
        <ul style={{ lineHeight: 1.6 }}>
          <li>
            <b>ROI:</b> {isFinite(roiPercent) ? `${roiPercent.toFixed(1)}%` : "—"}
          </li>
          <li>
            <b>Payback:</b> {isFinite(paybackYears) ? `${paybackYears.toFixed(1)} yrs` : "—"}
          </li>
        </ul>
      )}
    </Card>
  );
}
