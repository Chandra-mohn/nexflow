# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Decision Table Components

Decision table structure types.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation
from .enums import BaseType, HitPolicyType, ExecuteType
from .conditions import Condition
from .actions import Action


@dataclass
class InputParam:
    """Input parameter declaration."""
    name: str
    param_type: Union[BaseType, str]  # BaseType or custom type name
    comment: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class ReturnParam:
    """Return parameter declaration."""
    name: str
    param_type: Union[BaseType, str]
    location: Optional[SourceLocation] = None


@dataclass
class GivenBlock:
    """Given block with input parameters."""
    params: List[InputParam]
    location: Optional[SourceLocation] = None


@dataclass
class ColumnHeader:
    """Decision table column header."""
    name: str
    location: Optional[SourceLocation] = None


@dataclass
class TableCell:
    """Decision table cell content."""
    content: Union[Condition, Action]
    location: Optional[SourceLocation] = None


@dataclass
class TableRow:
    """Decision table row."""
    priority: Optional[int] = None
    cells: List[TableCell] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class TableMatrix:
    """Decision table matrix."""
    headers: List[ColumnHeader]
    has_priority: bool = False
    rows: List[TableRow] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class DecideBlock:
    """Decide block with table matrix."""
    matrix: TableMatrix
    location: Optional[SourceLocation] = None


@dataclass
class ReturnSpec:
    """Return specification."""
    params: List[ReturnParam]
    location: Optional[SourceLocation] = None


@dataclass
class ExecuteSpec:
    """Execute specification."""
    execute_type: ExecuteType
    custom_name: Optional[str] = None  # For custom execute type
    location: Optional[SourceLocation] = None


@dataclass
class DecisionTableDef:
    """Decision table definition."""
    name: str
    hit_policy: Optional[HitPolicyType] = None
    description: Optional[str] = None
    given: Optional[GivenBlock] = None
    decide: Optional[DecideBlock] = None
    return_spec: Optional[ReturnSpec] = None
    execute_spec: Optional[ExecuteSpec] = None
    location: Optional[SourceLocation] = None
