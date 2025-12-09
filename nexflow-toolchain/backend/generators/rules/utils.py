"""
Rules Generator Utilities

Shared utility functions for L4 Rules code generation.
Centralizes common operations to eliminate duplication across mixins.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
"""

import logging
from typing import Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


# =============================================================================
# Naming Conventions
# =============================================================================

def to_camel_case(name: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        name: Snake case string (e.g., 'user_name')

    Returns:
        Camel case string (e.g., 'userName')
    """
    if not name:
        return name
    parts = name.split('_')
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase.

    Args:
        name: Snake case string (e.g., 'user_name')

    Returns:
        Pascal case string (e.g., 'UserName')
    """
    if not name:
        return name
    return ''.join(word.capitalize() for word in name.split('_'))


def to_getter(field_name: str) -> str:
    """Convert field name to getter method call.

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        Getter call string (e.g., 'getUserName()')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "()"
    return f"get{camel[0].upper()}{camel[1:]}()"


def to_setter(field_name: str) -> str:
    """Convert field name to setter method name.

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        Setter method name (e.g., 'setUserName')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "set"
    return f"set{camel[0].upper()}{camel[1:]}"


# =============================================================================
# Type Mapping
# =============================================================================

def get_java_type(param_type, fallback: str = "Object") -> str:
    """Convert rule type to Java type.

    Args:
        param_type: AST type node or string
        fallback: Default type if unknown

    Returns:
        Java type string
    """
    from backend.ast import rules_ast as ast

    if isinstance(param_type, ast.BaseType):
        type_map = {
            ast.BaseType.TEXT: "String",
            ast.BaseType.NUMBER: "Long",
            ast.BaseType.BOOLEAN: "Boolean",
            ast.BaseType.DATE: "LocalDate",
            ast.BaseType.TIMESTAMP: "Instant",
            ast.BaseType.MONEY: "BigDecimal",
            ast.BaseType.PERCENTAGE: "BigDecimal",
        }
        result = type_map.get(param_type)
        if result:
            return result
        LOG.warning(f"Unknown BaseType: {param_type}, using fallback: {fallback}")
        return fallback

    if isinstance(param_type, str):
        return to_pascal_case(param_type)

    LOG.warning(f"Unknown param_type: {type(param_type)}, using fallback: {fallback}")
    return fallback


# =============================================================================
# Literal Generation
# =============================================================================

def generate_literal(literal, log_unsupported: bool = True) -> str:
    """Generate Java literal from AST literal.

    Args:
        literal: AST literal node
        log_unsupported: Whether to log warnings for unsupported types

    Returns:
        Java literal string
    """
    from backend.ast import rules_ast as ast

    if literal is None:
        return 'null'

    if isinstance(literal, ast.StringLiteral):
        # Escape special characters
        escaped = literal.value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    if isinstance(literal, ast.IntegerLiteral):
        return f'{literal.value}L'

    if isinstance(literal, ast.DecimalLiteral):
        return f'new BigDecimal("{literal.value}")'

    if isinstance(literal, ast.MoneyLiteral):
        return f'new BigDecimal("{literal.value}")'

    if isinstance(literal, ast.PercentageLiteral):
        # Convert percentage to decimal (e.g., 15% -> 0.15)
        decimal_value = literal.value / 100.0
        return f'new BigDecimal("{decimal_value}")'

    if isinstance(literal, ast.BooleanLiteral):
        return 'true' if literal.value else 'false'

    if isinstance(literal, ast.NullLiteral):
        return 'null'

    if isinstance(literal, ast.ListLiteral):
        elements = ", ".join(generate_literal(e) for e in literal.values)
        return f'Arrays.asList({elements})'

    if log_unsupported:
        LOG.warning(f"Unsupported literal type: {type(literal).__name__}")
    return 'null'


# =============================================================================
# Value Expression Generation
# =============================================================================

def generate_value_expr(expr, log_unsupported: bool = True) -> str:
    """Generate Java code for a value expression.

    Args:
        expr: AST expression node
        log_unsupported: Whether to log warnings for unsupported types

    Returns:
        Java expression string
    """
    from backend.ast import rules_ast as ast

    if expr is None:
        return 'null'

    if isinstance(expr, ast.FieldPath):
        return generate_field_path(expr)

    if isinstance(expr, ast.FunctionCall):
        args = ", ".join(generate_value_expr(a) for a in (expr.arguments or []))
        return f'{to_camel_case(expr.name)}({args})'

    if isinstance(expr, ast.StringLiteral):
        escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    if isinstance(expr, ast.IntegerLiteral):
        return f'{expr.value}L'

    if isinstance(expr, ast.DecimalLiteral):
        return f'new BigDecimal("{expr.value}")'

    if isinstance(expr, ast.MoneyLiteral):
        return f'new BigDecimal("{expr.value}")'

    if isinstance(expr, ast.BooleanLiteral):
        return 'true' if expr.value else 'false'

    if isinstance(expr, ast.NullLiteral):
        return 'null'

    if isinstance(expr, ast.ListLiteral):
        elements = ", ".join(generate_value_expr(e) for e in (expr.values or []))
        return f'Arrays.asList({elements})'

    # Fallback: try to use as literal
    if hasattr(expr, 'value'):
        return generate_literal(expr, log_unsupported)

    if log_unsupported:
        LOG.warning(f"Unsupported value expression type: {type(expr).__name__}")
    return str(expr)


def generate_field_path(fp) -> str:
    """Generate Java getter chain for field path.

    Args:
        fp: FieldPath AST node

    Returns:
        Java getter chain string
    """
    if not fp or not fp.parts:
        LOG.warning("Empty field path provided")
        return ""

    if len(fp.parts) == 1:
        return to_getter(fp.parts[0])

    return ".".join(to_getter(p) for p in fp.parts)


# =============================================================================
# Import Sets
# =============================================================================

def get_common_imports() -> Set[str]:
    """Get commonly needed imports for rule generation."""
    return {
        'java.util.Arrays',
        'java.math.BigDecimal',
    }


def get_logging_imports() -> Set[str]:
    """Get imports for logging."""
    return {
        'org.slf4j.Logger',
        'org.slf4j.LoggerFactory',
    }


def get_collection_imports() -> Set[str]:
    """Get imports for collections."""
    return {
        'java.util.List',
        'java.util.ArrayList',
        'java.util.Map',
        'java.util.HashMap',
        'java.util.Set',
        'java.util.HashSet',
        'java.util.Optional',
    }


def get_time_imports() -> Set[str]:
    """Get imports for date/time types."""
    return {
        'java.time.LocalDate',
        'java.time.Instant',
    }


def get_concurrent_imports() -> Set[str]:
    """Get imports for concurrent utilities."""
    return {
        'java.util.concurrent.CompletableFuture',
        'java.util.concurrent.ExecutorService',
        'java.util.concurrent.Executors',
    }


# =============================================================================
# Code Generation Helpers
# =============================================================================

def generate_unsupported_comment(element_type: str, context: str = "") -> str:
    """Generate a comment for unsupported elements with logging.

    Args:
        element_type: Type of unsupported element
        context: Additional context

    Returns:
        Java comment string
    """
    ctx_str = f" in {context}" if context else ""
    LOG.warning(f"Unsupported {element_type}{ctx_str}")
    return f"/* UNSUPPORTED: {element_type}{ctx_str} */"


def safe_get_attr(obj, attr: str, default=None):
    """Safely get an attribute with default fallback.

    Args:
        obj: Object to get attribute from
        attr: Attribute name
        default: Default value if attribute doesn't exist or is None

    Returns:
        Attribute value or default
    """
    if obj is None:
        return default
    value = getattr(obj, attr, default)
    return value if value is not None else default


# =============================================================================
# Null-Safe Comparison Helpers
# =============================================================================

def generate_null_safe_equals(left_expr: str, right_expr: str) -> str:
    """Generate null-safe equality comparison.

    Args:
        left_expr: Left side Java expression
        right_expr: Right side Java expression

    Returns:
        Null-safe equals check using Objects.equals()
    """
    return f'java.util.Objects.equals({left_expr}, {right_expr})'


def generate_null_safe_comparison(left_expr: str, operator: str, right_expr: str,
                                   is_primitive: bool = False) -> str:
    """Generate null-safe comparison expression.

    Args:
        left_expr: Left side Java expression
        operator: Comparison operator (==, !=, <, >, <=, >=)
        right_expr: Right side Java expression
        is_primitive: Whether comparing primitive types (no null check needed)

    Returns:
        Null-safe comparison expression
    """
    if is_primitive:
        return f'({left_expr} {operator} {right_expr})'

    # For object types, add null guard
    if operator in ('==', '!='):
        if operator == '==':
            return f'java.util.Objects.equals({left_expr}, {right_expr})'
        return f'!java.util.Objects.equals({left_expr}, {right_expr})'

    # For ordering comparisons, guard against null
    return f'({left_expr} != null && {left_expr}.compareTo({right_expr}) {operator} 0)'


def generate_null_safe_string_equals(left_expr: str, string_value: str) -> str:
    """Generate null-safe string equality (constant.equals(var) pattern).

    Args:
        left_expr: Variable expression to compare
        string_value: String constant value

    Returns:
        Null-safe equals using constant.equals(variable) pattern
    """
    escaped = string_value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}".equals({left_expr})'


# =============================================================================
# Constants
# =============================================================================

# Default cache TTL for lookups (5 minutes)
DEFAULT_CACHE_TTL_SECONDS = 300

# Default thread pool size multiplier
DEFAULT_THREAD_POOL_MULTIPLIER = 1  # times available processors
