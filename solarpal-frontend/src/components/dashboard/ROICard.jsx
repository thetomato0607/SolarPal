import Card from "../ui/Card";
import Button from "../ui/Button";
import useRoi from "../../hooks/useRoi";

export default function ROICard({ userId }) {
  const { roi, loading, error, retry } = useRoi(userId);

  let body;
  if (loading) {
    body = <p>Loading ROI…</p>;
  } else if (error) {
    body = (
      <div>
        <p>⚠️ {error?.message || "Failed to fetch ROI data"}</p>
        <Button style={{ marginTop: 8 }} onClick={retry}>
          Retry
        </Button>
      </div>
    );
  } else if (
    !roi ||
    roi.installCost == null ||
    roi.annualSaving == null ||
    roi.tariff == null
  ) {
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
