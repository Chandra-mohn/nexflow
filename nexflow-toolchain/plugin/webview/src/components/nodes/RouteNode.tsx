import { Handle, Position } from "@xyflow/react";

interface RouteOutput {
  id: string;
  label: string;
}

interface RouteNodeData {
  label: string;
  condition?: string;
  outputs?: RouteOutput[];
}

interface RouteNodeProps {
  data: RouteNodeData;
}

export function RouteNode({ data }: RouteNodeProps) {
  // Default to 2 outputs (true/false) if not specified
  const outputs = data.outputs || [
    { id: "true", label: "true" },
    { id: "false", label: "false" },
  ];

  const outputCount = outputs.length;
  const handleSpacing = 20; // pixels between handles
  const baseHeight = 60; // minimum node content height
  const nodeHeight = Math.max(baseHeight, outputCount * handleSpacing + 20);

  return (
    <div
      className="nexflow-node nexflow-node-route nexflow-node-multi-output"
      style={{ minHeight: `${nodeHeight}px` }}
    >
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex flex-col flex-1">
        <div className="nexflow-node-label">{data.label}</div>
        <div className="nexflow-node-type">Route</div>

        {data.condition && (
          <div className="text-xs text-amber-300 opacity-70 font-mono max-w-[180px] truncate mt-1">
            when: {data.condition}
          </div>
        )}

        {/* Output labels stacked */}
        <div className="nexflow-output-list">
          {outputs.map((output) => (
            <div key={output.id} className="nexflow-output-label">
              {output.label} →
            </div>
          ))}
        </div>
      </div>

      {/* Stacked source handles on right */}
      {outputs.map((output, index) => {
        const topPercent = ((index + 1) / (outputCount + 1)) * 100;
        return (
          <Handle
            key={output.id}
            type="source"
            position={Position.Right}
            id={output.id}
            style={{ top: `${topPercent}%` }}
          />
        );
      })}
    </div>
  );
}
