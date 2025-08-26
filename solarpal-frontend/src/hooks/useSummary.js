import { useEffect, useState } from "react";

/**
 * Fetches the system summary for a given user.
 *
 * @param {string} userId - Unique user identifier.
 * @returns {{ summary: object|null, loading: boolean, error: Error|null }}
 *
 * @example
 * const { summary, loading, error } = useSummary("abc123");
 */
export default function useSummary(userId) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(Boolean(userId));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    let cancelled = false;

    async function fetchSummary() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`http://localhost:8000/summary?user_id=${userId}`);
        const data = await res.json();
        if (!cancelled) {
          setSummary(data.summary ?? data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
          setSummary(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchSummary();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { summary, loading, error };
}
