# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Procedural Rule Components

Procedural rule structure types.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union

from .common import SourceLocation
from .expressions import ValueExpr, BooleanExpr


@dataclass
class ActionCallStmt:
    """Action call statement in procedural rule."""
    name: str  # Can be identifier or quoted string
    arguments: List[ValueExpr] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class ActionSequence:
    """Sequence of action calls."""
    actions: List[ActionCallStmt]
    location: Optional[SourceLocation] = None


@dataclass
class ReturnStatement:
    """Return statement (exits rule)."""
    location: Optional[SourceLocation] = None


@dataclass
class SetStatement:
    """Set statement: set variable = expression."""
    variable: str
    value: ValueExpr
    location: Optional[SourceLocation] = None


@dataclass
class LetStatement:
    """Let statement: let variable = expression."""
    variable: str
    value: ValueExpr
    location: Optional[SourceLocation] = None


@dataclass
class Block:
    """Block of statements in procedural rule."""
    items: List['BlockItem']
    location: Optional[SourceLocation] = None


@dataclass
class ElseIfBranch:
    """Else-if branch in conditional."""
    condition: BooleanExpr
    block: Block
    location: Optional[SourceLocation] = None


@dataclass
class RuleStep:
    """If-then-elseif-else conditional step."""
    condition: BooleanExpr
    then_block: Block
    elseif_branches: List[ElseIfBranch] = field(default_factory=list)
    else_block: Optional[Block] = None
    location: Optional[SourceLocation] = None


BlockItem = Union[RuleStep, ActionSequence, ReturnStatement, SetStatement, LetStatement]


@dataclass
class ProceduralRuleDef:
    """Procedural rule definition."""
    name: str  # Can be identifier or quoted string
    items: List[BlockItem] = field(default_factory=list)
    location: Optional[SourceLocation] = None
