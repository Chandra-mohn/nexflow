import { StreamNode } from "./StreamNode";
import { TransformRefNode } from "./TransformRefNode";
import { RulesRefNode } from "./RulesRefNode";
import { RouteNode } from "./RouteNode";
import { WindowNode } from "./WindowNode";
import { JoinNode } from "./JoinNode";
import { MarkerNode } from "./MarkerNode";
import { ProcessNode } from "./ProcessNode";
import { EnrichNode } from "./EnrichNode";
import { PersistNode } from "./PersistNode";

export const nodeTypes = {
  stream: StreamNode,
  "xform-ref": TransformRefNode,
  "rules-ref": RulesRefNode,
  route: RouteNode,
  window: WindowNode,
  join: JoinNode,
  marker: MarkerNode,
  process: ProcessNode,
  enrich: EnrichNode,
  persist: PersistNode,
};
