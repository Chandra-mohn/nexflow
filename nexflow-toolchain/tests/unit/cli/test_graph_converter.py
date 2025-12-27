# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Tests for Graph Converter Module

Tests the conversion of Process AST to UI-consumable graph format.
"""

import json
import pytest

from backend.cli.commands.graph_converter import (
    ast_to_graph,
    _flatten_operations,
    _process_to_graph,
    _compute_graph_checksum,
)
from backend.ast.proc.program import Program, ProcessDefinition
from backend.ast.proc.input import ReceiveDecl, SchemaDecl
from backend.ast.proc.output import EmitDecl
from backend.ast.proc.processing import (
    TransformDecl, RouteDecl, WindowDecl, JoinDecl,
    EnrichDecl, AggregateDecl, ValidateInputDecl,
    CallDecl, SetDecl,
)
from backend.ast.proc.enums import WindowType, JoinType
from backend.ast.proc.common import Duration


class TestAstToGraph:
    """Tests for the main ast_to_graph function."""

    def test_empty_program(self):
        """Test handling of program with no processes."""
        program = Program(processes=[])
        result = json.loads(ast_to_graph(program))
        assert "error" in result
        assert "No processes found" in result["error"]

    def test_unexpected_ast_type(self):
        """Test handling of unexpected AST types."""
        result = json.loads(ast_to_graph({"invalid": "object"}))
        assert "error" in result
        assert "Unexpected AST type" in result["error"]

    def test_simple_process(self):
        """Test conversion of a simple process with input and output."""
        proc = ProcessDefinition(
            name="test_process",
            receives=[
                ReceiveDecl(
                    source="orders_input",
                    alias="orders",
                    schema=SchemaDecl(schema_name="Order")
                )
            ],
            processing=[],
            emits=[
                EmitDecl(
                    target="orders_output",
                    schema=SchemaDecl(schema_name="Order")
                )
            ]
        )
        program = Program(processes=[proc])

        result = json.loads(ast_to_graph(program))

        assert result["processName"] == "test_process"
        assert len(result["nodes"]) == 2  # input + output streams
        assert len(result["edges"]) == 1  # input -> output

        # Check input node
        input_node = next(n for n in result["nodes"] if n["id"] == "stream:orders_input")
        assert input_node["type"] == "stream"
        assert input_node["data"]["source"] == "orders_input"
        assert input_node["data"]["alias"] == "orders"

        # Check output node
        output_node = next(n for n in result["nodes"] if n["id"] == "stream:orders_output")
        assert output_node["data"]["isOutput"] is True

    def test_process_with_transform(self):
        """Test process with a transform operation."""
        proc = ProcessDefinition(
            name="transform_process",
            receives=[
                ReceiveDecl(source="input", alias="i", schema=None)
            ],
            processing=[
                TransformDecl(transform_name="enrich_order")
            ],
            emits=[
                EmitDecl(target="output", schema=None)
            ]
        )

        result = json.loads(ast_to_graph(proc))

        assert result["processName"] == "transform_process"
        assert len(result["nodes"]) == 3  # input + transform + output

        # Check transform node
        xform_node = next(n for n in result["nodes"] if n["type"] == "xform-ref")
        assert xform_node["data"]["transformName"] == "enrich_order"

    def test_process_with_route(self):
        """Test process with a route operation."""
        proc = ProcessDefinition(
            name="route_process",
            receives=[
                ReceiveDecl(source="input", alias="i", schema=None)
            ],
            processing=[
                RouteDecl(rule_name="order_routing")
            ],
            emits=[
                EmitDecl(target="output", schema=None)
            ]
        )

        result = json.loads(ast_to_graph(proc))

        # Check rules-ref node
        route_node = next(n for n in result["nodes"] if n["type"] == "rules-ref")
        assert route_node["data"]["ruleName"] == "order_routing"


class TestProcessToGraph:
    """Tests for the _process_to_graph function."""

    def test_window_node(self):
        """Test window declaration creates correct node."""
        proc = ProcessDefinition(
            name="window_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                WindowDecl(
                    window_type=WindowType.TUMBLING,
                    size=Duration(value=5, unit="m"),
                    slide=None,
                    key_by="customer_id"
                )
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        window_node = next(n for n in result["nodes"] if n["type"] == "window")
        assert "tumbling" in window_node["data"]["windowType"].lower()
        assert window_node["data"]["keyBy"] == "customer_id"

    def test_join_node(self):
        """Test join declaration creates correct node."""
        proc = ProcessDefinition(
            name="join_process",
            receives=[
                ReceiveDecl(source="orders", alias="o", schema=None),
                ReceiveDecl(source="payments", alias="p", schema=None)
            ],
            processing=[
                JoinDecl(
                    left="orders",
                    right="payments",
                    on_fields=["order_id"],
                    within=Duration(value=10, unit="s"),
                    join_type=JoinType.INNER
                )
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        join_node = next(n for n in result["nodes"] if n["type"] == "join")
        assert join_node["data"]["left"] == "orders"
        assert join_node["data"]["right"] == "payments"
        assert "order_id" in join_node["data"]["onFields"]

    def test_enrich_node(self):
        """Test enrich declaration creates correct node."""
        proc = ProcessDefinition(
            name="enrich_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                EnrichDecl(
                    lookup_name="customer_lookup",
                    on_fields=["customer_id"],
                    select_fields=["name", "email"]
                )
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        enrich_node = next(n for n in result["nodes"] if n["type"] == "enrich")
        assert enrich_node["data"]["lookupName"] == "customer_lookup"

    def test_validate_input_node(self):
        """Test validate input creates correct node."""
        proc = ProcessDefinition(
            name="validate_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                ValidateInputDecl(expression="amount > 0")
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        validate_node = next(n for n in result["nodes"] if "validate" in n["id"])
        assert validate_node["data"]["opType"] == "validate"

    def test_call_node(self):
        """Test call declaration creates correct node."""
        proc = ProcessDefinition(
            name="call_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                CallDecl(target="external_service")
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        call_node = next(n for n in result["nodes"] if "call" in n["id"])
        assert call_node["data"]["target"] == "external_service"
        assert call_node["data"]["opType"] == "call"

    def test_set_node(self):
        """Test set declaration creates correct node."""
        proc = ProcessDefinition(
            name="set_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                SetDecl(variable="status", value="processed")
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        set_node = next(n for n in result["nodes"] if "set" in n["id"])
        assert set_node["data"]["variable"] == "status"
        assert set_node["data"]["opType"] == "set"


class TestGraphChecksum:
    """Tests for the _compute_graph_checksum function."""

    def test_checksum_stability(self):
        """Test that checksum is stable for same structure."""
        nodes = [
            {"id": "stream:input", "type": "stream", "data": {"label": "input"}},
            {"id": "xform:process", "type": "xform-ref", "data": {"label": "process"}},
            {"id": "stream:output", "type": "stream", "data": {"label": "output"}}
        ]
        edges = [
            {"source": "stream:input", "target": "xform:process"},
            {"source": "xform:process", "target": "stream:output"}
        ]

        checksum1 = _compute_graph_checksum(nodes, edges)
        checksum2 = _compute_graph_checksum(nodes, edges)

        assert checksum1 == checksum2

    def test_checksum_changes_on_structure_change(self):
        """Test that checksum changes when structure changes."""
        nodes1 = [
            {"id": "stream:input", "type": "stream", "data": {"label": "input"}}
        ]
        nodes2 = [
            {"id": "stream:input", "type": "stream", "data": {"label": "input"}},
            {"id": "stream:output", "type": "stream", "data": {"label": "output"}}
        ]
        edges = []

        checksum1 = _compute_graph_checksum(nodes1, edges)
        checksum2 = _compute_graph_checksum(nodes2, edges)

        assert checksum1 != checksum2

    def test_checksum_length(self):
        """Test that checksum has expected length."""
        nodes = [{"id": "test", "type": "stream", "data": {"label": "test"}}]
        edges = []

        checksum = _compute_graph_checksum(nodes, edges)

        assert len(checksum) == 16  # SHA256 truncated to 16 chars


class TestFlattenOperations:
    """Tests for the _flatten_operations function."""

    def test_empty_operations(self):
        """Test handling of empty operations list."""
        result = _flatten_operations([])
        assert result == []

    def test_single_operation(self):
        """Test flattening single operation."""
        ops = [TransformDecl(transform_name="test")]
        result = _flatten_operations(ops)

        assert len(result) == 1
        assert result[0][0].transform_name == "test"
        assert result[0][1] == 0  # depth
        assert result[0][2] is None  # parent context


class TestEdgeCreation:
    """Tests for edge creation between nodes."""

    def test_edges_connect_sequentially(self):
        """Test that edges connect nodes in sequence."""
        proc = ProcessDefinition(
            name="sequential_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[
                TransformDecl(transform_name="step1"),
                TransformDecl(transform_name="step2"),
                TransformDecl(transform_name="step3"),
            ],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        # Should have: input -> step1 -> step2 -> step3 -> output
        assert len(result["nodes"]) == 5
        assert len(result["edges"]) == 4

    def test_metadata_fields(self):
        """Test that metadata fields are populated."""
        proc = ProcessDefinition(
            name="meta_process",
            receives=[ReceiveDecl(source="input", alias="i", schema=None)],
            processing=[],
            emits=[EmitDecl(target="output", schema=None)]
        )

        result = _process_to_graph(proc)

        assert "metadata" in result
        assert "graphChecksum" in result["metadata"]
        assert len(result["metadata"]["graphChecksum"]) == 16
