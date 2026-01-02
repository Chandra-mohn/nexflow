# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
    BIZDATE = "bizdate"


class MarkerStateType(Enum):
    """Types of marker state checks for conditional rule execution."""

    FIRED = "fired"  # Marker has been triggered
    PENDING = "pending"  # Marker not yet triggered
    BETWEEN = "between"  # Between two markers


class CalendarFunction(Enum):
    """Calendar functions available in rules expressions."""

    CURRENT_BUSINESS_DATE = "current_business_date"
    PREVIOUS_BUSINESS_DATE = "previous_business_date"
    NEXT_BUSINESS_DATE = "next_business_date"
    ADD_BUSINESS_DAYS = "add_business_days"
    IS_BUSINESS_DAY = "is_business_day"
    IS_HOLIDAY = "is_holiday"
    BUSINESS_DAYS_BETWEEN = "business_days_between"


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
