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

# Explicit re-exports from the modular package (no wildcard imports)
from .rules import (
    # Enums
    HitPolicyType, ExecuteType, BaseType, ComparisonOp, PatternMatchType, LogicalOp,
    MarkerStateType, CalendarFunction,
    # Common
    SourceLocation, FieldPath,
    # Literals
    StringLiteral, IntegerLiteral, DecimalLiteral, MoneyLiteral,
    PercentageLiteral, BooleanLiteral, NullLiteral, ListLiteral, Literal,
    # Conditions
    WildcardCondition, ExactMatchCondition, RangeCondition, SetCondition,
    PatternCondition, NullCondition, ComparisonCondition, ExpressionCondition,
    MarkerStateCondition, Condition,
    # Actions
    NoAction, AssignAction, CalculateAction, LookupAction, ActionArg, CallAction, EmitAction, Action,
    # Action declarations (RFC Solution 5)
    ActionTargetType, ActionDeclParam, EmitTarget, StateOperation, StateTarget,
    AuditTarget, CallTarget, ActionDecl, ActionsBlock,
    # Expressions
    FunctionCall, UnaryExpr, BinaryExpr, ParenExpr, ValueExpr,
    ComparisonExpr, BooleanFactor, BooleanTerm, BooleanExpr,
    # Collection expressions
    CollectionFunctionType, CollectionPredicateComparison, CollectionPredicateIn,
    CollectionPredicateNull, CollectionPredicateNot, CollectionPredicateAtom,
    CollectionPredicateCompound, LambdaPredicate, MultiParamLambdaPredicate,
    CollectionPredicate, CollectionExpr,
    # Decision table
    InputParam, ReturnParam, GivenBlock, ColumnHeader, TableCell, TableRow,
    TableMatrix, DecideBlock, ReturnSpec, ExecuteSpec, DecisionTableDef,
    # Procedural
    ActionCallStmt, ActionSequence, ReturnStatement, SetStatement, LetStatement,
    Block, ElseIfBranch, RuleStep, BlockItem, ProceduralRuleDef,
    # Services
    ServiceType, DurationUnit, Duration, ServiceParam, ServiceOptions,
    ServiceDecl, ServicesBlock,
    # Program
    Program,
)

__all__ = [
    # Enums
    'HitPolicyType', 'ExecuteType', 'BaseType', 'ComparisonOp', 'PatternMatchType', 'LogicalOp',
    'MarkerStateType', 'CalendarFunction',
    # Common
    'SourceLocation', 'FieldPath',
    # Literals
    'StringLiteral', 'IntegerLiteral', 'DecimalLiteral', 'MoneyLiteral',
    'PercentageLiteral', 'BooleanLiteral', 'NullLiteral', 'ListLiteral', 'Literal',
    # Conditions
    'WildcardCondition', 'ExactMatchCondition', 'RangeCondition', 'SetCondition',
    'PatternCondition', 'NullCondition', 'ComparisonCondition', 'ExpressionCondition',
    'MarkerStateCondition', 'Condition',
    # Actions
    'NoAction', 'AssignAction', 'CalculateAction', 'LookupAction', 'ActionArg', 'CallAction', 'EmitAction', 'Action',
    # Action declarations
    'ActionTargetType', 'ActionDeclParam', 'EmitTarget', 'StateOperation', 'StateTarget',
    'AuditTarget', 'CallTarget', 'ActionDecl', 'ActionsBlock',
    # Expressions
    'FunctionCall', 'UnaryExpr', 'BinaryExpr', 'ParenExpr', 'ValueExpr',
    'ComparisonExpr', 'BooleanFactor', 'BooleanTerm', 'BooleanExpr',
    # Collection expressions
    'CollectionFunctionType', 'CollectionPredicateComparison', 'CollectionPredicateIn',
    'CollectionPredicateNull', 'CollectionPredicateNot', 'CollectionPredicateAtom',
    'CollectionPredicateCompound', 'LambdaPredicate', 'MultiParamLambdaPredicate',
    'CollectionPredicate', 'CollectionExpr',
    # Decision table
    'InputParam', 'ReturnParam', 'GivenBlock', 'ColumnHeader', 'TableCell', 'TableRow',
    'TableMatrix', 'DecideBlock', 'ReturnSpec', 'ExecuteSpec', 'DecisionTableDef',
    # Procedural
    'ActionCallStmt', 'ActionSequence', 'ReturnStatement', 'SetStatement', 'LetStatement',
    'Block', 'ElseIfBranch', 'RuleStep', 'BlockItem', 'ProceduralRuleDef',
    # Services
    'ServiceType', 'DurationUnit', 'Duration', 'ServiceParam', 'ServiceOptions',
    'ServiceDecl', 'ServicesBlock',
    # Program
    'Program',
]
