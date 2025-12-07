"""
Schema AST Module

Re-exports all schema AST types for backward compatibility.
"""

# Enumerations
from .enums import (
    MutationPattern,
    CompatibilityMode,
    TimeSemantics,
    WatermarkStrategy,
    LateDataStrategy,
    IdleBehavior,
    RetentionPolicy,
    BaseType,
    FieldQualifierType,
)

# Common types
from .common import (
    SourceLocation,
    Duration,
    SizeSpec,
    FieldPath,
    RangeSpec,
    LengthSpec,
)

# Literals
from .literals import (
    StringLiteral,
    IntegerLiteral,
    DecimalLiteral,
    BooleanLiteral,
    NullLiteral,
    ListLiteral,
    Literal,
)

# Type system
from .types import (
    Constraint,
    CollectionType,
    FieldType,
    FieldQualifier,
    FieldDecl,
    IdentityBlock,
    FieldsBlock,
    NestedObjectBlock,
    TypeAlias,
    TypeAliasBlock,
)

# Blocks
from .blocks import (
    DeprecationDecl,
    VersionBlock,
    SparsityBlock,
    RetentionOptions,
    StreamingBlock,
    ActionCall,
    TransitionDecl,
    TransitionAction,
    StateMachineBlock,
    ParameterOption,
    ParameterDecl,
    ParametersBlock,
    EntryField,
    EntryDecl,
    EntriesBlock,
)

# Rules
from .rules import (
    RuleFieldDecl,
    Expression,
    Calculation,
    GivenBlock,
    CalculateBlock,
    ReturnBlock,
    RuleBlock,
    MigrationStatement,
    MigrationBlock,
)

# Program
from .program import (
    SchemaDefinition,
    Program,
)

__all__ = [
    # Enums
    'MutationPattern', 'CompatibilityMode', 'TimeSemantics', 'WatermarkStrategy',
    'LateDataStrategy', 'IdleBehavior', 'RetentionPolicy', 'BaseType', 'FieldQualifierType',
    # Common
    'SourceLocation', 'Duration', 'SizeSpec', 'FieldPath', 'RangeSpec', 'LengthSpec',
    # Literals
    'StringLiteral', 'IntegerLiteral', 'DecimalLiteral', 'BooleanLiteral',
    'NullLiteral', 'ListLiteral', 'Literal',
    # Types
    'Constraint', 'CollectionType', 'FieldType', 'FieldQualifier', 'FieldDecl',
    'IdentityBlock', 'FieldsBlock', 'NestedObjectBlock', 'TypeAlias', 'TypeAliasBlock',
    # Blocks
    'DeprecationDecl', 'VersionBlock', 'SparsityBlock', 'RetentionOptions', 'StreamingBlock',
    'ActionCall', 'TransitionDecl', 'TransitionAction', 'StateMachineBlock',
    'ParameterOption', 'ParameterDecl', 'ParametersBlock',
    'EntryField', 'EntryDecl', 'EntriesBlock',
    # Rules
    'RuleFieldDecl', 'Expression', 'Calculation', 'GivenBlock', 'CalculateBlock',
    'ReturnBlock', 'RuleBlock', 'MigrationStatement', 'MigrationBlock',
    # Program
    'SchemaDefinition', 'Program',
]
