import { useEffect, useState } from "react";

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

    async function fetchTip() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`http://localhost:8000/tips?user_id=${userId}`);
        const data = await res.json();
        if (!cancelled) {
          setTip(data.tip ?? "No tip available right now.");
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

    fetchTip();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { tip, loading, error };
}
