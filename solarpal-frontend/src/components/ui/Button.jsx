export default function Button({ children, style, ...props }) {
  return (
    <button
      {...props}
      style={{
        background: "linear-gradient(180deg,var(--accent),var(--accent-2))",
        border: "0",
        color: "#083344",
        fontWeight: 700,
        padding: "10px 16px",
        borderRadius: "999px",
        boxShadow: "0 6px 16px rgba(14, 165, 233, .35)",
        cursor: "pointer",
        transition: "transform .06s ease",
        ...style
      }}
      onMouseDown={(e)=>{ e.currentTarget.style.transform='translateY(1px)'; }}
      onMouseUp={(e)=>{ e.currentTarget.style.transform='translateY(0)'; }}
    >
      {children}
    </button>
  );
}
