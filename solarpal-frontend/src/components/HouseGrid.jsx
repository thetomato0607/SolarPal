// Cute bottom “neighborhood” – light DOM, good perf
export default function HouseGrid({ rows = 4, cols = 14 }) {
  const tiles = Array.from({ length: rows * cols });

  return (
    <div
      aria-hidden
      style={{
        position: "absolute",
        inset: "auto 0 0 0",
        height: rows * 56 + 24,     // tile size * rows + padding
        padding: "12px 16px 16px",
        background:
          "linear-gradient(180deg, rgba(255,255,255,0), rgba(210,234,255,.5) 40%, rgba(198,228,255,.8))",
        backdropFilter: "blur(1px)",
        zIndex: 0,
        overflow: "hidden",
      }}
    >
      <div
        className="house-shadow"
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gap: 10,
          maxWidth: 1200,
          margin: "0 auto",
          transform: "translateY(6px)",
        }}
      >
        {tiles.map((_, i) => (
          <House key={i} i={i} />
        ))}
      </div>
    </div>
  );
}

function House({ i }) {
  // slight variance so the grid feels alive
  const hue = 200 + ((i * 11) % 40);         // blue/teal roofs
  const bobDelay = (i % 7) * 0.15;
  const shineDelay = (i % 9) * 0.35;

  return (
    <div
      style={{
        width: 56,
        height: 38,
        borderRadius: 10,
        background: "#fff",
        position: "relative",
        animation: `bob 3.6s ${bobDelay}s ease-in-out infinite`,
        transformOrigin: "50% 100%",
      }}
    >
      {/* roof */}
      <div
        style={{
          position: "absolute",
          top: -10,
          left: -2,
          right: -2,
          height: 18,
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
          background: `linear-gradient(180deg, hsl(${hue} 95% 78%), hsl(${hue} 90% 64%))`,
          border: "1px solid rgba(8,40,60,.08)",
        }}
      />
      {/* door */}
      <div
        style={{
          position: "absolute",
          bottom: 6,
          left: 8,
          width: 10,
          height: 14,
          borderRadius: 3,
          background: "#0b2a3f",
          opacity: .9,
        }}
      />
      {/* window */}
      <div
        style={{
          position: "absolute",
          bottom: 10,
          right: 8,
          width: 14,
          height: 10,
          borderRadius: 3,
          background: "linear-gradient(180deg, #fff 0%, #e2f3ff 100%)",
          boxShadow: "inset 0 0 0 1px rgba(8,42,63,.08)",
        }}
      />
      {/* roof shine sweep */}
      <div
        style={{
          position: "absolute",
          top: -10,
          left: -2,
          right: -2,
          height: 18,
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12,
          background:
            "linear-gradient(90deg, transparent, rgba(255,255,255,.7), transparent)",
          backgroundSize: "120px 100%",
          animation: `shine 3.8s ${shineDelay}s ease-in-out infinite`,
          pointerEvents: "none",
        }}
      />
    </div>
  );
}
