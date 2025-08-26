export default function GhostButton({ children, style, className = "", ...props }) {
  return (
    <button
      {...props}
      className={`bg-transparent border border-[#cfe3ef] text-[#0b2a3f] px-3 py-2 rounded-xl transition-colors hover:bg-[#f3f9fd] ${className}`}
      style={style}
    >
      {children}
    </button>
  );
}
