import { Handle, Position } from "@xyflow/react";

interface EnrichNodeData {
  label: string;
  lookupName?: string;
  sourceName?: string;
  opType?: string;
}

interface EnrichNodeProps {
  data: EnrichNodeData;
}

/**
 * EnrichNode - represents data enrichment operations (lookup, enrich).
 * Used for enriching stream data from external sources.
 */
export function EnrichNode({ data }: EnrichNodeProps) {
  return (
    <div className="nexflow-node nexflow-node-enrich">
      <Handle type="target" position={Position.Left} id="left" />

      <div className="flex flex-col">
        <div className="nexflow-node-label">{data.label}</div>
        <div className="nexflow-node-type">
          {data.opType === "lookup" ? "Lookup" : "Enrich"}
        </div>
      </div>

      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}
