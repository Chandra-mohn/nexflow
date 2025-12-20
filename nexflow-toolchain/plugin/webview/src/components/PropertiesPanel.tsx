import { useCallback } from "react";
import { Node } from "@xyflow/react";

interface PropertyField {
  key: string;
  label: string;
  type: "text" | "select" | "number" | "checkbox";
  options?: string[];
  placeholder?: string;
}

// Define editable fields per node type
const NODE_FIELDS: Record<string, PropertyField[]> = {
  stream: [
    { key: "label", label: "Name", type: "text", placeholder: "stream_name" },
    { key: "source", label: "Source", type: "text", placeholder: "kafka_topic" },
    { key: "target", label: "Target", type: "text", placeholder: "output_sink" },
    { key: "schema", label: "Schema", type: "text", placeholder: "schema_name" },
    { key: "isOutput", label: "Is Output", type: "checkbox" },
  ],
  "xform-ref": [
    { key: "label", label: "Name", type: "text", placeholder: "transform_name" },
    { key: "transformName", label: "Transform File", type: "text", placeholder: "my_transform" },
  ],
  "rules-ref": [
    { key: "label", label: "Name", type: "text", placeholder: "rules_name" },
    { key: "ruleName", label: "Rules File", type: "text", placeholder: "my_rules" },
  ],
  route: [
    { key: "label", label: "Name", type: "text", placeholder: "route_name" },
    { key: "condition", label: "Condition", type: "text", placeholder: "field > 100" },
  ],
  window: [
    { key: "label", label: "Name", type: "text", placeholder: "window_name" },
    { key: "windowType", label: "Type", type: "select", options: ["tumbling", "sliding", "session"] },
    { key: "size", label: "Size", type: "text", placeholder: "1 minute" },
    { key: "slide", label: "Slide", type: "text", placeholder: "30 seconds" },
    { key: "keyBy", label: "Key By", type: "text", placeholder: "customer_id" },
  ],
  join: [
    { key: "label", label: "Name", type: "text", placeholder: "join_name" },
    { key: "joinType", label: "Type", type: "select", options: ["inner", "left", "right", "full"] },
    { key: "left", label: "Left Stream", type: "text", placeholder: "stream_a" },
    { key: "right", label: "Right Stream", type: "text", placeholder: "stream_b" },
    { key: "within", label: "Within", type: "text", placeholder: "10 seconds" },
  ],
  marker: [
    { key: "label", label: "Name", type: "text", placeholder: "marker_name" },
    { key: "markerName", label: "Marker Type", type: "text", placeholder: "EOD" },
  ],
};

interface ProcessInfo {
  processName: string;
  parallelism?: number;
  timeField?: string;
  watermarkDelay?: string;
}

interface PropertiesPanelProps {
  selectedNode: Node | null;
  processInfo: ProcessInfo;
  onNodeChange: (nodeId: string, data: Record<string, unknown>) => void;
  onProcessChange: (info: Partial<ProcessInfo>) => void;
  onDeleteNode: (nodeId: string) => void;
}

