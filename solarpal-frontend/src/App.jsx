import { useEffect, useState } from "react";
import Onboarding from "./components/Onboarding";
import Dashboard from "./components/Dashboard";
import { loadState, saveState, clearState } from "./lib/storage";

export default function App() {
  const [appStage, setAppStage] = useState("onboarding"); // 'onboarding' | 'dashboard'
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const saved = loadState();
    if (saved?.appStage && saved?.dashboardData) {
      setAppStage(saved.appStage);
      setDashboardData(saved.dashboardData);
    }
  }, []);

  useEffect(() => {
    saveState({ appStage, dashboardData });
  }, [appStage, dashboardData]);

  const handleOnboardingSuccess = (data) => {
    setDashboardData(data);
    setAppStage("dashboard");
  };

  const handleReset = () => {
    setDashboardData(null);
    setAppStage("onboarding");
    clearState();
  };

  return appStage === "onboarding" ? (
    <Onboarding onSuccess={handleOnboardingSuccess} />
  ) : (
    <Dashboard data={dashboardData} onReset={handleReset} />
  );
}
