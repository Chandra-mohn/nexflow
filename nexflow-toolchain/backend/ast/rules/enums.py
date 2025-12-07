"""
Rules AST Enumerations

All enum types used in the Rules DSL AST.
"""

from enum import Enum


class HitPolicyType(Enum):
    FIRST_MATCH = "first_match"
    SINGLE_HIT = "single_hit"
    MULTI_HIT = "multi_hit"


class ExecuteType(Enum):
    YES = "yes"
    MULTI = "multi"
    CUSTOM = "custom"


class BaseType(Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    MONEY = "money"
    PERCENTAGE = "percentage"


class ComparisonOp(Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="


class PatternMatchType(Enum):
    MATCHES = "matches"
    ENDS_WITH = "ends_with"
    STARTS_WITH = "starts_with"
    CONTAINS = "contains"


class LogicalOp(Enum):
    AND = "and"
    OR = "or"
