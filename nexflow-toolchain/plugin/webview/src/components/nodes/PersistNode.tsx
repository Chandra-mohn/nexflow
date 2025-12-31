import { Handle, Position } from "@xyflow/react";

interface PersistNodeData {
  label: string;
  storeName: string;
  schema?: string;
  async?: boolean;
}

interface PersistNodeProps {
  data: PersistNodeData;
}

export function PersistNode({ data }: PersistNodeProps) {
  return (
    <div className="nexflow-node nexflow-node-persist">
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex items-center gap-2">
        <span className="text-lg">🛢️</span>
        <div>
          <div className="nexflow-node-label">{data.label}</div>
          <div className="nexflow-node-type">
            Persist{data.async !== false ? " (async)" : ""}
          </div>
        </div>
      </div>

      {data.schema && (
        <div className="nexflow-node-meta mt-1">{data.schema}</div>
      )}

      {/* Persist is a sink - no output handle */}
    </div>
  );
}
