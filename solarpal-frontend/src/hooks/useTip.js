
import { useCallback, useEffect, useState } from "react";
import { fetchTip } from "../services/solarApi";

/**
 * Retrieves a personalised solar tip for the user.
 *
 * @param {string} userId - Unique user identifier.
 * @returns {{ tip: string|null, loading: boolean, error: Error|null }}
 *
 * @example
 * const { tip, loading, error } = useTip(userId);
 */
export default function useTip(userId) {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(Boolean(userId));
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!userId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTip(userId);
      setTip(data ?? "No tip available right now.");
    } catch (err) {
      setError(err);
      setTip(null);
    } finally {
      setLoading(false);
    }

  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  return { tip, loading, error, retry: load };
}
