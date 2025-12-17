# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Base Visitor Mixin

Common helper methods shared across all parser visitor mixins.
Eliminates duplication of _get_location, _get_text, _strip_quotes methods.
"""

from typing import Optional

from backend.parser.base import SourceLocation


class BaseVisitorMixin:
    """
    Base mixin providing common helper methods for all parser visitors.

    Methods:
    - _get_location: Extract SourceLocation from parser context
    - _get_text: Get text content from context
    - _strip_quotes: Strip quotes from string literals
    """

    def _get_location(self, ctx) -> Optional[SourceLocation]:
        """Extract source location from parser context.

        Args:
            ctx: ANTLR parser context

        Returns:
            SourceLocation with line, column, and index information
        """
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
        """Get text content from context.

        Args:
            ctx: ANTLR parser context or terminal node

        Returns:
            Text content as string, empty string if ctx is None
        """
        return ctx.getText() if ctx else ""

    def _strip_quotes(self, text: str) -> str:
        """Strip quotes from string literal.

        Handles both single and double quotes.

        Args:
            text: String that may be quoted

        Returns:
            String with quotes removed
        """
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text
