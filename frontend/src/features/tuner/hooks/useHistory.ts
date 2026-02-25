import { useState, useCallback, useRef } from 'react';
import type { IconConfig } from '../../../types/tuner';

interface HistoryState {
  entries: { config: IconConfig; description: string }[];
  currentIndex: number;
}

const MAX_HISTORY = 50;

export function useHistory() {
  const stateRef = useRef<HistoryState>({ entries: [], currentIndex: -1 });
  const [, setTick] = useState(0);
  const rerender = () => setTick(t => t + 1);

  const push = useCallback((config: IconConfig, description: string) => {
    const state = stateRef.current;
    // Remove any future entries (redo stack)
    const entries = state.entries.slice(0, state.currentIndex + 1);
    entries.push({ config: structuredClone(config), description });
    // Trim to max
    if (entries.length > MAX_HISTORY) {
      entries.shift();
    }
    stateRef.current = { entries, currentIndex: entries.length - 1 };
    rerender();
  }, []);

  const undo = useCallback((): IconConfig | null => {
    const state = stateRef.current;
    if (state.currentIndex <= 0) return null;
    const newIndex = state.currentIndex - 1;
    stateRef.current = { ...state, currentIndex: newIndex };
    rerender();
    return structuredClone(state.entries[newIndex].config);
  }, []);

  const redo = useCallback((): IconConfig | null => {
    const state = stateRef.current;
    if (state.currentIndex >= state.entries.length - 1) return null;
    const newIndex = state.currentIndex + 1;
    stateRef.current = { ...state, currentIndex: newIndex };
    rerender();
    return structuredClone(state.entries[newIndex].config);
  }, []);

  const reset = useCallback((config: IconConfig) => {
    stateRef.current = {
      entries: [{ config: structuredClone(config), description: 'Initial' }],
      currentIndex: 0,
    };
    rerender();
  }, []);

  const state = stateRef.current;

  return {
    push,
    undo,
    redo,
    reset,
    canUndo: state.currentIndex > 0,
    canRedo: state.currentIndex < state.entries.length - 1,
  };
}
