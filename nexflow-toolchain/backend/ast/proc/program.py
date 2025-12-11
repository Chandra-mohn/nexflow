"""
Process AST Top-Level Structures

Top-level program and process definition dataclasses.

Updated for grammar v0.5.0+ which uses bodyContent for flexible ordering
instead of separate inputBlock/outputBlock.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union, Any

from .common import SourceLocation
from .execution import ExecutionBlock
from .input import ReceiveDecl
from .processing import EnrichDecl, TransformDecl, RouteDecl, AggregateDecl, WindowDecl, JoinDecl, MergeDecl
from .correlation import AwaitDecl, HoldDecl
from .output import EmitDecl, CompletionBlock
from .state import StateBlock
from .resilience import ResilienceBlock


# Type alias for processing operations
ProcessingOp = Union[EnrichDecl, TransformDecl, RouteDecl, AggregateDecl, WindowDecl, JoinDecl, MergeDecl, Any]


@dataclass
class ProcessDefinition:
    """
    Complete process definition.

    v0.5.0+: Uses lists for receives, emits, correlations, completions
    instead of single inputBlock/outputBlock containers.
    """
    name: str
    execution: Optional[ExecutionBlock] = None
    # v0.5.0+: Direct lists instead of block containers
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


@dataclass
class Program:
    """Top-level program containing process definitions."""
    processes: List[ProcessDefinition]
    location: Optional[SourceLocation] = None
