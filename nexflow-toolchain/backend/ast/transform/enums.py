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
