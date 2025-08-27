
import { useCallback, useEffect, useState } from "react";
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

  const load = useCallback(async () => {
    if (!userId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await fetchRoi(userId);
      setRoi(data);
    } catch (err) {
      setError(err);
      setRoi(null);
    } finally {
      setLoading(false);
    }

  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  return { roi, loading, error, retry: load };
}
