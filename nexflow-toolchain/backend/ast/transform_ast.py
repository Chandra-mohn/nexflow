# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow L3 (Transform Catalog) AST Definitions

Python dataclass definitions for L3 Transform Catalog DSL AST nodes.
Maps directly to the TransformDSL.g4 grammar.

This module re-exports all types from the modular transform/ subpackage
for backward compatibility.
"""

# Explicit re-exports from the modular package (no wildcard imports)
from .transform import (
    # Enums
    CompatibilityMode, ComposeType, SeverityLevel, LogLevel, ErrorActionType,
    QualifierType, BaseType, CalendarFunction, UnaryOp, ArithmeticOp, ComparisonOp, LogicalOp,
    # Common
    SourceLocation, Duration, FieldPath, RangeSpec, LengthSpec,
    # Literals
    StringLiteral, IntegerLiteral, DecimalLiteral, BooleanLiteral,
    NullLiteral, ListLiteral, Literal,
    # Types
    Constraint, CollectionType, FieldType, Qualifier,
    # Expressions
    FunctionCall, WhenBranch, WhenExpression, IndexExpression,
    OptionalChainExpression, UnaryExpression, BinaryExpression,
    BetweenExpression, InExpression, IsNullExpression, ParenExpression,
    LambdaExpression, ObjectLiteralField, ObjectLiteral, Expression,
    # Specs
    InputFieldDecl, OutputFieldDecl, InputSpec, OutputSpec,
    # Metadata
    TransformMetadata, CacheDecl, LookupRef, LookupsBlock, ParamDecl, ParamsBlock,
    # Blocks
    Assignment, LocalAssignment, ApplyBlock, Mapping, MappingsBlock,
    ComposeRef, ComposeBlock, ValidationMessageObject, ValidationRule,
    ValidateInputBlock, ValidateOutputBlock, InvariantBlock,
    ErrorAction, OnErrorBlock, RecalculateBlock, OnChangeBlock,
    # Program
    TransformDef, UseBlock, TransformBlockDef, Program,
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
