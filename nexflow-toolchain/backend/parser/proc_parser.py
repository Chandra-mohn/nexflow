# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Proc DSL (L1) Parser

Parser wrapper for L1 Process Orchestration DSL with AST building.
Uses modular visitor mixins for maintainability.

Note: Due to grammar evolution (v0.5.0+), the full AST builder may fail to load
if visitor mixins reference non-existent parser contexts. In this case, the parser
falls back to syntax-only validation mode.
"""

from .base import BaseParser, ParseResult
from .generated.proc import ProcDSLLexer, ProcDSLParser, ProcDSLVisitor

# Try to load the full AST builder mixins
# If they fail (due to grammar/visitor mismatch), we'll use syntax-only mode
_AST_BUILDER_AVAILABLE = False
ProcASTBuilder = None

try:
    from .proc import (
        ProcHelpersVisitorMixin,
        ProcCoreVisitorMixin,
        ProcExecutionVisitorMixin,
        ProcInputVisitorMixin,
        ProcProcessingVisitorMixin,
        ProcCorrelationVisitorMixin,
        ProcOutputVisitorMixin,
        ProcStateVisitorMixin,
        ProcResilienceVisitorMixin,
        ProcMarkersVisitorMixin,
    )

    class ProcASTBuilder(
        ProcHelpersVisitorMixin,
        ProcCoreVisitorMixin,
        ProcExecutionVisitorMixin,
        ProcInputVisitorMixin,
        ProcProcessingVisitorMixin,
        ProcCorrelationVisitorMixin,
        ProcOutputVisitorMixin,
        ProcStateVisitorMixin,
        ProcResilienceVisitorMixin,
        ProcMarkersVisitorMixin,
        ProcDSLVisitor
    ):
        """
        Visitor that builds AST from ANTLR parse tree for L1 Proc DSL.

        Composed from modular mixins:
        - ProcHelpersVisitorMixin: Common helpers (field paths, durations, field lists)
        - ProcCoreVisitorMixin: Program, process definition
        - ProcExecutionVisitorMixin: Execution config (parallelism, time, mode)
        - ProcInputVisitorMixin: Input declarations (receive, store, match)
        - ProcProcessingVisitorMixin: Processing ops (enrich, transform, window, join)
        - ProcCorrelationVisitorMixin: Correlation (await, hold, completion)
        - ProcOutputVisitorMixin: Output and completion blocks
        - ProcStateVisitorMixin: State management (uses, local, buffer)
        - ProcResilienceVisitorMixin: Error handling, checkpoint, backpressure
        - ProcMarkersVisitorMixin: Business date, EOD markers, phases (v0.6.0+)
        """
        pass

    _AST_BUILDER_AVAILABLE = True

except (AttributeError, ImportError) as e:
    # Visitors reference parser contexts that don't exist in current grammar
    # Fall back to syntax-only mode
    import logging
    logging.getLogger(__name__).warning(
        f"AST builder unavailable (grammar/visitor mismatch): {e}. "
        "Using syntax-only validation mode."
    )
    _AST_BUILDER_AVAILABLE = False


class ProcParser(BaseParser):
    """Parser for L1 Process DSL files (.proc)."""

    def parse(self, content: str) -> ParseResult:
        """
        Parse Proc DSL content and return result.

        If AST builder is available, returns full AST.
        Otherwise, performs syntax validation only.
        """
        result = ParseResult(success=True)

        try:
            parser = self._setup_parser(ProcDSLLexer, ProcDSLParser, content)
            tree = parser.program()
            self._collect_errors(result)

            if result.success and _AST_BUILDER_AVAILABLE and ProcASTBuilder:
                try:
                    builder = ProcASTBuilder()
                    result.ast = builder.visitProgram(tree)
                except Exception as ast_error:
                    # AST building failed, but syntax was valid
                    # Add a warning but keep success=True
                    result.add_warning(f"AST building skipped: {ast_error}")

            result.parse_tree = tree

        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")

        return result
