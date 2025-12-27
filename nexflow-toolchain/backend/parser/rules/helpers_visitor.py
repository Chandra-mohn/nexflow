# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Helper Methods Visitor Mixin for Rules Parser

Common helper methods for parsing rules DSL.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from backend.ast import rules_ast as ast
from backend.parser.base import SourceLocation
from backend.parser.generated.rules import RulesDSLParser


class RulesHelpersVisitorMixin:
    """Mixin for common helper methods used by all rules visitor mixins."""

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

    def _parse_money(self, text: str) -> ast.MoneyLiteral:
        """Parse money literal like $100.00."""
        value_str = text.lstrip('$€£')
        try:
            return ast.MoneyLiteral(value=Decimal(value_str))
        except (ValueError, InvalidOperation):
            return ast.MoneyLiteral(value=Decimal(0))
