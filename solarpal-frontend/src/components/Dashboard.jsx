// src/components/Dashboard.jsx
import { useEffect } from "react";

export default function Dashboard({ data, onReset }) {
  // Guard: if no data, go back
  useEffect(() => {
    if (!data) {
      onReset();
    }
  }, [data, onReset]);

  if (!data) return null; // brief empty render during redirect

  return (
    <div style={{ padding: 16 }}>
      <h1>Dashboard</h1>

      <section>
        <h2>Summary</h2>
        <pre>{JSON.stringify(data.summary ?? data, null, 2)}</pre>
      </section>

      {data.tip && (
        <section>
          <h3>Tip</h3>
          <p>{data.tip}</p>
        </section>
      )}

      <button onClick={onReset}>Reset</button>
    </div>
  );
}
