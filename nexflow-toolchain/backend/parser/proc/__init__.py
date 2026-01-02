# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Proc Parser Visitor Mixins

Modular visitor components for Proc/Process DSL AST building.
Each mixin handles a specific domain of the proc grammar.

Extended for markers and phases support.
"""

from .core_visitor import ProcCoreVisitorMixin
from .correlation_visitor import ProcCorrelationVisitorMixin
from .execution_visitor import ProcExecutionVisitorMixin
from .helpers_visitor import ProcHelpersVisitorMixin
from .input_visitor import ProcInputVisitorMixin
from .markers_visitor import ProcMarkersVisitorMixin
from .output_visitor import ProcOutputVisitorMixin
from .processing_visitor import ProcProcessingVisitorMixin
from .resilience_visitor import ProcResilienceVisitorMixin
from .state_visitor import ProcStateVisitorMixin

__all__ = [
    "ProcHelpersVisitorMixin",
    "ProcCoreVisitorMixin",
    "ProcExecutionVisitorMixin",
    "ProcInputVisitorMixin",
    "ProcProcessingVisitorMixin",
    "ProcCorrelationVisitorMixin",
    "ProcOutputVisitorMixin",
    "ProcStateVisitorMixin",
    "ProcResilienceVisitorMixin",
    "ProcMarkersVisitorMixin",
]
