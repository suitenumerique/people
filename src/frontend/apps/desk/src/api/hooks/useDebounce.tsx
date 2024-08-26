import { useEffect, useState } from 'react';

const MS_DEBOUNCE = 500;
export const useDebounce = (value: string, delay: number = MS_DEBOUNCE) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};
