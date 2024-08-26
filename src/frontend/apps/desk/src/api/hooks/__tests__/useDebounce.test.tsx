import { act, renderHook } from '@testing-library/react';

import { useDebounce } from '../useDebounce';

jest.useFakeTimers();

describe('useDebounce', () => {
  it('should return the initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial value'));

    expect(result.current).toBe('initial value');
  });

  it('should return debounced value after default 500ms delay', () => {
    const { result, rerender } = renderHook(({ value }) => useDebounce(value), {
      initialProps: { value: 'initial' },
    });

    expect(result.current).toBe('initial');

    rerender({ value: 'updated' });

    expect(result.current).toBe('initial');

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('should reset the debounce timer if value changes before delay', () => {
    const { result, rerender } = renderHook(({ value }) => useDebounce(value), {
      initialProps: { value: 'initial' },
    });

    expect(result.current).toBe('initial');

    rerender({ value: 'updated' });
    rerender({ value: 'updated again' });

    // Fast forward 400ms (less than debounce delay), value should still be 'initial'
    act(() => {
      jest.advanceTimersByTime(400);
    });

    expect(result.current).toBe('initial');

    // Fast forward 500ms (total: 900ms), value should be 'updated again'
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated again');
  });
});
