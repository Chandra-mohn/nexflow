# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Execution Block

Execution-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation, Duration, FieldPath
from .enums import ModeType


@dataclass
class WatermarkDecl:
    """Watermark delay declaration."""
    delay: Duration
    location: Optional[SourceLocation] = None


@dataclass
class LateDataDecl:
    """Late data routing declaration."""
    target: str
    location: Optional[SourceLocation] = None


@dataclass
class LatenessDecl:
    """Allowed lateness declaration."""
    duration: Duration
    location: Optional[SourceLocation] = None


@dataclass
class TimeDecl:
    """Time configuration declaration."""
    time_field: FieldPath
    watermark: Optional[WatermarkDecl] = None
    late_data: Optional[LateDataDecl] = None
    lateness: Optional[LatenessDecl] = None
    location: Optional[SourceLocation] = None


@dataclass
class ModeDecl:
    """Execution mode declaration."""
    mode: ModeType
    micro_batch_interval: Optional[Duration] = None
    location: Optional[SourceLocation] = None


@dataclass
class ExecutionBlock:
    """Process execution configuration."""
    parallelism: Optional[int] = None
    parallelism_hint: bool = False
    partition_by: Optional[List[str]] = None
    time: Optional[TimeDecl] = None
    mode: Optional[ModeDecl] = None
    location: Optional[SourceLocation] = None
