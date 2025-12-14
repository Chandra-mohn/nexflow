# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Helper Methods Visitor Mixin for Flow Parser

Common helper methods for field paths, durations, and utility functions
used across all flow visitor mixins.

Updated for grammar v0.5.0+ which uses keywordOrIdentifier for field paths
to allow keywords as valid field names.
"""

from typing import List, Optional

from backend.ast import proc_ast as ast
from backend.parser.base import SourceLocation
from backend.parser.generated.proc import ProcDSLParser


class FlowHelpersVisitorMixin:
    """Mixin for common helper methods used by all flow visitor mixins."""

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

    def visitFieldPath(self, ctx: ProcDSLParser.FieldPathContext) -> ast.FieldPath:
        """
        Visit a field path.

        Grammar v0.5.0+: fieldPath: keywordOrIdentifier (DOT keywordOrIdentifier)* (LBRACKET INTEGER RBRACKET)?
        keywordOrIdentifier allows keywords like 'priority', 'state', 'type' to be field names.
        """
        parts = []
        for koi_ctx in ctx.keywordOrIdentifier():
            # keywordOrIdentifier can be IDENTIFIER or various keywords
            parts.append(self._get_text(koi_ctx))

        # Handle optional array index [N]
        index = None
        if ctx.INTEGER():
            index = int(ctx.INTEGER().getText())

        return ast.FieldPath(parts=parts, index=index)

    def visitDuration(self, ctx: ProcDSLParser.DurationContext) -> ast.Duration:
        if ctx.DURATION_LITERAL():
            text = ctx.DURATION_LITERAL().getText()
            unit_char = text[-1]
            value = int(text[:-1])
            unit_map = {'s': 's', 'm': 'm', 'h': 'h', 'd': 'd'}
            return ast.Duration(value=value, unit=unit_map.get(unit_char, 's'))
        else:
            value = int(ctx.INTEGER().getText())
            unit = self._get_time_unit(ctx.timeUnit())
            return ast.Duration(value=value, unit=unit)

    def _get_time_unit(self, ctx: ProcDSLParser.TimeUnitContext) -> str:
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

    def _get_field_list(self, ctx: ProcDSLParser.FieldListContext) -> List[str]:
        """Extract field names from fieldList context."""
        if ctx is None:
            return []
        fields = []
        for field_path_ctx in ctx.fieldPath():
            # Use keywordOrIdentifier for each part of the field path
            parts = [self._get_text(koi) for koi in field_path_ctx.keywordOrIdentifier()]
            fields.append('.'.join(parts))
        return fields
