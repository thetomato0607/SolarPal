import { useEffect, useState } from "react";
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

  useEffect(() => {
    if (!userId) return;

    let cancelled = false;

    async function loadTip() {
      try {
        setLoading(true);
        setError(null);
        const tipText = await fetchTip(userId);
        if (!cancelled) {
          setTip(tipText ?? "No tip available right now.");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
          setTip(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadTip();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { tip, loading, error };
}
