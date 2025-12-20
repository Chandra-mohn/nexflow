import { Node, Edge } from "@xyflow/react";

interface LayoutConfig {
  nodeWidth: number;
  nodeHeight: number;
  horizontalGap: number;
  laneHeight: number;
  startX: number;
  startY: number;
}

const DEFAULT_CONFIG: LayoutConfig = {
  nodeWidth: 150,
  nodeHeight: 60,
  horizontalGap: 80,
  laneHeight: 100,
  startX: 50,
  startY: 50,
};

interface NodeLaneInfo {
  lane: number;
  column: number;
  nodeId: string;
}

/**
 * Apply train-lane layout to nodes.
 * - Main flow stays on lane 0
 * - Branches from rules/route nodes go to new lanes
 * - All nodes in same lane have same Y position
 */
export function applyTrainLaneLayout(
  nodes: Node[],
  edges: Edge[],
  config: Partial<LayoutConfig> = {}
): Node[] {
  const cfg = { ...DEFAULT_CONFIG, ...config };

  if (nodes.length === 0) return nodes;

  // Build adjacency maps
  const outgoing = new Map<string, { target: string; sourceHandle?: string }[]>();
  const incoming = new Map<string, string[]>();

  nodes.forEach((n) => {
    outgoing.set(n.id, []);
    incoming.set(n.id, []);
  });

  edges.forEach((e) => {
    outgoing.get(e.source)?.push({ target: e.target, sourceHandle: e.sourceHandle || undefined });
    incoming.get(e.target)?.push(e.source);
  });

  // Find root nodes (no incoming edges)
  const roots = nodes.filter((n) => (incoming.get(n.id)?.length || 0) === 0);

  // Track lane assignments
  const nodeLaneInfo = new Map<string, NodeLaneInfo>();
  let nextLane = 0;
  let maxColumn = 0;

  // BFS to assign lanes and columns
  function assignLanes(startNodes: Node[], startLane: number, startColumn: number) {
    const queue: { nodeId: string; lane: number; column: number }[] = [];

    startNodes.forEach((n, idx) => {
      const lane = startLane + idx;
      queue.push({ nodeId: n.id, lane, column: startColumn });
      nextLane = Math.max(nextLane, lane + 1);
    });

    while (queue.length > 0) {
      const { nodeId, lane, column } = queue.shift()!;

      // Skip if already assigned (take the first assignment)
      if (nodeLaneInfo.has(nodeId)) continue;

      nodeLaneInfo.set(nodeId, { nodeId, lane, column });
      maxColumn = Math.max(maxColumn, column);

      const node = nodes.find((n) => n.id === nodeId);
      const targets = outgoing.get(nodeId) || [];

      // Check if this is a branching node (rules/route)
      const isBranchingNode = node?.type === "rules-ref" || node?.type === "route";

      if (isBranchingNode && targets.length > 1) {
        // First output stays on current lane, others get new lanes
        targets.forEach((t, idx) => {
          if (idx === 0) {
            // Primary output stays on same lane
            queue.push({ nodeId: t.target, lane, column: column + 1 });
          } else {
            // Secondary outputs go to new lanes
            queue.push({ nodeId: t.target, lane: nextLane, column: column + 1 });
            nextLane++;
          }
        });
      } else {
        // Non-branching: all targets continue on same lane
        targets.forEach((t) => {
          queue.push({ nodeId: t.target, lane, column: column + 1 });
        });
      }
    }
  }

  // Start layout from root nodes
  if (roots.length > 0) {
    assignLanes(roots, 0, 0);
  } else {
    // Fallback: start from first node
    assignLanes([nodes[0]], 0, 0);
  }

  // Handle any unassigned nodes (disconnected components)
  nodes.forEach((n) => {
    if (!nodeLaneInfo.has(n.id)) {
      nodeLaneInfo.set(n.id, { nodeId: n.id, lane: nextLane, column: 0 });
      nextLane++;
    }
  });

  // Apply positions based on lane assignments
  return nodes.map((node) => {
    const info = nodeLaneInfo.get(node.id);
    if (!info) return node;

    // Stream nodes are shorter - adjust Y position for vertical centering
    const isStream = node.type === "stream";

    // Calculate position
    const x = cfg.startX + info.column * (cfg.nodeWidth + cfg.horizontalGap);
    const y = cfg.startY + info.lane * cfg.laneHeight + (isStream ? 15 : 0); // Center streams vertically

    return {
      ...node,
      position: { x, y },
    };
  });
}

/**
 * Get the lane number for a node.
 */
export function getNodeLane(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): number {
  const layoutNodes = applyTrainLaneLayout(nodes, edges);
  const node = layoutNodes.find((n) => n.id === nodeId);
  return node?.position.y || 0;
}
