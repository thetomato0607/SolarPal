import { useEffect, useState } from "react";
import { fetchRoi } from "../services/solarApi";

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

    async function loadRoi() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchRoi(userId);
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

    loadRoi();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { roi, loading, error };
}
