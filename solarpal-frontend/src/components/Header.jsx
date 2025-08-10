import GhostButton from "./ui/GhostButton";

export default function Header({ onReset }) {
  return (
    <div style={{ 
      display:"flex", alignItems:"center", justifyContent:"space-between",
      padding:"14px 16px", maxWidth:980, margin:"0 auto"
    }}>
      <div style={{ fontWeight:800, letterSpacing:.2, fontSize:20 }}>🌤️ SolarPal</div>
      <GhostButton onClick={onReset}>Reset</GhostButton>
    </div>
  );
}
