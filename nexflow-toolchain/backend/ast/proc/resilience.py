"""
Process AST Resilience Block

Resilience-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation, Duration
from .enums import ErrorType, ErrorActionType, BackpressureStrategy


@dataclass
class ErrorAction:
    """Error handler action."""
    action_type: ErrorActionType
    target: Optional[str] = None  # For dead_letter
    retry_count: Optional[int] = None  # For retry
    location: Optional[SourceLocation] = None


@dataclass
class ErrorHandler:
    """Error handler declaration."""
    error_type: ErrorType
    action: ErrorAction
    location: Optional[SourceLocation] = None


@dataclass
class ErrorBlock:
    """Error handling block."""
    handlers: List[ErrorHandler]
    location: Optional[SourceLocation] = None


@dataclass
class CheckpointBlock:
    """Checkpoint configuration."""
    interval: Duration
    storage: str
    location: Optional[SourceLocation] = None


@dataclass
class AlertDecl:
    """Alert configuration."""
    after: Duration
    location: Optional[SourceLocation] = None


@dataclass
class BackpressureBlock:
    """Backpressure handling configuration."""
    strategy: BackpressureStrategy
    sample_rate: Optional[float] = None  # For sample strategy
    alert: Optional[AlertDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class ResilienceBlock:
    """Resilience configuration."""
    error: Optional[ErrorBlock] = None
    checkpoint: Optional[CheckpointBlock] = None
    backpressure: Optional[BackpressureBlock] = None
    location: Optional[SourceLocation] = None
