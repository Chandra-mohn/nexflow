# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules AST Top-Level Program

Top-level program containing rule definitions.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from .common import SourceLocation

if TYPE_CHECKING:
    from backend.ast.common import ImportStatement
from .actions import ActionsBlock
from .decision_table import DecisionTableDef
from .procedural import ProceduralRuleDef
from .services import ServicesBlock


@dataclass
class Program:
    """Top-level program containing rule definitions."""

    decision_tables: List[DecisionTableDef] = field(default_factory=list)
    procedural_rules: List[ProceduralRuleDef] = field(default_factory=list)
    services: Optional[ServicesBlock] = None
    actions: Optional[ActionsBlock] = None
    imports: List["ImportStatement"] = field(default_factory=list)
    location: Optional[SourceLocation] = None
