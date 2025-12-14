# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
L6 Master Compiler

Orchestrates the full Nexflow compilation pipeline:
- L2 Schema parsing and type generation
- L3 Transform parsing and function generation
- L4 Rules parsing and decision table generation
- L5 Infrastructure binding resolution
- L1 Flow parsing with infrastructure-aware code generation

The compiler ensures proper ordering and dependency resolution between layers.
"""

from .master_compiler import (
    MasterCompiler,
    CompilationResult,
    CompilationPhase,
    LayerResult,
)

__all__ = [
    "MasterCompiler",
    "CompilationResult",
    "CompilationPhase",
    "LayerResult",
]
