"""
Rules AST Top-Level Program

Top-level program containing rule definitions.
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .common import SourceLocation
from .decision_table import DecisionTableDef
from .procedural import ProceduralRuleDef
from .services import ServicesBlock
from .actions import ActionsBlock


@dataclass
class Program:
    """Top-level program containing rule definitions."""
    decision_tables: List[DecisionTableDef] = field(default_factory=list)
    procedural_rules: List[ProceduralRuleDef] = field(default_factory=list)
    services: Optional[ServicesBlock] = None
    actions: Optional[ActionsBlock] = None
    location: Optional[SourceLocation] = None
