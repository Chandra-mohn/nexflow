import { Handle, Position } from "@xyflow/react";
import { vscodeApi } from "../../vscode";

interface TransformRefNodeData {
  label: string;
  transformName: string;
}

interface TransformRefNodeProps {
  data: TransformRefNodeData;
}

export function TransformRefNode({ data }: TransformRefNodeProps) {
  const handleOpenTransform = () => {
    vscodeApi.postMessage({
      type: "openTransform",
      name: data.transformName,
    });
  };

  return (
    <div className="nexflow-node nexflow-node-xform-ref">
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex items-center gap-2">
        <span className="text-lg">🔄</span>
        <div>
          <div className="nexflow-node-label">{data.label}</div>
          <div className="nexflow-node-type">Transform</div>
        </div>
      </div>

      <button
        onClick={handleOpenTransform}
        className="mt-2 text-xs text-green-300 hover:text-green-100 underline"
      >
        Open in VS Code →
      </button>

      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}
