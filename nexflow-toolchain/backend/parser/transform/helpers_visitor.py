"""
Helper Methods Visitor Mixin for Transform Parser

Common helper methods for field paths, durations, and utility functions
used across all transform visitor mixins.
"""

from typing import List, Optional, Union

from backend.ast import transform_ast as ast
from backend.parser.base import SourceLocation
from backend.parser.generated.transform import TransformDSLParser


class TransformHelpersVisitorMixin:
    """Mixin for common helper methods used by all transform visitor mixins."""

    def _get_location(self, ctx) -> Optional[SourceLocation]:
        """Extract source location from parser context."""
        if ctx is None:
            return None
        start = ctx.start if hasattr(ctx, 'start') else None
        stop = ctx.stop if hasattr(ctx, 'stop') else None
        if start:
            return SourceLocation(
                line=start.line,
                column=start.column,
                start_index=start.start if hasattr(start, 'start') else 0,
                stop_index=stop.stop if stop and hasattr(stop, 'stop') else 0
            )
        return None

    def _get_text(self, ctx) -> str:
        """Get text content from context."""
        return ctx.getText() if ctx else ""

    def _strip_quotes(self, text: str) -> str:
        """Strip quotes from string literal."""
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text

    def visitFieldPath(self, ctx: TransformDSLParser.FieldPathContext) -> ast.FieldPath:
        parts = [ident.getText() for ident in ctx.IDENTIFIER()]
        return ast.FieldPath(parts=parts)

    def visitDuration(self, ctx: TransformDSLParser.DurationContext) -> ast.Duration:
        value = int(ctx.INTEGER().getText()) if ctx.INTEGER() else 0
        unit = self._get_time_unit(ctx.timeUnit()) if ctx.timeUnit() else 's'
        return ast.Duration(value=value, unit=unit)

    def _get_time_unit(self, ctx: TransformDSLParser.TimeUnitContext) -> str:
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

    def _get_field_array(self, ctx) -> List[str]:
        """Extract field names from fieldArray context."""
        if ctx is None:
            return []
        fields = []
        for field_path_ctx in ctx.fieldPath():
            parts = [ident.getText() for ident in field_path_ctx.IDENTIFIER()]
            fields.append('.'.join(parts))
        return fields

    def _get_value_list(self, ctx: TransformDSLParser.ValueListContext) -> List[str]:
        """Extract string values from valueList context."""
        if ctx is None:
            return []
        values = []
        for lit_ctx in ctx.literal():
            values.append(self._strip_quotes(self._get_text(lit_ctx)))
        return values

    def _parse_number(self, ctx) -> Union[int, float]:
        text = self._get_text(ctx)
        if '.' in text:
            return float(text)
        return int(text)
