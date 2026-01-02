# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Top-Level Structures

Top-level program and process definition dataclasses.

Updated for grammar which uses bodyContent for flexible ordering
instead of separate inputBlock/outputBlock.

Extended for EOD markers and phases
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional, Union

from .common import SourceLocation

if TYPE_CHECKING:
    from backend.ast.common import ImportStatement
from .correlation import AwaitDecl, HoldDecl
from .execution import ExecutionBlock
from .input import ReceiveDecl
from .markers import BusinessDateDecl, MarkersBlock, PhaseBlock, ProcessingDateDecl
from .output import CompletionBlock, EmitDecl
from .processing import (
    AggregateDecl,
    EnrichDecl,
    JoinDecl,
    MergeDecl,
    RouteDecl,
    TransformDecl,
    WindowDecl,
)
from .resilience import ResilienceBlock
from .state import StateBlock

# Type alias for processing operations
ProcessingOp = Union[
    EnrichDecl,
    TransformDecl,
    RouteDecl,
    AggregateDecl,
    WindowDecl,
    JoinDecl,
    MergeDecl,
    Any,
]


@dataclass
class ProcessDefinition:
    """
    Complete process definition.

    Uses lists for receives, emits, correlations, completions
    instead of single inputBlock/outputBlock containers.

    Extended for EOD markers and phases:
    - business_date: Calendar reference for business date resolution
    - markers: EOD marker definitions
    - phases: Phase blocks containing statements

    Extended for processing date:
    - processing_date: System time when record is processed (auto mode)
    """

    name: str
    execution: Optional[ExecutionBlock] = None
    business_date: Optional[BusinessDateDecl] = None
    processing_date: Optional[ProcessingDateDecl] = None  # system time
    markers: Optional[MarkersBlock] = None
    phases: List[PhaseBlock] = field(default_factory=list)
    receives: List[ReceiveDecl] = field(default_factory=list)
    processing: List[ProcessingOp] = field(default_factory=list)
    emits: List[EmitDecl] = field(default_factory=list)
    correlations: List[Union[AwaitDecl, HoldDecl]] = field(default_factory=list)
    completions: List[CompletionBlock] = field(default_factory=list)
    state: Optional[StateBlock] = None
    resilience: Optional[ResilienceBlock] = None
    location: Optional[SourceLocation] = None

    # Backward compatibility properties
    @property
    def input(self):
        """Backward compatibility: returns first receive or None."""
        return self.receives[0] if self.receives else None

    @property
    def output(self):
        """Backward compatibility: returns first emit or None."""
        return self.emits[0] if self.emits else None

    @property
    def correlation(self):
        """Backward compatibility: returns first correlation or None."""
        return self.correlations[0] if self.correlations else None

    @property
    def completion(self):
        """Backward compatibility: returns first completion or None."""
        return self.completions[0] if self.completions else None

    # Helper methods for markers and phases
    def has_markers(self) -> bool:
        """Check if process has markers defined."""
        return self.markers is not None and len(self.markers.markers) > 0

    def has_phases(self) -> bool:
        """Check if process uses phase-based execution."""
        return len(self.phases) > 0

    def has_business_date(self) -> bool:
        """Check if process references a business calendar."""
        return self.business_date is not None

    def has_processing_date(self) -> bool:
        """Check if process uses processing date."""
        return self.processing_date is not None

    def is_phase_based(self) -> bool:
        """Check if process uses phase-based execution model.

        A process is phase-based if it has either markers or phases defined.
        Non-phase-based processes use the traditional statement model.
        """
        return self.has_markers() or self.has_phases()


@dataclass
class Program:
    """Top-level program containing process definitions."""

    processes: List[ProcessDefinition]
    imports: List["ImportStatement"] = field(default_factory=list)
    location: Optional[SourceLocation] = None
