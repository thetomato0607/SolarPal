
import { useCallback, useEffect, useState } from "react";
import { fetchSummary } from "../services/solarApi";

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

  const load = useCallback(async () => {
    if (!userId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await fetchSummary(userId);
      setSummary(data);
    } catch (err) {
      setError(err);
      setSummary(null);
    } finally {
      setLoading(false);
    }

  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  return { summary, loading, error, retry: load };
}
