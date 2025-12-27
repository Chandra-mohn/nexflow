# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Tests for Parse Command

Integration tests for the CLI parse command functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.cli.commands.parse import (
    parse_file,
    get_language_from_file,
    ast_to_json,
    ast_to_tree,
    ast_to_summary,
)
from backend.cli.commands.types import ParseResult


class TestGetLanguageFromFile:
    """Tests for file extension to language mapping."""

    def test_proc_extension(self):
        """Test .proc file extension detection."""
        assert get_language_from_file(Path("test.proc")) == "proc"

    def test_schema_extension(self):
        """Test .schema file extension detection."""
        assert get_language_from_file(Path("test.schema")) == "schema"

    def test_rules_extension(self):
        """Test .rules file extension detection."""
        assert get_language_from_file(Path("test.rules")) == "rules"

    def test_transform_extension(self):
        """Test .xform file extension detection."""
        assert get_language_from_file(Path("test.xform")) == "transform"

    def test_unknown_extension(self):
        """Test unknown file extension returns None."""
        assert get_language_from_file(Path("test.unknown")) is None
        assert get_language_from_file(Path("test.py")) is None
        assert get_language_from_file(Path("test.java")) is None


class TestParseFile:
    """Tests for parse_file function."""

    def test_unknown_file_type(self, tmp_path):
        """Test error handling for unknown file types."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("content")

        result = parse_file(test_file, "summary", verbose=False)

        assert result.success is False
        assert len(result.errors) == 1
        assert "Unknown file type" in result.errors[0].message

    def test_graph_format_only_for_proc(self, tmp_path):
        """Test that graph format is only supported for .proc files."""
        test_file = tmp_path / "test.schema"
        test_file.write_text("schema Test { field: string }")

        result = parse_file(test_file, "graph", verbose=False)

        assert result.success is False
        assert "Graph format only supported for .proc files" in result.errors[0].message


class TestAstToJson:
    """Tests for AST to JSON conversion."""

    def test_simple_dataclass(self):
        """Test JSON serialization of simple dataclass."""
        from dataclasses import dataclass

        @dataclass
        class SimpleNode:
            name: str
            value: int

        node = SimpleNode(name="test", value=42)
        result = json.loads(ast_to_json(node))

        assert result["_type"] == "SimpleNode"
        assert result["name"] == "test"
        assert result["value"] == 42

    def test_nested_dataclass(self):
        """Test JSON serialization of nested dataclass."""
        from dataclasses import dataclass

        @dataclass
        class Inner:
            data: str

        @dataclass
        class Outer:
            inner: Inner
            count: int

        node = Outer(inner=Inner(data="nested"), count=10)
        result = json.loads(ast_to_json(node))

        assert result["_type"] == "Outer"
        assert result["inner"]["_type"] == "Inner"
        assert result["inner"]["data"] == "nested"

    def test_list_serialization(self):
        """Test JSON serialization of lists."""
        from dataclasses import dataclass

        @dataclass
        class Container:
            items: list

        node = Container(items=["a", "b", "c"])
        result = json.loads(ast_to_json(node))

        assert result["items"] == ["a", "b", "c"]

    def test_enum_serialization(self):
        """Test JSON serialization of enums."""
        from enum import Enum
        from dataclasses import dataclass

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        @dataclass
        class Record:
            status: Status

        node = Record(status=Status.ACTIVE)
        result = json.loads(ast_to_json(node))

        assert result["status"] == "active"


class TestAstToTree:
    """Tests for AST to tree string conversion."""

    def test_simple_tree(self):
        """Test tree generation for simple dataclass."""
        from dataclasses import dataclass

        @dataclass
        class Node:
            name: str

        node = Node(name="test")
        result = ast_to_tree(node)

        assert "Node" in result
        # The implementation uses the field name accessor which outputs field name
        assert "name:" in result

    def test_indentation(self):
        """Test proper indentation in tree output."""
        from dataclasses import dataclass

        @dataclass
        class Child:
            value: str

        @dataclass
        class Parent:
            child: Child

        node = Parent(child=Child(value="nested"))
        result = ast_to_tree(node)

        # Parent should be at root level
        assert result.startswith("Parent")


class TestAstToSummary:
    """Tests for AST to summary conversion."""

    def test_summary_with_processes(self):
        """Test summary generation for program with processes."""
        from backend.ast.proc.program import Program, ProcessDefinition

        program = Program(processes=[
            ProcessDefinition(name="proc1", receives=[], processing=[], emits=[]),
            ProcessDefinition(name="proc2", receives=[], processing=[], emits=[]),
        ])

        result = ast_to_summary(program, Path("test.proc"))

        assert "File: test.proc" in result
        assert "Processes: 2" in result
        assert "proc1" in result
        assert "proc2" in result

    def test_summary_with_schemas(self):
        """Test summary generation for program with schemas."""
        from dataclasses import dataclass

        @dataclass
        class Schema:
            name: str

        @dataclass
        class SchemaProgram:
            schemas: list

        program = SchemaProgram(schemas=[
            Schema(name="Order"),
            Schema(name="Customer"),
        ])

        result = ast_to_summary(program, Path("test.schema"))

        assert "Schemas: 2" in result
        assert "Order" in result
        assert "Customer" in result


class TestParseResultType:
    """Tests for ParseResult type."""

    def test_default_values(self):
        """Test ParseResult default values."""
        result = ParseResult(success=True)

        assert result.success is True
        assert result.output == ""  # Default is empty string
        assert result.errors == []

    def test_with_errors(self):
        """Test ParseResult with errors."""
        from backend.cli.commands.types import ValidationError

        result = ParseResult(success=False)
        result.errors.append(ValidationError(
            file="test.proc",
            line=10,
            column=5,
            message="Syntax error"
        ))

        assert result.success is False
        assert len(result.errors) == 1
        assert result.errors[0].line == 10
