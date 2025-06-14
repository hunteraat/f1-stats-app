import { useEffect, useRef } from 'react';

export function useInterval<T>(
  callback: () => T | Promise<T>,
  delay: number | null
) {
  const savedCallback = useRef<() => T | Promise<T>>();

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    function tick() {
      if (savedCallback.current) {
        savedCallback.current();
      }
    }

    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}
