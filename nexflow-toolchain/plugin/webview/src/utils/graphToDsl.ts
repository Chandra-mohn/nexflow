import { Node, Edge } from "@xyflow/react";

interface ProcessConfig {
  processName: string;
  parallelism?: number;
  timeField?: string;
  watermarkDelay?: string;
}

/**
 * Convert React Flow graph to Nexflow ProcDSL text.
 */
export function graphToDsl(
  nodes: Node[],
  edges: Edge[],
  config: ProcessConfig
): string {
  const lines: string[] = [];

  // Process header
  lines.push(`process ${config.processName || "my_process"}`);

  // Process-level configuration
  if (config.parallelism) {
    lines.push(`    parallelism hint ${config.parallelism}`);
  }

  if (config.timeField) {
    lines.push(`    time by ${config.timeField}`);
    if (config.watermarkDelay) {
      lines.push(`        watermark delay ${config.watermarkDelay}`);
    }
  }

  lines.push(""); // Blank line after config

  // Build adjacency map for topological sort
  const adjacency = new Map<string, string[]>();
  const inDegree = new Map<string, number>();

  nodes.forEach((node) => {
    adjacency.set(node.id, []);
    inDegree.set(node.id, 0);
  });

  edges.forEach((edge) => {
    const targets = adjacency.get(edge.source) || [];
    targets.push(edge.target);
    adjacency.set(edge.source, targets);
    inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
  });

  // Topological sort (Kahn's algorithm)
  const sorted: string[] = [];
  const queue: string[] = [];

  inDegree.forEach((degree, nodeId) => {
    if (degree === 0) {
      queue.push(nodeId);
    }
  });

  while (queue.length > 0) {
    const nodeId = queue.shift()!;
    sorted.push(nodeId);

    const neighbors = adjacency.get(nodeId) || [];
    for (const neighbor of neighbors) {
      const newDegree = (inDegree.get(neighbor) || 0) - 1;
      inDegree.set(neighbor, newDegree);
      if (newDegree === 0) {
        queue.push(neighbor);
      }
    }
  }

  // Generate DSL for each node in topological order
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const emitNodes: Node[] = [];

  for (const nodeId of sorted) {
    const node = nodeMap.get(nodeId);
    if (!node) continue;

    const data = node.data as Record<string, unknown>;
    const nodeType = node.type || "stream";

    switch (nodeType) {
      case "stream":
        if (data.isOutput) {
          // Collect output streams for emit at the end
          emitNodes.push(node);
        } else {
          // Input stream - receive statement
          lines.push(`    receive ${data.label || data.source || "input"}`);
          if (data.source) {
            lines.push(`        from ${data.source}`);
          }
          if (data.schema) {
            lines.push(`        schema ${data.schema}`);
          }
          lines.push("");
        }
        break;

      case "xform-ref":
        lines.push(`    transform using ${data.transformName || data.label || "transform"}`);
        lines.push("");
        break;

      case "rules-ref":
        lines.push(`    route using ${data.ruleName || data.label || "rules"}`);
        // Get outgoing edges to determine routing targets
        const rulesEdges = edges.filter((e) => e.source === nodeId);
        for (const edge of rulesEdges) {
          const targetNode = nodeMap.get(edge.target);
          if (targetNode) {
            const targetData = targetNode.data as Record<string, unknown>;
            const targetLabel = targetData.label || edge.target;
            // Use edge label or infer from target
            lines.push(`        ${edge.label || "result"} to ${targetLabel}`);
          }
        }
        lines.push("");
        break;

      case "route":
        if (data.condition) {
          lines.push(`    when ${data.condition}`);
          // Get outgoing edges
          const routeEdges = edges.filter((e) => e.source === nodeId);
          for (const edge of routeEdges) {
            const targetNode = nodeMap.get(edge.target);
            if (targetNode) {
              const targetData = targetNode.data as Record<string, unknown>;
              lines.push(`        to ${targetData.label || edge.target}`);
            }
          }
          lines.push("");
        }
        break;

      case "window":
        const windowType = data.windowType || "tumbling";
        const size = data.size || "1 minute";
        lines.push(`    window ${windowType} ${size}`);
        if (data.slide) {
          lines.push(`        slide ${data.slide}`);
        }
        if (data.keyBy) {
          lines.push(`        key by ${data.keyBy}`);
        }
        lines.push("");
        break;

      case "join":
        const joinType = data.joinType || "inner";
        lines.push(`    join ${joinType}`);
        if (data.left && data.right) {
          lines.push(`        ${data.left} with ${data.right}`);
        }
        if (data.onFields && Array.isArray(data.onFields) && data.onFields.length > 0) {
          lines.push(`        on ${(data.onFields as string[]).join(", ")}`);
        }
        if (data.within) {
          lines.push(`        within ${data.within}`);
        }
        lines.push("");
        break;

      case "marker":
        lines.push(`    marker ${data.markerName || data.label || "checkpoint"}`);
        lines.push("");
        break;

      case "persist":
        lines.push(`    persist to ${data.storeName || data.label || "store"}`);
        if (data.async !== false) {
          lines.push(`        async`);
        }
        if (data.schema) {
          lines.push(`        schema ${data.schema}`);
        }
        lines.push("");
        break;
    }
  }

  // Generate emit statements for output streams
  for (const node of emitNodes) {
    const data = node.data as Record<string, unknown>;
    lines.push(`    emit to ${data.target || data.label || "output"}`);
    if (data.schema) {
      lines.push(`        schema ${data.schema}`);
    }
  }

  // Close process
  lines.push("end");

  return lines.join("\n");
}

/**
 * Generate a unique node ID.
 */
export function generateNodeId(type: string, existingNodes: Node[]): string {
  const prefix = type.replace("-ref", "");
  const existing = existingNodes.filter((n) => n.id.startsWith(`${prefix}:`));
  let index = existing.length + 1;
  let id = `${prefix}:${prefix}_${index}`;

  // Ensure uniqueness
  while (existingNodes.some((n) => n.id === id)) {
    index++;
    id = `${prefix}:${prefix}_${index}`;
  }

  return id;
}
