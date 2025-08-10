import Sun from "./ui/Sun";
import HouseGrid from "./HouseGrid";

export default function CloudBackground({ children }) {
  return (
    <div style={{ minHeight: "100dvh", position: "relative", overflow: "hidden" }}>
      {/* soft sky tint */}
      <div style={{
        position:"absolute", inset:0,
        background:"radial-gradient(1200px 600px at 50% -200px, rgba(179,236,255,.6), transparent 70%)",
        pointerEvents:"none"
      }}/>
      {/* fluffy cloud lobes */}
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} style={{
          position:"absolute",
          top: `${-40 + i*18}px`,
          left: `${-80 + i*22}%`,
          width: 320, height: 120, borderRadius: 999, background: "#fff",
          filter: "blur(2px)", opacity: .9,
          boxShadow: "40px 10px 0 0 #fff, 90px 25px 0 0 #fff, 140px 0 0 0 #fff, 190px 18px 0 0 #fff",
          zIndex: 0
        }} />
      ))}

      {/* NEW: Sun & Houses */}
      <Sun />
      <HouseGrid rows={4} cols={14} />

      {/* content layer */}
      <div style={{ position:"relative", zIndex: 1 }}>{children}</div>
    </div>
  );
}
