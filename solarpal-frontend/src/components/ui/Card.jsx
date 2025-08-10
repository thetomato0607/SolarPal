export default function Card({ children, style }) {
  return (
    <div
      style={{
        background: "var(--card)",
        borderRadius: "var(--radius)",
        boxShadow: "var(--shadow)",
        padding: 20,
        ...style
      }}
    >
      {children}
    </div>
  );
}
