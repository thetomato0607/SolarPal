export default function GhostButton({ children, style, ...props }) {
  return (
    <button
      {...props}
      style={{
        background: "transparent",
        border: "1px solid #cfe3ef",
        color: "#0b2a3f",
        padding: "10px 14px",
        borderRadius: 12,
        cursor: "pointer",
        transition: "background .15s",
        ...style
      }}
      onMouseEnter={(e)=>e.currentTarget.style.background="#f3f9fd"}
      onMouseLeave={(e)=>e.currentTarget.style.background="transparent"}
    >
      {children}
    </button>
  );
}
