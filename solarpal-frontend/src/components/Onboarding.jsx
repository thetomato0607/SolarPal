import { useState } from "react";
import { fetchSummary } from "../services/solarApi";
import Card from "./ui/Card";
import Button from "./ui/Button";
import CloudBackground from "./CloudBackground";

export default function Onboarding({ onSuccess }) {
  const [form, setForm] = useState({ userId: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.userId?.trim()) {
      setError("Please enter your user ID.");
      return;
    }
    setLoading(true);
    try {
      const data = await fetchSummary(form.userId);
      onSuccess(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <CloudBackground>
      <div style={{ maxWidth: 560, margin: "0 auto", padding: "64px 16px" }}>
        <h1 style={{ fontSize: 28, marginBottom: 16 }}>SolarPal Onboarding</h1>
        <Card>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 14 }}>
              <label>User ID</label>
              <input
                name="userId"
                value={form.userId}
                onChange={onChange}
                placeholder="e.g. 12345"
                style={{
                  display: "block", width: "100%", padding: 12, marginTop: 6,
                  borderRadius: 12, border: "1px solid #d7e2eb", outline: "none"
                }}
              />
            </div>

            {error && <p style={{ color: "#b00020", marginTop: 8 }}>{error}</p>}

            <div style={{ marginTop: 16 }}>
              <Button type="submit" disabled={loading}>
                {loading ? "Loading…" : "Continue"}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </CloudBackground>
  );
}
