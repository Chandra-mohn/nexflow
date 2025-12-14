# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow L4 (Business Rules) AST Definitions

Python dataclass definitions for L4 Business Rules DSL AST nodes.
Maps directly to the RulesDSL.g4 grammar.

Supports both:
- Decision Tables: Matrix-based logic for multi-condition scenarios
- Procedural Rules: Full if-then-elseif-else chains with nesting

This module re-exports all types from the modular rules/ subpackage
for backward compatibility.
"""

# Re-export everything from the modular package
from .rules import *
