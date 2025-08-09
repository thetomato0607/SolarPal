// src/components/Onboarding.jsx
import { useState } from "react";
import { fetchSummary } from "../services/solarApi.js";

export default function Onboarding({ onSuccess }) {
  const [form, setForm] = useState({ location: "", systemSize: 5 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Simple validation
    if (!form.location) {
      setError("Please enter your location.");
      return;
    }

    setLoading(true);
    try {
      const data = await fetchSummary(form); // ← calls backend
      onSuccess(data); // ← tells App to go to Dashboard
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: 16 }}>
      <h1>SolarPal Onboarding</h1>

      <label>
        Location
        <input
          name="location"
          value={form.location}
          onChange={onChange}
          placeholder="e.g. Sydney, AU or -33.87,151.21"
        />
      </label>

      <label>
        System Size (kW)
        <input
          name="systemSize"
          type="number"
          min="1"
          step="0.1"
          value={form.systemSize}
          onChange={onChange}
        />
      </label>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Loading..." : "Continue"}
      </button>
    </form>
  );
}
