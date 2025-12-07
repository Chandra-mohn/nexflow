"""
Process AST Top-Level Structures

Top-level program and process definition dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation
from .execution import ExecutionBlock
from .input import InputBlock
from .processing import EnrichDecl, TransformDecl, RouteDecl, AggregateDecl, WindowDecl, JoinDecl, MergeDecl
from .correlation import AwaitDecl, HoldDecl
from .output import OutputBlock, CompletionBlock
from .state import StateBlock
from .resilience import ResilienceBlock


@dataclass
class ProcessDefinition:
    """Complete process definition."""
    name: str
    execution: Optional[ExecutionBlock] = None
    input: Optional[InputBlock] = None
    processing: List[Union[EnrichDecl, TransformDecl, RouteDecl, AggregateDecl, WindowDecl, JoinDecl, MergeDecl]] = field(default_factory=list)
    correlation: Optional[Union[AwaitDecl, HoldDecl]] = None
    output: Optional[OutputBlock] = None
    completion: Optional[CompletionBlock] = None
    state: Optional[StateBlock] = None
    resilience: Optional[ResilienceBlock] = None
    location: Optional[SourceLocation] = None


@dataclass
class Program:
    """Top-level program containing process definitions."""
    processes: List[ProcessDefinition]
    location: Optional[SourceLocation] = None
