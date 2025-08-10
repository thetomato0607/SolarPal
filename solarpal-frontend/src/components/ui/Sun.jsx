export default function Sun() {
  return (
    <div
      aria-hidden
      style={{
        position: "absolute",
        top: 40,
        left: "50%",
        width: 84,
        height: 84,
        marginLeft: -42,
        borderRadius: "50%",
        background: "radial-gradient(circle at 30% 30%, #fff7ad, #ffd86b 60%, #ffb84d 100%)",
        boxShadow: "0 0 80px 20px rgba(255, 216, 107, .35)",
        animation: "sunSlide 18s ease-in-out infinite",
        zIndex: 0,
        pointerEvents: "none",
      }}
    />
  );
}
