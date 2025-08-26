import CloudBackground from "../CloudBackground";
import Header from "../Header";
import SummaryCard from "./SummaryCard";
import ROICard from "./ROICard";
import TipCard from "./TipCard";
import PremiumTeaser from "./PremiumTeaser";

export default function Dashboard({ data, onReset }) {
  const userId = data?.user_id;

  return (
    <CloudBackground>
      <Header onReset={onReset} />
      <div
        style={{
          maxWidth: 560,
          margin: "0 auto",
          padding: "32px 16px",
          display: "flex",
          flexDirection: "column",
          gap: 20
        }}
      >
        <SummaryCard userId={userId} />
        <ROICard userId={userId} />
        <TipCard userId={userId} />
        <PremiumTeaser />
      </div>
    </CloudBackground>
  );
}

