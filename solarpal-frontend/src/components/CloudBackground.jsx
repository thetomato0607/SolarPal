import Sun from "./ui/Sun";
import HouseGrid from "./HouseGrid";

export default function CloudBackground({ children }) {
  return (
    <div style={{ minHeight: "100dvh", position: "relative" }}>
      <div style={{ position:"relative", zIndex:1 }}>{children}</div>
    </div>
  );
}
