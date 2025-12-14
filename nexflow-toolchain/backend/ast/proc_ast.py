# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow L1 (Flow/Process) AST Definitions

Python dataclass definitions for L1 Process Orchestration DSL AST nodes.
Maps directly to the ProcDSL.g4 grammar.

This module re-exports all types from the modular proc/ subpackage
for backward compatibility.
"""

# Re-export everything from the modular package
from .proc import *
