import { BaseNode } from "./BaseNode";

interface MarkerNodeData {
  label: string;
  markerName: string;
  condition?: {
    type?: string;
  };
}

interface MarkerNodeProps {
  data: MarkerNodeData;
}

export function MarkerNode({ data }: MarkerNodeProps) {
  return (
    <BaseNode
      label={data.label}
      type="marker"
      typeLabel="EOD Marker"
      icon="🚩"
      className="nexflow-node-marker"
      handles={{ left: false, right: false }}
    >
      {data.condition && (
        <div className="mt-2 text-xs text-red-300 opacity-70">
          {data.condition.type || "condition"}
        </div>
      )}
    </BaseNode>
  );
}
