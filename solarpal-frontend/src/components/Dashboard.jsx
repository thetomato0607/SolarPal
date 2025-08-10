import { useEffect } from "react";
import CloudBackground from "./CloudBackground";
import Header from "./Header";
import SummaryCard from "./dashboard/SummaryCard";
import TipCard from "./dashboard/TipCard";
import WeeklyEnergyChart from "./charts/WeeklyEnergyChart";
import PremiumTeaser from "./dashboard/PremiumTeaser";

export default function Dashboard({ data, onReset }) {
  useEffect(() => { if (!data) onReset(); }, [data, onReset]);
  if (!data) return null;

  const summary = data.summary ?? data;
  const isPremium = false; // TODO: replace with real auth/subscription

  return (
    <CloudBackground>
      <Header onReset={onReset} />
      <main style={{ maxWidth: 980, margin: "12px auto 40px", padding: "0 16px" }}>
        <h1 style={{ fontSize: 28, marginBottom: 8 }}>Dashboard</h1>

        <SummaryCard summary={summary} />
        <TipCard tip={data.tip} />
        <WeeklyEnergyChart summary={summary} />

        {!isPremium && <PremiumTeaser />}
      </main>
    </CloudBackground>
  );
}
