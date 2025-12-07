"""
Transform DSL (L3) Parser

Parser wrapper for L3 Transform Catalog DSL with AST building.
Composed from modular visitor mixins for maintainability.
"""

from .base import BaseParser, ParseResult
from .generated.transform import TransformDSLLexer, TransformDSLParser, TransformDSLVisitor
from .transform import (
    TransformHelpersVisitorMixin,
    TransformCoreVisitorMixin,
    TransformMetadataVisitorMixin,
    TransformTypesVisitorMixin,
    TransformSpecsVisitorMixin,
    TransformApplyVisitorMixin,
    TransformValidationVisitorMixin,
    TransformErrorVisitorMixin,
    TransformExpressionVisitorMixin,
)


class TransformASTBuilder(
    TransformHelpersVisitorMixin,
    TransformCoreVisitorMixin,
    TransformMetadataVisitorMixin,
    TransformTypesVisitorMixin,
    TransformSpecsVisitorMixin,
    TransformApplyVisitorMixin,
    TransformValidationVisitorMixin,
    TransformErrorVisitorMixin,
    TransformExpressionVisitorMixin,
    TransformDSLVisitor
):
    """Visitor that builds AST from ANTLR parse tree for L3 Transform DSL.

    Composed from modular mixins:
    - TransformHelpersVisitorMixin: Common helper methods
    - TransformCoreVisitorMixin: Program and transform definitions
    - TransformMetadataVisitorMixin: Version, cache, compatibility
    - TransformTypesVisitorMixin: Field types and constraints
    - TransformSpecsVisitorMixin: Input/output specifications
    - TransformApplyVisitorMixin: Apply block, mappings, compose
    - TransformValidationVisitorMixin: Validation rules
    - TransformErrorVisitorMixin: Error handling blocks
    - TransformExpressionVisitorMixin: Expression parsing
    """
    pass


class TransformParser(BaseParser):
    """Parser for L3 Transform DSL files."""

    def parse(self, content: str) -> ParseResult:
        """Parse Transform DSL content and return AST."""
        result = ParseResult(success=True)

        try:
            parser = self._setup_parser(TransformDSLLexer, TransformDSLParser, content)
            tree = parser.program()
            self._collect_errors(result)

            if result.success:
                builder = TransformASTBuilder()
                result.ast = builder.visitProgram(tree)
                result.parse_tree = tree

        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")

        return result
