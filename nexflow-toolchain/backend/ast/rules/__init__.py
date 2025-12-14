"""
Rules AST Module

Re-exports all rules AST types for backward compatibility.
"""

# Enumerations
from .enums import (
    HitPolicyType,
    ExecuteType,
    BaseType,
    ComparisonOp,
    PatternMatchType,
    LogicalOp,
    MarkerStateType,
    CalendarFunction,
)

# Common types
from .common import (
    SourceLocation,
    FieldPath,
)

# Literals
from .literals import (
    StringLiteral,
    IntegerLiteral,
    DecimalLiteral,
    MoneyLiteral,
    PercentageLiteral,
    BooleanLiteral,
    NullLiteral,
    ListLiteral,
    Literal,
)

# Conditions
from .conditions import (
    WildcardCondition,
    ExactMatchCondition,
    RangeCondition,
    SetCondition,
    PatternCondition,
    NullCondition,
    ComparisonCondition,
    ExpressionCondition,
    MarkerStateCondition,
    Condition,
)

# Actions
from .actions import (
    NoAction,
    AssignAction,
    CalculateAction,
    LookupAction,
    ActionArg,
    CallAction,
    EmitAction,
    Action,
    # Action declarations (RFC Solution 5)
    ActionTargetType,
    ActionDeclParam,
    EmitTarget,
    StateOperation,
    StateTarget,
    AuditTarget,
    CallTarget,
    ActionDecl,
    ActionsBlock,
)

# Expressions
from .expressions import (
    FunctionCall,
    UnaryExpr,
    BinaryExpr,
    ParenExpr,
    ValueExpr,
    ComparisonExpr,
    BooleanFactor,
    BooleanTerm,
    BooleanExpr,
)

# Collection expressions (RFC: Collection Operations Instead of Loops)
from .collections import (
    CollectionFunctionType,
    CollectionPredicateComparison,
    CollectionPredicateIn,
    CollectionPredicateNull,
    CollectionPredicateNot,
    CollectionPredicateAtom,
    CollectionPredicateCompound,
    LambdaPredicate,
    MultiParamLambdaPredicate,
    CollectionPredicate,
    CollectionExpr,
)

# Decision table
from .decision_table import (
    InputParam,
    ReturnParam,
    GivenBlock,
    ColumnHeader,
    TableCell,
    TableRow,
    TableMatrix,
    DecideBlock,
    ReturnSpec,
    ExecuteSpec,
    DecisionTableDef,
)

# Procedural
from .procedural import (
    ActionCallStmt,
    ActionSequence,
    ReturnStatement,
    SetStatement,
    LetStatement,
    Block,
    ElseIfBranch,
    RuleStep,
    BlockItem,
    ProceduralRuleDef,
)

# Services
from .services import (
    ServiceType,
    DurationUnit,
    Duration,
    ServiceParam,
    ServiceOptions,
    ServiceDecl,
    ServicesBlock,
)

# Program
from .program import (
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
    # Action declarations (RFC Solution 5)
    'ActionTargetType', 'ActionDeclParam', 'EmitTarget', 'StateOperation', 'StateTarget',
    'AuditTarget', 'CallTarget', 'ActionDecl', 'ActionsBlock',
    # Expressions
    'FunctionCall', 'UnaryExpr', 'BinaryExpr', 'ParenExpr', 'ValueExpr',
    'ComparisonExpr', 'BooleanFactor', 'BooleanTerm', 'BooleanExpr',
    # Collection expressions (RFC: Collection Operations Instead of Loops)
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
