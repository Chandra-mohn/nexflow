import { Handle, Position } from "@xyflow/react";

interface StreamNodeData {
  label: string;
  source?: string;
  target?: string;
  alias?: string;
  schema?: string;
  isOutput?: boolean;
}

interface StreamNodeProps {
  data: StreamNodeData;
}

export function StreamNode({ data }: StreamNodeProps) {
  const isInput = !data.isOutput;

  return (
    <div className="nexflow-node nexflow-node-stream nexflow-node-pipe">
      {/* Input streams have source handle on right, output streams have target on left */}
      {!isInput && <Handle type="target" position={Position.Left} id="left" />}

      <div className="flex flex-col">
        <span className="nexflow-pipe-label">{data.label}</span>
        {data.schema && (
          <span className="nexflow-pipe-meta">{data.schema}</span>
        )}
      </div>

      {isInput && <Handle type="source" position={Position.Right} id="right" />}
    </div>
  );
}
