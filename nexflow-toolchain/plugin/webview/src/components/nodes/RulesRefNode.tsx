import { Handle, Position } from "@xyflow/react";
import { vscodeApi } from "../../vscode";

interface RulesOutput {
  id: string;
  label: string;
}

interface RulesRefNodeData {
  label: string;
  ruleName: string;
  outputs?: RulesOutput[];
}

interface RulesRefNodeProps {
  data: RulesRefNodeData;
}

export function RulesRefNode({ data }: RulesRefNodeProps) {
  const handleOpenRules = () => {
    vscodeApi.postMessage({
      type: "openRules",
      name: data.ruleName,
    });
  };

  // Default to 2 outputs if not specified
  const outputs = data.outputs || [
    { id: "out1", label: "match" },
    { id: "out2", label: "no_match" },
  ];

  const outputCount = outputs.length;
  const handleSpacing = 20; // pixels between handles
  const baseHeight = 60; // minimum node content height
  const nodeHeight = Math.max(baseHeight, outputCount * handleSpacing + 20);

  return (
    <div
      className="nexflow-node nexflow-node-rules-ref nexflow-node-multi-output"
      style={{ minHeight: `${nodeHeight}px` }}
    >
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex flex-col flex-1">
        <div className="nexflow-node-label">{data.label}</div>
        <div className="nexflow-node-type">Rules</div>

        {/* Output labels stacked on right side */}
        <div className="nexflow-output-list">
          {outputs.map((output) => (
            <div key={output.id} className="nexflow-output-label">
              {output.label} →
            </div>
          ))}
        </div>

        <button
          onClick={handleOpenRules}
          className="mt-auto text-xs text-purple-300 hover:text-purple-100 underline"
        >
          Open in VS Code
        </button>
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
