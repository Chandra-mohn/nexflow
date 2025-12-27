# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow L2 (Schema Registry) AST Definitions

Python dataclass definitions for L2 Schema Registry DSL AST nodes.
Maps directly to the SchemaDSL.g4 grammar.

This module re-exports all types from the modular schema/ subpackage
for backward compatibility.
"""

# Explicit re-exports from the modular package (no wildcard imports)
from .schema import (
    # Enums
    MutationPattern, CompatibilityMode, TimeSemantics, WatermarkStrategy,
    LateDataStrategy, IdleBehavior, RetentionPolicy, BaseType, FieldQualifierType,
    # Common
    SourceLocation, Duration, SizeSpec, FieldPath, RangeSpec, LengthSpec,
    # Literals
    StringLiteral, IntegerLiteral, DecimalLiteral, BooleanLiteral,
    NullLiteral, ListLiteral, Literal,
    # Types
    Constraint, CollectionType, FieldType, FieldQualifier, FieldDecl,
    IdentityBlock, FieldsBlock, NestedObjectBlock, TypeAlias, TypeAliasBlock,
    # Blocks
    DeprecationDecl, VersionBlock, SparsityBlock, RetentionOptions, StreamingBlock,
    ActionCall, TransitionDecl, TransitionAction, StateMachineBlock,
    ParameterOption, ParameterDecl, ParametersBlock,
    EntryField, EntryDecl, EntriesBlock,
    ConstraintDecl, ConstraintsBlock,
    # Computed fields
    ComputedExpression, BinaryExpression, UnaryExpression, FieldRefExpression,
    LiteralExpression, FunctionCallExpression, WhenBranch, WhenExpression,
    ComputedFieldDecl, ComputedBlock,
    # Rules
    RuleFieldDecl, Expression, Calculation, GivenBlock, CalculateBlock,
    ReturnBlock, RuleBlock, MigrationStatement, MigrationBlock,
    # Program
    SchemaDefinition, Program,
    # Serialization
    SerializationFormat, SerializationConfig, SerializationCompatibilityMode,
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
    'ConstraintDecl', 'ConstraintsBlock',
    # Computed fields
    'ComputedExpression', 'BinaryExpression', 'UnaryExpression', 'FieldRefExpression',
    'LiteralExpression', 'FunctionCallExpression', 'WhenBranch', 'WhenExpression',
    'ComputedFieldDecl', 'ComputedBlock',
    # Rules
    'RuleFieldDecl', 'Expression', 'Calculation', 'GivenBlock', 'CalculateBlock',
    'ReturnBlock', 'RuleBlock', 'MigrationStatement', 'MigrationBlock',
    # Program
    'SchemaDefinition', 'Program',
    # Serialization
    'SerializationFormat', 'SerializationConfig', 'SerializationCompatibilityMode',
]
