import { create } from "zustand";

export interface ProcessConfig {
  processName: string;
  parallelism?: number;
  timeField?: string;
  watermarkDelay?: string;
}

interface CanvasState {
  // Process info
  processName: string;
  filePath: string | null;
  processConfig: ProcessConfig;

  // Selection
  selectedNodeId: string | null;
  selectedEdgeId: string | null;

  // Canvas state
  isDirty: boolean;
  isPaletteCollapsed: boolean;

  // Actions
  setProcessName: (name: string) => void;
  setFilePath: (path: string | null) => void;
  setProcessConfig: (config: Partial<ProcessConfig>) => void;
  setSelectedNode: (id: string | null) => void;
  setSelectedEdge: (id: string | null) => void;
  setDirty: (dirty: boolean) => void;
  clearSelection: () => void;
  togglePalette: () => void;
  resetCanvas: () => void;
}

const initialProcessConfig: ProcessConfig = {
  processName: "new_process",
  parallelism: 4,
  timeField: "",
  watermarkDelay: "",
};

export const useCanvasStore = create<CanvasState>((set) => ({
  // Initial state
  processName: "",
  filePath: null,
  processConfig: { ...initialProcessConfig },
  selectedNodeId: null,
  selectedEdgeId: null,
  isDirty: false,
  isPaletteCollapsed: false,

  // Actions
  setProcessName: (name) =>
    set((state) => ({
      processName: name,
      processConfig: { ...state.processConfig, processName: name },
    })),
  setFilePath: (path) => set({ filePath: path }),
  setProcessConfig: (config) =>
    set((state) => ({
      processConfig: { ...state.processConfig, ...config },
      isDirty: true,
    })),
  setSelectedNode: (id) => set({ selectedNodeId: id, selectedEdgeId: null }),
  setSelectedEdge: (id) => set({ selectedEdgeId: id, selectedNodeId: null }),
  setDirty: (dirty) => set({ isDirty: dirty }),
  clearSelection: () => set({ selectedNodeId: null, selectedEdgeId: null }),
  togglePalette: () => set((state) => ({ isPaletteCollapsed: !state.isPaletteCollapsed })),
  resetCanvas: () =>
    set({
      processName: "new_process",
      filePath: null,
      processConfig: { ...initialProcessConfig },
      selectedNodeId: null,
      selectedEdgeId: null,
      isDirty: false,
    }),
}));
