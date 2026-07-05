import { useEffect, useRef } from "react";

/** Runs `fn` on an interval; pass `enabled=false` to pause. */
export function usePolling(fn: () => void | Promise<void>, intervalMs: number, enabled = true) {
  const saved = useRef(fn);
  useEffect(() => {
    saved.current = fn;
  }, [fn]);
  useEffect(() => {
    if (!enabled) return;
    const id = setInterval(() => {
      void saved.current();
    }, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, enabled]);
}
