"""
Helper Methods Visitor Mixin

Common helper methods for expressions, literals, duration, field path,
size specifications, and utility functions used across all visitor mixins.
"""

from typing import List, Union

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class HelpersVisitorMixin:
    """Mixin for common helper methods used by all visitor mixins."""

    # =========================================================================
    # Expressions and Literals
    # =========================================================================

    def visitExpression(self, ctx: SchemaDSLParser.ExpressionContext) -> ast.Expression:
        raw_text = self._get_text(ctx)
        return ast.Expression(
            raw_text=raw_text,
            location=self._get_location(ctx)
        )

    def visitFunctionCall(self, ctx: SchemaDSLParser.FunctionCallContext) -> ast.Expression:
        raw_text = self._get_text(ctx)
        return ast.Expression(
            raw_text=raw_text,
            location=self._get_location(ctx)
        )

    def visitLiteral(self, ctx: SchemaDSLParser.LiteralContext) -> ast.Literal:
        if ctx.STRING():
            return ast.StringLiteral(value=self._strip_quotes(ctx.STRING().getText()))
        elif ctx.numberLiteral():
            num = self._parse_number(ctx.numberLiteral())
            if isinstance(num, float):
                return ast.DecimalLiteral(value=num)
            return ast.IntegerLiteral(value=num)
        elif ctx.getText().lower() == 'true':
            return ast.BooleanLiteral(value=True)
        elif ctx.getText().lower() == 'false':
            return ast.BooleanLiteral(value=False)
        elif ctx.getText().lower() == 'null':
            return ast.NullLiteral()

        return ast.StringLiteral(value=ctx.getText())

    def _parse_number(self, ctx) -> Union[int, float]:
        text = self._get_text(ctx)
        if '.' in text:
            return float(text)
        return int(text)

    # =========================================================================
    # Field Path and Field Lists
    # =========================================================================

    def visitFieldPath(self, ctx: SchemaDSLParser.FieldPathContext) -> ast.FieldPath:
        parts = [ident.getText() for ident in ctx.IDENTIFIER()]
        return ast.FieldPath(parts=parts)

    def _get_field_list(self, ctx) -> List[str]:
        """Extract field names from fieldList or fieldArray context."""
        if ctx is None:
            return []
        fields = []
        if hasattr(ctx, 'fieldPath'):
            for field_path_ctx in ctx.fieldPath():
                parts = [ident.getText() for ident in field_path_ctx.IDENTIFIER()]
                fields.append('.'.join(parts))
        elif hasattr(ctx, 'IDENTIFIER'):
            for ident in ctx.IDENTIFIER():
                fields.append(ident.getText())
        return fields

    # =========================================================================
    # Duration and Size Specifications
    # =========================================================================

    def visitDuration(self, ctx: SchemaDSLParser.DurationContext) -> ast.Duration:
        value = int(ctx.INTEGER().getText()) if ctx.INTEGER() else 0
        unit = self._get_time_unit(ctx.timeUnit()) if ctx.timeUnit() else 's'
        return ast.Duration(value=value, unit=unit)

    def _get_time_unit(self, ctx: SchemaDSLParser.TimeUnitContext) -> str:
        unit_text = self._get_text(ctx).lower()
        if 'second' in unit_text:
            return 's'
        elif 'minute' in unit_text:
            return 'm'
        elif 'hour' in unit_text:
            return 'h'
        elif 'day' in unit_text:
            return 'd'
        return 's'

    def visitSizeSpec(self, ctx: SchemaDSLParser.SizeSpecContext) -> ast.SizeSpec:
        value = int(ctx.INTEGER().getText()) if ctx.INTEGER() else 0
        unit = self._get_size_unit(ctx.sizeUnit()) if ctx.sizeUnit() else 'MB'
        return ast.SizeSpec(value=value, unit=unit)

    def _get_size_unit(self, ctx: SchemaDSLParser.SizeUnitContext) -> str:
        unit_text = self._get_text(ctx).upper()
        if 'KB' in unit_text:
            return 'KB'
        elif 'MB' in unit_text:
            return 'MB'
        elif 'GB' in unit_text:
            return 'GB'
        elif 'TB' in unit_text:
            return 'TB'
        return 'MB'
