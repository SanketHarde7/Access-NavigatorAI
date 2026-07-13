import { useRef, useCallback, useEffect } from "react";

/**
 * useTilt — mouse-tracked 3D perspective tilt for glass cards.
 * Returns a ref to attach to the element and handlers for mouse events.
 * Sets CSS vars --tilt-x, --tilt-y, --tilt-glare-x, --tilt-glare-y.
 */
export function useTilt<T extends HTMLElement = HTMLDivElement>(maxTilt = 8) {
  const ref = useRef<T>(null);

  const onMove = useCallback(
    (e: React.MouseEvent<T>) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width; // 0..1
      const y = (e.clientY - rect.top) / rect.height; // 0..1
      const tiltY = (x - 0.5) * 2 * maxTilt; // -max..max
      const tiltX = -(y - 0.5) * 2 * maxTilt;
      el.style.setProperty("--tilt-x", `${tiltX}deg`);
      el.style.setProperty("--tilt-y", `${tiltY}deg`);
      el.style.setProperty("--tilt-glare-x", `${x * 100}%`);
      el.style.setProperty("--tilt-glare-y", `${y * 100}%`);
    },
    [maxTilt]
  );

  const onLeave = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--tilt-x", "0deg");
    el.style.setProperty("--tilt-y", "0deg");
    el.style.setProperty("--tilt-glare-x", "50%");
    el.style.setProperty("--tilt-glare-y", "50%");
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => onLeave();
  }, [onLeave]);

  return { ref, onMouseMove: onMove, onMouseLeave: onLeave };
}
