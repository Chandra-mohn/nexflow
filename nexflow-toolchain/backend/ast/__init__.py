# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Nexflow AST Module
# Python dataclass definitions for AST nodes

# Common types (shared across all DSL levels)
from .common import ImportStatement, SourceLocation

from .proc_ast import (
    Program as ProcProgram,
    ProcessDefinition,
    ExecutionBlock,
    InputBlock,
    OutputBlock,
)

from .schema_ast import (
    Program as SchemaProgram,
    SchemaDefinition,
    MutationPattern,
    FieldDecl,
)

from .transform_ast import (
    Program as TransformProgram,
    TransformDef,
    TransformBlockDef,
)

from .rules_ast import (
    Program as RulesProgram,
    DecisionTableDef,
    ProceduralRuleDef,
)

__all__ = [
    # Common types
    'ImportStatement',
    'SourceLocation',
    # L1 - Process/Flow
    'ProcProgram',
    'ProcessDefinition',
    'ExecutionBlock',
    'InputBlock',
    'OutputBlock',
    # L2 - Schema
    'SchemaProgram',
    'SchemaDefinition',
    'MutationPattern',
    'FieldDecl',
    # L3 - Transform
    'TransformProgram',
    'TransformDef',
    'TransformBlockDef',
    # L4 - Rules
    'RulesProgram',
    'DecisionTableDef',
    'ProceduralRuleDef',
]
