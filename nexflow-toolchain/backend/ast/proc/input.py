"""
Process AST Input Block

Input-related dataclasses for process AST.
"""

from dataclasses import dataclass
from typing import Optional, List

from .common import SourceLocation


@dataclass
class SchemaDecl:
    """Schema reference declaration."""
    schema_name: str
    location: Optional[SourceLocation] = None


@dataclass
class ProjectClause:
    """Field projection clause."""
    fields: List[str]
    is_except: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class StoreAction:
    """Store in state action."""
    state_name: str
    location: Optional[SourceLocation] = None


@dataclass
class MatchAction:
    """Match from state action."""
    state_name: str
    on_fields: List[str]
    location: Optional[SourceLocation] = None


@dataclass
class ReceiveDecl:
    """Input receive declaration."""
    source: str
    alias: Optional[str] = None
    schema: Optional[SchemaDecl] = None
    project: Optional[ProjectClause] = None
    store_action: Optional[StoreAction] = None
    match_action: Optional[MatchAction] = None
    location: Optional[SourceLocation] = None


@dataclass
class InputBlock:
    """Process input declarations."""
    receives: List[ReceiveDecl]
    location: Optional[SourceLocation] = None
