# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform AST Module

Re-exports all transform AST types for backward compatibility.
"""

# Enumerations
from .enums import (
    CompatibilityMode,
    ComposeType,
    SeverityLevel,
    LogLevel,
    ErrorActionType,
    QualifierType,
    BaseType,
    CalendarFunction,
    UnaryOp,
    ArithmeticOp,
    ComparisonOp,
    LogicalOp,
)

# Common types
from .common import (
    SourceLocation,
    Duration,
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
    Qualifier,
)

# Expressions
from .expressions import (
    FunctionCall,
    WhenBranch,
    WhenExpression,
    IndexExpression,
    OptionalChainExpression,
    UnaryExpression,
    BinaryExpression,
    BetweenExpression,
    InExpression,
    IsNullExpression,
    ParenExpression,
    LambdaExpression,
    ObjectLiteralField,
    ObjectLiteral,
    Expression,
)

# Specs
from .specs import (
    InputFieldDecl,
    OutputFieldDecl,
    InputSpec,
    OutputSpec,
)

# Metadata
from .metadata import (
    TransformMetadata,
    CacheDecl,
    LookupRef,
    LookupsBlock,
    ParamDecl,
    ParamsBlock,
)

# Blocks
from .blocks import (
    Assignment,
    LocalAssignment,
    ApplyBlock,
    Mapping,
    MappingsBlock,
    ComposeRef,
    ComposeBlock,
    ValidationMessageObject,
    ValidationRule,
    ValidateInputBlock,
    ValidateOutputBlock,
    InvariantBlock,
    ErrorAction,
    OnErrorBlock,
    RecalculateBlock,
    OnChangeBlock,
)

# Program
from .program import (
    TransformDef,
    UseBlock,
    TransformBlockDef,
    Program,
)

__all__ = [
    # Enums
    'CompatibilityMode', 'ComposeType', 'SeverityLevel', 'LogLevel', 'ErrorActionType',
    'QualifierType', 'BaseType', 'CalendarFunction', 'UnaryOp', 'ArithmeticOp', 'ComparisonOp', 'LogicalOp',
    # Common
    'SourceLocation', 'Duration', 'FieldPath', 'RangeSpec', 'LengthSpec',
    # Literals
    'StringLiteral', 'IntegerLiteral', 'DecimalLiteral', 'BooleanLiteral',
    'NullLiteral', 'ListLiteral', 'Literal',
    # Types
    'Constraint', 'CollectionType', 'FieldType', 'Qualifier',
    # Expressions
    'FunctionCall', 'WhenBranch', 'WhenExpression', 'IndexExpression',
    'OptionalChainExpression', 'UnaryExpression', 'BinaryExpression',
    'BetweenExpression', 'InExpression', 'IsNullExpression', 'ParenExpression',
    'LambdaExpression', 'ObjectLiteralField', 'ObjectLiteral', 'Expression',
    # Specs
    'InputFieldDecl', 'OutputFieldDecl', 'InputSpec', 'OutputSpec',
    # Metadata
    'TransformMetadata', 'CacheDecl', 'LookupRef', 'LookupsBlock', 'ParamDecl', 'ParamsBlock',
    # Blocks
    'Assignment', 'LocalAssignment', 'ApplyBlock', 'Mapping', 'MappingsBlock',
    'ComposeRef', 'ComposeBlock', 'ValidationMessageObject', 'ValidationRule',
    'ValidateInputBlock', 'ValidateOutputBlock', 'InvariantBlock',
    'ErrorAction', 'OnErrorBlock', 'RecalculateBlock', 'OnChangeBlock',
    # Program
    'TransformDef', 'UseBlock', 'TransformBlockDef', 'Program',
]
