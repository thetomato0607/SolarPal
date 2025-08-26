import { useEffect, useState } from "react";

/**
 * Fetches ROI information for the user.
 *
 * @param {string} userId - Unique user identifier.
 * @returns {{ roi: object|null, loading: boolean, error: Error|null }}
 *
 * @example
 * const { roi, loading, error } = useRoi(userId);
 */
export default function useRoi(userId) {
  const [roi, setRoi] = useState(null);
  const [loading, setLoading] = useState(Boolean(userId));
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    let cancelled = false;

    async function fetchRoi() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`http://localhost:8000/roi?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to fetch ROI data");
        const data = await res.json();
        if (!cancelled) {
          setRoi(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
          setRoi(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchRoi();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { roi, loading, error };
}
