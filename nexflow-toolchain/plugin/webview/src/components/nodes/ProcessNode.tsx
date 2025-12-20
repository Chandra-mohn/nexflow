import { Handle, Position } from "@xyflow/react";

interface ProcessNodeData {
  label: string;
  opType?: string;
}

interface ProcessNodeProps {
  data: ProcessNodeData;
}

/**
 * Generic process node for operations like transition, emit_audit, etc.
 * Rendered as a compact step in the flow.
 */
export function ProcessNode({ data }: ProcessNodeProps) {
  return (
    <div className="nexflow-node nexflow-node-process">
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex flex-col">
        <div className="nexflow-node-label text-xs">{data.label}</div>
        {data.opType && (
          <div className="nexflow-node-type">{data.opType}</div>
        )}
      </div>

      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}
