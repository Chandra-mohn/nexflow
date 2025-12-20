import { Handle, Position } from "@xyflow/react";

interface WindowNodeData {
  label: string;
  windowType: string;
  size: string;
  slide?: string;
  keyBy?: string;
}

interface WindowNodeProps {
  data: WindowNodeData;
}

export function WindowNode({ data }: WindowNodeProps) {
  return (
    <div className="nexflow-node nexflow-node-window">
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex items-center gap-2">
        <span className="text-lg">🪟</span>
        <div>
          <div className="nexflow-node-label">{data.label}</div>
          <div className="nexflow-node-type">Window</div>
        </div>
      </div>

      <div className="mt-2 text-xs text-cyan-300 opacity-70">
        <div>
          {data.windowType} - {data.size}
        </div>
        {data.slide && <div>slide: {data.slide}</div>}
        {data.keyBy && <div>key: {data.keyBy}</div>}
      </div>

      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}
