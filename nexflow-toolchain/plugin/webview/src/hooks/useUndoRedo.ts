/**
 * Undo/Redo Hook for Visual Designer
 *
 * Manages history stack for node/edge state changes.
 * Nodes include their data (configs), so undo/redo captures full state.
 */

import { useCallback, useRef } from "react";
import { Node, Edge } from "@xyflow/react";

interface HistoryState {
  nodes: Node[];
  edges: Edge[];
}

interface UseUndoRedoOptions {
  maxHistory?: number;
}

interface UseUndoRedoReturn {
  // State checks
  canUndo: boolean;
  canRedo: boolean;

  // Actions
  takeSnapshot: (nodes: Node[], edges: Edge[]) => void;
  undo: () => HistoryState | null;
  redo: () => HistoryState | null;
  clear: () => void;

  // Info
  historyLength: number;
  currentIndex: number;
}

export function useUndoRedo(
  options: UseUndoRedoOptions = {}
): UseUndoRedoReturn {
  const { maxHistory = 50 } = options;

  // History stack - array of snapshots
  const historyRef = useRef<HistoryState[]>([]);
  // Current position in history (-1 means no history yet)
  const indexRef = useRef<number>(-1);

  /**
   * Deep clone nodes/edges to avoid reference issues
   */
  const cloneState = useCallback(
    (nodes: Node[], edges: Edge[]): HistoryState => {
      return {
        nodes: JSON.parse(JSON.stringify(nodes)),
        edges: JSON.parse(JSON.stringify(edges)),
      };
    },
    []
  );

  /**
   * Take a snapshot of current state and add to history.
   * Called after each user action that modifies nodes/edges.
   */
  const takeSnapshot = useCallback(
    (nodes: Node[], edges: Edge[]) => {
      const history = historyRef.current;
      const currentIndex = indexRef.current;

      // If we're not at the end of history, truncate future states
      if (currentIndex < history.length - 1) {
        history.splice(currentIndex + 1);
      }

      // Add new snapshot
      const snapshot = cloneState(nodes, edges);
      history.push(snapshot);

      // Trim history if exceeds max
      if (history.length > maxHistory) {
        history.shift();
      } else {
        indexRef.current = history.length - 1;
      }
    },
    [cloneState, maxHistory]
  );

  /**
   * Undo - go back one step in history
   */
  const undo = useCallback((): HistoryState | null => {
    const history = historyRef.current;
    const currentIndex = indexRef.current;

    if (currentIndex <= 0) {
      return null; // Nothing to undo
    }

    indexRef.current = currentIndex - 1;
    const previousState = history[indexRef.current];

    return cloneState(previousState.nodes, previousState.edges);
  }, [cloneState]);

  /**
   * Redo - go forward one step in history
   */
  const redo = useCallback((): HistoryState | null => {
    const history = historyRef.current;
    const currentIndex = indexRef.current;

    if (currentIndex >= history.length - 1) {
      return null; // Nothing to redo
    }

    indexRef.current = currentIndex + 1;
    const nextState = history[indexRef.current];

    return cloneState(nextState.nodes, nextState.edges);
  }, [cloneState]);

  /**
   * Clear all history
   */
  const clear = useCallback(() => {
    historyRef.current = [];
    indexRef.current = -1;
  }, []);

  return {
    canUndo: indexRef.current > 0,
    canRedo: indexRef.current < historyRef.current.length - 1,
    takeSnapshot,
    undo,
    redo,
    clear,
    historyLength: historyRef.current.length,
    currentIndex: indexRef.current,
  };
}
