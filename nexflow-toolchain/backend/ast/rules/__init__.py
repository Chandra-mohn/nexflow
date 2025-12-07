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
    Block,
    ElseIfBranch,
    RuleStep,
    BlockItem,
    ProceduralRuleDef,
)

# Program
from .program import (
    Program,
)

__all__ = [
    # Enums
    'HitPolicyType', 'ExecuteType', 'BaseType', 'ComparisonOp', 'PatternMatchType', 'LogicalOp',
    # Common
    'SourceLocation', 'FieldPath',
    # Literals
    'StringLiteral', 'IntegerLiteral', 'DecimalLiteral', 'MoneyLiteral',
    'PercentageLiteral', 'BooleanLiteral', 'NullLiteral', 'ListLiteral', 'Literal',
    # Conditions
    'WildcardCondition', 'ExactMatchCondition', 'RangeCondition', 'SetCondition',
    'PatternCondition', 'NullCondition', 'ComparisonCondition', 'ExpressionCondition', 'Condition',
    # Actions
    'NoAction', 'AssignAction', 'CalculateAction', 'LookupAction', 'ActionArg', 'CallAction', 'EmitAction', 'Action',
    # Expressions
    'FunctionCall', 'UnaryExpr', 'BinaryExpr', 'ParenExpr', 'ValueExpr',
    'ComparisonExpr', 'BooleanFactor', 'BooleanTerm', 'BooleanExpr',
    # Decision table
    'InputParam', 'ReturnParam', 'GivenBlock', 'ColumnHeader', 'TableCell', 'TableRow',
    'TableMatrix', 'DecideBlock', 'ReturnSpec', 'ExecuteSpec', 'DecisionTableDef',
    # Procedural
    'ActionCallStmt', 'ActionSequence', 'ReturnStatement', 'Block', 'ElseIfBranch',
    'RuleStep', 'BlockItem', 'ProceduralRuleDef',
    # Program
    'Program',
]
