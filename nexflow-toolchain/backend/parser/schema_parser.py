"""
Schema DSL (L2) Parser

Parser wrapper for L2 Schema Registry DSL with AST building.
Uses modular visitor mixins for maintainability.
"""

from .base import BaseParser, ParseResult
from .generated.schema import SchemaDSLLexer, SchemaDSLParser, SchemaDSLVisitor
from .schema import (
    HelpersVisitorMixin,
    CoreVisitorMixin,
    TypesVisitorMixin,
    StreamingVisitorMixin,
    StateMachineVisitorMixin,
    PatternVisitorMixin,
)


class SchemaASTBuilder(
    HelpersVisitorMixin,
    CoreVisitorMixin,
    TypesVisitorMixin,
    StreamingVisitorMixin,
    StateMachineVisitorMixin,
    PatternVisitorMixin,
    SchemaDSLVisitor
):
    """
    Visitor that builds AST from ANTLR parse tree for L2 Schema DSL.

    Composed from modular mixins:
    - HelpersVisitorMixin: Common helpers (expressions, literals, duration, paths)
    - CoreVisitorMixin: Program, schema definition, identity, fields, nested objects
    - TypesVisitorMixin: Field types, constraints, qualifiers, type aliases
    - StreamingVisitorMixin: Streaming configuration (watermarks, time semantics)
    - StateMachineVisitorMixin: State machine blocks (states, transitions, actions)
    - PatternVisitorMixin: Pattern-specific blocks (parameters, entries, rules, migration)
    """
    pass


class SchemaParser(BaseParser):
    """Parser for L2 Schema DSL files."""

    def parse(self, content: str) -> ParseResult:
        """Parse Schema DSL content and return AST."""
        result = ParseResult(success=True)

        try:
            parser = self._setup_parser(SchemaDSLLexer, SchemaDSLParser, content)
            tree = parser.program()
            self._collect_errors(result)

            if result.success:
                builder = SchemaASTBuilder()
                result.ast = builder.visitProgram(tree)
                result.parse_tree = tree

        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")

        return result
