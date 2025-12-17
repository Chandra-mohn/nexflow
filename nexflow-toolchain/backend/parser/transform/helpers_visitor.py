# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Helper Methods Visitor Mixin for Transform Parser

Common helper methods for field paths, durations, and utility functions
used across all transform visitor mixins.
"""

from typing import List, Optional, Union

from backend.ast import transform_ast as ast
from backend.parser.common import BaseVisitorMixin
from backend.parser.generated.transform import TransformDSLParser


class TransformHelpersVisitorMixin(BaseVisitorMixin):
    """Mixin for common helper methods used by all transform visitor mixins.

    Inherits _get_location, _get_text, _strip_quotes from BaseVisitorMixin.
    """

    def visitFieldPath(self, ctx: TransformDSLParser.FieldPathContext) -> ast.FieldPath:
        # fieldPath now uses fieldOrKeyword which can be IDENTIFIER or keyword
        parts = [self._get_text(fok) for fok in ctx.fieldOrKeyword()]
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
            # fieldPath = fieldOrKeyword ('.' fieldOrKeyword)*
            # Each fieldOrKeyword is either IDENTIFIER or a keyword
            parts = [fok.getText() for fok in field_path_ctx.fieldOrKeyword()]
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