export function PropertiesPanel({
  selectedNode,
  processInfo,
  onNodeChange,
  onProcessChange,
  onDeleteNode,
}: PropertiesPanelProps) {
  const handleFieldChange = useCallback(
    (key: string, value: unknown) => {
      if (selectedNode) {
        const newData = { ...(selectedNode.data as Record<string, unknown>), [key]: value };
        onNodeChange(selectedNode.id, newData);
      }
    },
    [selectedNode, onNodeChange]
  );

  const renderField = (field: PropertyField, value: unknown) => {
    switch (field.type) {
      case "select":
        return (
          <select
            value={String(value || "")}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
          >
            {field.options?.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        );
      case "checkbox":
        return (
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => handleFieldChange(field.key, e.target.checked)}
            className="w-4 h-4"
          />
        );
      case "number":
        return (
          <input
            type="number"
            value={String(value || "")}
            onChange={(e) => handleFieldChange(field.key, Number(e.target.value))}
            placeholder={field.placeholder}
            className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
          />
        );
      default:
        return (
          <input
            type="text"
            value={String(value || "")}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
          />
        );
    }
  };

  // Render process-level properties when no node selected
  if (!selectedNode) {
    return (
      <div className="w-56 border-l border-vscode-border bg-vscode-sidebar overflow-y-auto flex flex-col">
        <div className="h-8 px-3 flex items-center border-b border-vscode-border">
          <span className="text-xs font-semibold text-vscode-fg opacity-70 uppercase tracking-wide">
            Process Config
          </span>
        </div>

        <div className="p-3 space-y-3 flex-1">
          {/* Process Name */}
          <div>
            <label className="block text-xs text-vscode-fg opacity-60 mb-1">Process Name</label>
            <input
              type="text"
              value={processInfo.processName}
              onChange={(e) => onProcessChange({ processName: e.target.value })}
              placeholder="my_process"
              className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
            />
          </div>

          {/* Parallelism */}
          <div>
            <label className="block text-xs text-vscode-fg opacity-60 mb-1">Parallelism</label>
            <input
              type="number"
              value={processInfo.parallelism || ""}
              onChange={(e) => onProcessChange({ parallelism: Number(e.target.value) || undefined })}
              placeholder="4"
              className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
            />
          </div>

          {/* Time Field */}
          <div>
            <label className="block text-xs text-vscode-fg opacity-60 mb-1">Time Field</label>
            <input
              type="text"
              value={processInfo.timeField || ""}
              onChange={(e) => onProcessChange({ timeField: e.target.value || undefined })}
              placeholder="event_timestamp"
              className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
            />
          </div>

          {/* Watermark Delay */}
          <div>
            <label className="block text-xs text-vscode-fg opacity-60 mb-1">Watermark Delay</label>
            <input
              type="text"
              value={processInfo.watermarkDelay || ""}
              onChange={(e) => onProcessChange({ watermarkDelay: e.target.value || undefined })}
              placeholder="5 seconds"
              className="w-full px-2 py-1 text-xs bg-vscode-input text-vscode-input-fg border border-vscode-input-border rounded"
            />
          </div>
        </div>

        <div className="p-2 border-t border-vscode-border">
          <p className="text-xs text-vscode-fg opacity-40 text-center">
            Click a node to edit properties
          </p>
        </div>
      </div>
    );
  }

  // Get fields for this node type
  const nodeType = selectedNode.type || "stream";
  const fields = NODE_FIELDS[nodeType] || [];
  const nodeData = selectedNode.data as Record<string, unknown>;

  return (
    <div className="w-56 border-l border-vscode-border bg-vscode-sidebar overflow-y-auto flex flex-col">
      {/* Header */}
      <div className="h-8 px-3 flex items-center justify-between border-b border-vscode-border">
        <span className="text-xs font-semibold text-vscode-fg opacity-70 uppercase tracking-wide">
          Properties
        </span>
        <button
          onClick={() => onDeleteNode(selectedNode.id)}
          className="text-red-400 hover:text-red-300 text-xs"
          title="Delete node"
        >
          Delete
        </button>
      </div>

      {/* Node type badge */}
      <div className="px-3 py-2 border-b border-vscode-border">
        <span className="inline-block px-2 py-0.5 text-xs rounded bg-vscode-button text-vscode-button-fg">
          {nodeType}
        </span>
        <span className="ml-2 text-xs text-vscode-fg opacity-50">
          {selectedNode.id}
        </span>
      </div>

      {/* Editable fields */}
      <div className="p-3 space-y-3 flex-1">
        {fields.map((field) => (
          <div key={field.key}>
            <label className="block text-xs text-vscode-fg opacity-60 mb-1">
              {field.label}
            </label>
            {renderField(field, nodeData[field.key])}
          </div>
        ))}
      </div>
    </div>
  );
}
