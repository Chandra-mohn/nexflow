# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Schema AST Module

Re-exports all schema AST types for backward compatibility.
"""

# Enumerations
from backend.ast.serialization import (
    CompatibilityMode as SerializationCompatibilityMode,
)

# Serialization
from backend.ast.serialization import (
    SerializationConfig,
    SerializationFormat,
)

# Blocks
from .blocks import (
    ActionCall,
    BinaryExpression,
    ComputedBlock,
    # Computed fields
    ComputedExpression,
    ComputedFieldDecl,
    ConstraintDecl,
    ConstraintsBlock,
    DeprecationDecl,
    EntriesBlock,
    EntryDecl,
    EntryField,
    FieldRefExpression,
    FunctionCallExpression,
    LiteralExpression,
    ParameterDecl,
    ParameterOption,
    ParametersBlock,
    RetentionOptions,
    SparsityBlock,
    StateMachineBlock,
    StreamingBlock,
    TransitionAction,
    TransitionDecl,
    UnaryExpression,
    VersionBlock,
    WhenBranch,
    WhenExpression,
)

# Common types
from .common import (
    Duration,
    FieldPath,
    LengthSpec,
    RangeSpec,
    SizeSpec,
    SourceLocation,
)
from .enums import (
    BaseType,
    CompatibilityMode,
    FieldQualifierType,
    IdleBehavior,
    LateDataStrategy,
    MutationPattern,
    RetentionPolicy,
    TimeSemantics,
    WatermarkStrategy,
)

# Literals
from .literals import (
    BooleanLiteral,
    DecimalLiteral,
    IntegerLiteral,
    ListLiteral,
    Literal,
    NullLiteral,
    StringLiteral,
)

# Program
from .program import (
    Program,
    SchemaDefinition,
)

# Rules
from .rules import (
    CalculateBlock,
    Calculation,
    Expression,
    GivenBlock,
    MigrationBlock,
    MigrationStatement,
    ReturnBlock,
    RuleBlock,
    RuleFieldDecl,
)

# Type system
from .types import (
    CollectionType,
    Constraint,
    FieldDecl,
    FieldQualifier,
    FieldsBlock,
    FieldType,
    IdentityBlock,
    NestedObjectBlock,
    TypeAlias,
    TypeAliasBlock,
)

__all__ = [
    # Enums
    "MutationPattern",
    "CompatibilityMode",
    "TimeSemantics",
    "WatermarkStrategy",
    "LateDataStrategy",
    "IdleBehavior",
    "RetentionPolicy",
    "BaseType",
    "FieldQualifierType",
    # Common
    "SourceLocation",
    "Duration",
    "SizeSpec",
    "FieldPath",
    "RangeSpec",
    "LengthSpec",
    # Literals
    "StringLiteral",
    "IntegerLiteral",
    "DecimalLiteral",
    "BooleanLiteral",
    "NullLiteral",
    "ListLiteral",
    "Literal",
    # Types
    "Constraint",
    "CollectionType",
    "FieldType",
    "FieldQualifier",
    "FieldDecl",
    "IdentityBlock",
    "FieldsBlock",
    "NestedObjectBlock",
    "TypeAlias",
    "TypeAliasBlock",
    # Blocks
    "DeprecationDecl",
    "VersionBlock",
    "SparsityBlock",
    "RetentionOptions",
    "StreamingBlock",
    "ActionCall",
    "TransitionDecl",
    "TransitionAction",
    "StateMachineBlock",
    "ParameterOption",
    "ParameterDecl",
    "ParametersBlock",
    "EntryField",
    "EntryDecl",
    "EntriesBlock",
    "ConstraintDecl",
    "ConstraintsBlock",
    # Computed fields
    "ComputedExpression",
    "BinaryExpression",
    "UnaryExpression",
    "FieldRefExpression",
    "LiteralExpression",
    "FunctionCallExpression",
    "WhenBranch",
    "WhenExpression",
    "ComputedFieldDecl",
    "ComputedBlock",
    # Rules
    "RuleFieldDecl",
    "Expression",
    "Calculation",
    "GivenBlock",
    "CalculateBlock",
    "ReturnBlock",
    "RuleBlock",
    "MigrationStatement",
    "MigrationBlock",
    # Program
    "SchemaDefinition",
    "Program",
    # Serialization
    "SerializationFormat",
    "SerializationConfig",
    "SerializationCompatibilityMode",
]
