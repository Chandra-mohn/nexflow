# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Graph Converter Module

Converts Process AST to UI-consumable graph format for React Flow canvas.
Node IDs follow convention: {type}:{name}

Extracted from parse.py for maintainability.
"""

import hashlib
import json
from typing import Any


def ast_to_graph(ast: Any) -> str:
    """
    Convert Process AST to UI-consumable graph format.

    Returns JSON with nodes and edges for React Flow canvas.
    Node IDs follow convention: {type}:{name}
    """
    from ...ast.proc.program import Program, ProcessDefinition

    # Handle Program wrapper - get first process
    if isinstance(ast, Program):
        if not ast.processes:
            return json.dumps({"error": "No processes found"}, indent=2)
        proc = ast.processes[0]
    elif isinstance(ast, ProcessDefinition):
        proc = ast
    else:
        return json.dumps({"error": f"Unexpected AST type: {type(ast).__name__}"}, indent=2)

    return json.dumps(_process_to_graph(proc), indent=2)


def _flatten_operations(operations: list, depth: int = 0) -> list:
    """
    Flatten nested operations (branch/parallel bodies, on_success/on_failure) for visualization.
    Returns a flat list of (operation, depth, parent_context) tuples.
    """
    from ...ast.proc.processing import BranchDecl, ParallelDecl, TransformDecl

    result = []
    for op in operations:
        # Add the operation itself
        result.append((op, depth, None))

        # Recursively flatten nested content
        if isinstance(op, BranchDecl) and hasattr(op, 'body') and op.body:
            nested = _flatten_operations(op.body, depth + 1)
            for nested_op, nested_depth, ctx in nested:
                result.append((nested_op, nested_depth, f"branch:{op.branch_name}"))

        elif isinstance(op, ParallelDecl) and hasattr(op, 'branches') and op.branches:
            for branch in op.branches:
                if hasattr(branch, 'body') and branch.body:
                    nested = _flatten_operations(branch.body, depth + 1)
                    for nested_op, nested_depth, ctx in nested:
                        result.append((nested_op, nested_depth, f"parallel:{op.name}/{branch.branch_name}"))

        elif isinstance(op, TransformDecl):
            # Handle on_success/on_failure blocks
            if hasattr(op, 'on_success') and op.on_success:
                nested = _flatten_operations(op.on_success, depth + 1)
                for nested_op, nested_depth, ctx in nested:
                    result.append((nested_op, nested_depth, f"on_success:{op.transform_name}"))

            if hasattr(op, 'on_failure') and op.on_failure:
                nested = _flatten_operations(op.on_failure, depth + 1)
                for nested_op, nested_depth, ctx in nested:
                    result.append((nested_op, nested_depth, f"on_failure:{op.transform_name}"))

    return result


def _process_to_graph(proc) -> dict:
    """Convert a ProcessDefinition to graph format."""
    from ...ast.proc.processing import (
        TransformDecl, RouteDecl, WindowDecl, JoinDecl,
        EnrichDecl, AggregateDecl, MergeDecl,
        # Additional processing types
        EvaluateDecl, TransitionDecl, EmitAuditDecl, DeduplicateDecl,
        LookupDecl, BranchDecl, ParallelDecl, ValidateInputDecl,
        CallDecl, ScheduleDecl, SetDecl
    )

    nodes = []
    edges = []
    edge_id = 0

    # Track node order for edge creation
    previous_node_ids = []

    # 1. Process receives (stream nodes)
    for recv in proc.receives:
        node_id = f"stream:{recv.source}"
        nodes.append({
            "id": node_id,
            "type": "stream",
            "data": {
                "label": recv.source,
                "source": recv.source,
                "alias": recv.alias,
                "schema": recv.schema.schema_name if recv.schema else None
            }
        })
        previous_node_ids.append(node_id)

    # 2. Process processing operations (flattened for visualization)
    flattened_ops = _flatten_operations(proc.processing)
    for op, depth, parent_ctx in flattened_ops:
        node_id = None
        node_type = None
        node_data = {}

        if isinstance(op, TransformDecl):
            node_id = f"xform-ref:{op.transform_name}"
            node_type = "xform-ref"
            node_data = {
                "label": op.transform_name,
                "transformName": op.transform_name
            }

        elif isinstance(op, RouteDecl):
            if op.rule_name:
                node_id = f"rules-ref:{op.rule_name}"
                node_type = "rules-ref"
                node_data = {
                    "label": op.rule_name,
                    "ruleName": op.rule_name
                }
            else:
                # Inline route condition
                node_id = f"route:inline_{edge_id}"
                node_type = "route"
                node_data = {
                    "label": "Route",
                    "condition": op.condition
                }

        elif isinstance(op, WindowDecl):
            # Handle both enum and string unit types
            size_unit = op.size.unit.value if hasattr(op.size.unit, 'value') else str(op.size.unit)
            window_type_val = op.window_type.value if hasattr(op.window_type, 'value') else str(op.window_type)
            window_label = f"{window_type_val}({op.size.value}{size_unit})"
            node_id = f"window:{window_label}"
            node_type = "window"

            slide_str = None
            if op.slide:
                slide_unit = op.slide.unit.value if hasattr(op.slide.unit, 'value') else str(op.slide.unit)
                slide_str = f"{op.slide.value}{slide_unit}"

            node_data = {
                "label": window_label,
                "windowType": window_type_val,
                "size": f"{op.size.value}{size_unit}",
                "slide": slide_str,
                "keyBy": op.key_by
            }

        elif isinstance(op, JoinDecl):
            node_id = f"join:{op.left}_{op.right}"
            node_type = "join"
            # Handle both enum and string types
            within_unit = op.within.unit.value if hasattr(op.within.unit, 'value') else str(op.within.unit)
            join_type_val = op.join_type.value if hasattr(op.join_type, 'value') else str(op.join_type)
            node_data = {
                "label": f"Join {op.left} ⋈ {op.right}",
                "left": op.left,
                "right": op.right,
                "onFields": op.on_fields,
                "within": f"{op.within.value}{within_unit}",
                "joinType": join_type_val
            }

        elif isinstance(op, EnrichDecl):
            node_id = f"enrich:{op.lookup_name}"
            node_type = "enrich"
            node_data = {
                "label": f"Enrich from {op.lookup_name}",
                "lookupName": op.lookup_name,
                "onFields": op.on_fields,
                "selectFields": op.select_fields
            }

        elif isinstance(op, AggregateDecl):
            node_id = f"aggregate:{op.transform_name}"
            node_type = "aggregate"
            node_data = {
                "label": f"Aggregate: {op.transform_name}",
                "transformName": op.transform_name
            }

        elif isinstance(op, MergeDecl):
            node_id = f"merge:{op.output_alias or '_'.join(op.streams)}"
            node_type = "merge"
            node_data = {
                "label": f"Merge: {', '.join(op.streams)}",
                "streams": op.streams,
                "outputAlias": op.output_alias
            }

        # Additional processing types
        elif isinstance(op, EvaluateDecl):
            # Rules evaluation step
            node_id = f"rules-ref:eval_{edge_id}"
            node_type = "rules-ref"
            node_data = {
                "label": op.expression[:30] + "..." if len(op.expression) > 30 else op.expression,
                "expression": op.expression,
                "opType": "evaluate"
            }

        elif isinstance(op, TransitionDecl):
            # State transition - show as process step
            node_id = f"process:transition_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"→ {op.target_state}",
                "targetState": op.target_state,
                "opType": "transition"
            }

        elif isinstance(op, EmitAuditDecl):
            # Audit event emission - show as process step
            node_id = f"process:audit_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"📋 {op.event_name}",
                "eventName": op.event_name,
                "opType": "emit_audit"
            }

        elif isinstance(op, DeduplicateDecl):
            # Deduplication step
            node_id = f"process:dedup_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"Dedup: {op.key_field}",
                "keyField": op.key_field,
                "opType": "deduplicate"
            }

        elif isinstance(op, LookupDecl):
            # Lookup operation
            node_id = f"enrich:lookup_{op.source_name}"
            node_type = "enrich"
            node_data = {
                "label": f"Lookup: {op.source_name}",
                "sourceName": op.source_name,
                "opType": "lookup"
            }

        elif isinstance(op, BranchDecl):
            # Branch - represents a flow branch
            node_id = f"route:branch_{op.branch_name}"
            node_type = "route"
            node_data = {
                "label": op.branch_name,
                "branchName": op.branch_name,
                "opType": "branch",
                "outputs": [op.branch_name]
            }

        elif isinstance(op, ParallelDecl):
            # Parallel block - fan-out node
            branch_names = [b.branch_name for b in op.branches] if op.branches else []
            node_id = f"route:parallel_{op.name}"
            node_type = "route"
            node_data = {
                "label": f"⫴ {op.name}",
                "parallelName": op.name,
                "opType": "parallel",
                "outputs": branch_names if branch_names else [op.name]
            }

        elif isinstance(op, ValidateInputDecl):
            # Input validation
            node_id = f"process:validate_{edge_id}"
            node_type = "process"
            node_data = {
                "label": "Validate Input",
                "expression": op.expression,
                "opType": "validate"
            }

        elif isinstance(op, CallDecl):
            # External call
            node_id = f"process:call_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"Call: {op.target}",
                "target": op.target,
                "opType": "call"
            }

        elif isinstance(op, ScheduleDecl):
            # Scheduled action
            node_id = f"process:schedule_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"⏰ {op.target}",
                "target": op.target,
                "opType": "schedule"
            }

        elif isinstance(op, SetDecl):
            # Variable assignment
            node_id = f"process:set_{edge_id}"
            node_type = "process"
            node_data = {
                "label": f"{op.variable} = ...",
                "variable": op.variable,
                "value": op.value,
                "opType": "set"
            }

        else:
            # Generic processing node for any unknown types
            op_name = type(op).__name__.replace('Decl', '').lower()
            node_id = f"process:{op_name}_{edge_id}"
            node_type = "process"
            node_data = {
                "label": op_name.capitalize(),
                "opType": op_name
            }

        if node_id:
            # Add nesting metadata for visualization
            if depth > 0:
                node_data["nestingDepth"] = depth
            if parent_ctx:
                node_data["parentContext"] = parent_ctx

            nodes.append({
                "id": node_id,
                "type": node_type,
                "data": node_data
            })

            # Create edges from previous nodes
            for prev_id in previous_node_ids:
                edges.append({
                    "id": f"edge_{edge_id}",
                    "source": prev_id,
                    "target": node_id,
                    "type": "default"
                })
                edge_id += 1

            previous_node_ids = [node_id]

    # 3. Process emits (output stream nodes)
    for emit in proc.emits:
        node_id = f"stream:{emit.target}"
        nodes.append({
            "id": node_id,
            "type": "stream",
            "data": {
                "label": emit.target,
                "target": emit.target,
                "schema": emit.schema.schema_name if emit.schema else None,
                "isOutput": True
            }
        })

        # Connect from previous processing nodes
        for prev_id in previous_node_ids:
            edges.append({
                "id": f"edge_{edge_id}",
                "source": prev_id,
                "target": node_id,
                "type": "default"
            })
            edge_id += 1

    # 4. Process markers if present
    if proc.markers:
        for marker in proc.markers.markers:
            node_id = f"marker:{marker.name}"
            nodes.append({
                "id": node_id,
                "type": "marker",
                "data": {
                    "label": marker.name,
                    "markerName": marker.name,
                    "condition": _serialize_marker_condition(marker.condition) if marker.condition else None
                }
            })

    # Generate graph checksum based on node/edge IDs and types (stable across layout changes)
    graph_checksum = _compute_graph_checksum(nodes, edges)

    return {
        "processName": proc.name,
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "hasMarkers": proc.has_markers() if hasattr(proc, 'has_markers') else False,
            "hasPhases": proc.has_phases() if hasattr(proc, 'has_phases') else False,
            "hasBusinessDate": proc.has_business_date() if hasattr(proc, 'has_business_date') else False,
            "graphChecksum": graph_checksum
        }
    }


def _compute_graph_checksum(nodes: list, edges: list) -> str:
    """
    Compute a stable checksum of the graph structure.

    Uses node IDs, types, and edge connections to create a hash that is:
    - Stable across layout/position changes (positions are NOT included)
    - Sensitive to structural changes (new nodes, removed nodes, changed connections)

    This allows detecting when .proc file changes affect the graph structure
    without being affected by UI-only layout changes.
    """
    # Extract structural information only (no positions, no measured dimensions)
    node_signatures = sorted([
        f"{n['id']}:{n['type']}:{n['data'].get('label', '')}"
        for n in nodes
    ])

    edge_signatures = sorted([
        f"{e['source']}->{e['target']}"
        for e in edges
    ])

    # Combine into a single string and hash
    combined = "|".join(node_signatures) + "||" + "|".join(edge_signatures)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]


def _serialize_marker_condition(condition) -> dict:
    """Serialize marker condition to JSON-friendly format."""
    if condition is None:
        return None

    result = {"type": type(condition).__name__}

    # Handle different condition types
    if hasattr(condition, 'time'):
        result["time"] = condition.time
    if hasattr(condition, 'stream'):
        result["stream"] = condition.stream
    if hasattr(condition, 'threshold'):
        result["threshold"] = condition.threshold
    if hasattr(condition, 'left'):
        result["left"] = _serialize_marker_condition(condition.left)
    if hasattr(condition, 'right'):
        result["right"] = _serialize_marker_condition(condition.right)
    if hasattr(condition, 'operator'):
        result["operator"] = condition.operator.value if hasattr(condition.operator, 'value') else str(condition.operator)

    return result
