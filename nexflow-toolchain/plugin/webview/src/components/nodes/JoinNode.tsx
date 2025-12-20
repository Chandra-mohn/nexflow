import { Handle, Position } from "@xyflow/react";

interface JoinNodeData {
  label: string;
  left: string;
  right: string;
  onFields: string[];
  within: string;
  joinType: string;
}

interface JoinNodeProps {
  data: JoinNodeData;
}

export function JoinNode({ data }: JoinNodeProps) {
  return (
    <div className="nexflow-node nexflow-node-join">
      <Handle type="target" position={Position.Left} id="left" />
      <Handle type="target" position={Position.Top} id="top" />

      <div className="flex items-center gap-2">
        <span className="text-lg">🔗</span>
        <div>
          <div className="nexflow-node-label">{data.label}</div>
          <div className="nexflow-node-type">{data.joinType} Join</div>
        </div>
      </div>

      <div className="mt-2 text-xs text-pink-300 opacity-70">
        <div>on: {data.onFields?.join(", ")}</div>
        <div>within: {data.within}</div>
      </div>

      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}
