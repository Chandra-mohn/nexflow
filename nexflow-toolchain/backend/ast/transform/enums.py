# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Transform AST Enumerations

All enum types used in the Transform DSL AST.
"""

from enum import Enum


class CompatibilityMode(Enum):
    BACKWARD = "backward"
    FORWARD = "forward"
    FULL = "full"
    NONE = "none"


class ComposeType(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class SeverityLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LogLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class ErrorActionType(Enum):
    REJECT = "reject"
    SKIP = "skip"
    USE_DEFAULT = "use_default"
    RAISE = "raise"
    LOG_ERROR = "log_error"
    EMIT = "emit"


class QualifierType(Enum):
    NULLABLE = "nullable"
    REQUIRED = "required"
    DEFAULT = "default"


class BaseType(Enum):
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    BYTES = "bytes"
    BIZDATE = "bizdate"  # Business date - validated against calendar


class CalendarFunction(Enum):
    """Built-in calendar functions for business date operations.

    These functions call the Calendar Service API at runtime.
    """
    # Current business date from calendar
    CURRENT_BUSINESS_DATE = "current_business_date"
    # Previous business date (T-1)
    PREVIOUS_BUSINESS_DATE = "previous_business_date"
    # Next business date (T+1)
    NEXT_BUSINESS_DATE = "next_business_date"
    # Add/subtract business days: add_business_days(date, n)
    ADD_BUSINESS_DAYS = "add_business_days"
    # Check if date is a business day: is_business_day(date)
    IS_BUSINESS_DAY = "is_business_day"
    # Check if date is a holiday: is_holiday(date)
    IS_HOLIDAY = "is_holiday"
    # Get business days between two dates: business_days_between(start, end)
    BUSINESS_DAYS_BETWEEN = "business_days_between"


class UnaryOp(Enum):
    NOT = "not"
    MINUS = "-"


class ArithmeticOp(Enum):
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"


class ComparisonOp(Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    NULLSAFE_EQ = "=?"


class LogicalOp(Enum):
    AND = "and"
    OR = "or"
