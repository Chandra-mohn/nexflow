# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Proc Parser Visitor Mixins

Modular visitor components for Proc/Process DSL AST building.
Each mixin handles a specific domain of the proc grammar.

Extended for v0.6.0+ with markers and phases support.
"""

from .helpers_visitor import ProcHelpersVisitorMixin
from .core_visitor import ProcCoreVisitorMixin
from .execution_visitor import ProcExecutionVisitorMixin
from .input_visitor import ProcInputVisitorMixin
from .processing_visitor import ProcProcessingVisitorMixin
from .correlation_visitor import ProcCorrelationVisitorMixin
from .output_visitor import ProcOutputVisitorMixin
from .state_visitor import ProcStateVisitorMixin
from .resilience_visitor import ProcResilienceVisitorMixin
from .markers_visitor import ProcMarkersVisitorMixin

__all__ = [
    'ProcHelpersVisitorMixin',
    'ProcCoreVisitorMixin',
    'ProcExecutionVisitorMixin',
    'ProcInputVisitorMixin',
    'ProcProcessingVisitorMixin',
    'ProcCorrelationVisitorMixin',
    'ProcOutputVisitorMixin',
    'ProcStateVisitorMixin',
    'ProcResilienceVisitorMixin',
    'ProcMarkersVisitorMixin',
]
