import { DragEvent } from "react";

interface PaletteNode {
  type: string;
  label: string;
  icon: string;
  description: string;
  defaultData: Record<string, unknown>;
}

const PALETTE_NODES: PaletteNode[] = [
  {
    type: "stream",
    label: "Stream",
    icon: "📥",
    description: "Input/output data stream",
    defaultData: { label: "new_stream", source: "", schema: "" },
  },
  {
    type: "xform-ref",
    label: "Transform",
    icon: "🔄",
    description: "Apply transformation",
    defaultData: { label: "transform", transformName: "" },
  },
  {
    type: "rules-ref",
    label: "Rules",
    icon: "📋",
    description: "Business rules",
    defaultData: { label: "rules", ruleName: "" },
  },
  {
    type: "route",
    label: "Route",
    icon: "🔀",
    description: "Conditional routing",
    defaultData: { label: "route", condition: "" },
  },
  {
    type: "window",
    label: "Window",
    icon: "🪟",
    description: "Time window aggregation",
    defaultData: { label: "window", windowType: "tumbling", size: "1 minute" },
  },
  {
    type: "join",
    label: "Join",
    icon: "🔗",
    description: "Stream join",
    defaultData: { label: "join", joinType: "inner", onFields: [], within: "10 seconds" },
  },
  {
    type: "persist",
    label: "Persist",
    icon: "🛢️",
    description: "Database sink (MongoDB)",
    defaultData: { label: "persist", storeName: "", schema: "", async: true },
  },
];

interface PaletteProps {
  isCollapsed?: boolean;
  onToggle?: () => void;
}

export function Palette({ isCollapsed = false, onToggle }: PaletteProps) {
  const onDragStart = (event: DragEvent<HTMLDivElement>, node: PaletteNode) => {
    event.dataTransfer.setData("application/reactflow-type", node.type);
    event.dataTransfer.setData("application/reactflow-data", JSON.stringify(node.defaultData));
    event.dataTransfer.effectAllowed = "move";
  };

  if (isCollapsed) {
    return (
      <div className="w-10 bg-vscode-sidebar border-r border-vscode-border flex flex-col items-center py-2">
        <button
          onClick={onToggle}
          className="p-2 text-vscode-fg opacity-60 hover:opacity-100"
          title="Expand palette"
        >
          »
        </button>
        {PALETTE_NODES.map((node) => (
          <div
            key={node.type}
            draggable
            onDragStart={(e) => onDragStart(e, node)}
            className="p-2 cursor-grab text-lg hover:bg-vscode-button hover:bg-opacity-30 rounded"
            title={node.label}
          >
            {node.icon}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="w-48 bg-vscode-sidebar border-r border-vscode-border flex flex-col">
      {/* Header */}
      <div className="h-8 px-3 flex items-center justify-between border-b border-vscode-border">
        <span className="text-xs font-semibold text-vscode-fg opacity-70 uppercase tracking-wide">
          Components
        </span>
        {onToggle && (
          <button
            onClick={onToggle}
            className="text-vscode-fg opacity-60 hover:opacity-100 text-xs"
            title="Collapse palette"
          >
            «
          </button>
        )}
      </div>

      {/* Draggable nodes */}
      <div className="flex-1 p-2 space-y-1 overflow-y-auto">
        {PALETTE_NODES.map((node) => (
          <div
            key={node.type}
            draggable
            onDragStart={(e) => onDragStart(e, node)}
            className="p-2 rounded border border-vscode-border bg-vscode-bg cursor-grab hover:border-vscode-accent transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{node.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-vscode-fg">{node.label}</div>
                <div className="text-xs text-vscode-fg opacity-50 truncate">
                  {node.description}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Help text */}
      <div className="p-2 border-t border-vscode-border">
        <p className="text-xs text-vscode-fg opacity-40 text-center">
          Drag components to canvas
        </p>
      </div>
    </div>
  );
}
