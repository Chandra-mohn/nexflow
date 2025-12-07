"""
Flow DSL (L1) Parser

Parser wrapper for L1 Process Orchestration DSL with AST building.
Uses modular visitor mixins for maintainability.
"""

from .base import BaseParser, ParseResult
from .generated.proc import ProcDSLLexer, ProcDSLParser, ProcDSLVisitor
from .flow import (
    FlowHelpersVisitorMixin,
    FlowCoreVisitorMixin,
    FlowExecutionVisitorMixin,
    FlowInputVisitorMixin,
    FlowProcessingVisitorMixin,
    FlowCorrelationVisitorMixin,
    FlowOutputVisitorMixin,
    FlowStateVisitorMixin,
    FlowResilienceVisitorMixin,
)


class FlowASTBuilder(
    FlowHelpersVisitorMixin,
    FlowCoreVisitorMixin,
    FlowExecutionVisitorMixin,
    FlowInputVisitorMixin,
    FlowProcessingVisitorMixin,
    FlowCorrelationVisitorMixin,
    FlowOutputVisitorMixin,
    FlowStateVisitorMixin,
    FlowResilienceVisitorMixin,
    ProcDSLVisitor
):
    """
    Visitor that builds AST from ANTLR parse tree for L1 Flow DSL.

    Composed from modular mixins:
    - FlowHelpersVisitorMixin: Common helpers (field paths, durations, field lists)
    - FlowCoreVisitorMixin: Program, process definition
    - FlowExecutionVisitorMixin: Execution config (parallelism, time, mode)
    - FlowInputVisitorMixin: Input declarations (receive, store, match)
    - FlowProcessingVisitorMixin: Processing ops (enrich, transform, window, join)
    - FlowCorrelationVisitorMixin: Correlation (await, hold, completion)
    - FlowOutputVisitorMixin: Output and completion blocks
    - FlowStateVisitorMixin: State management (uses, local, buffer)
    - FlowResilienceVisitorMixin: Error handling, checkpoint, backpressure
    """
    pass


class FlowParser(BaseParser):
    """Parser for L1 Flow/Process DSL files."""

    def parse(self, content: str) -> ParseResult:
        """Parse Flow DSL content and return AST."""
        result = ParseResult(success=True)

        try:
            parser = self._setup_parser(ProcDSLLexer, ProcDSLParser, content)
            tree = parser.program()
            self._collect_errors(result)

            if result.success:
                builder = FlowASTBuilder()
                result.ast = builder.visitProgram(tree)
                result.parse_tree = tree

        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")

        return result
