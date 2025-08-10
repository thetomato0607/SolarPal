export default function LockBadge({ text="Premium" }) {
  return (
    <span style={{
      display:"inline-flex", alignItems:"center", gap:6,
      padding:"6px 10px", borderRadius:999, fontSize:12,
      background:"#eef6ff", color:"#0b2a3f", border:"1px solid #cfe3ef"
    }}>
      🔒 {text}
    </span>
  );
}
