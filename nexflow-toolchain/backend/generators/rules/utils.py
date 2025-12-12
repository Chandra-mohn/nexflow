"""
Rules Generator Utilities

Shared utility functions for L4 Rules code generation.
Centralizes common operations to eliminate duplication across mixins.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
"""

import logging
from typing import Set, Optional, TYPE_CHECKING

# Re-export from focused modules for backward compatibility
from backend.generators.rules.utils_naming import (
    to_camel_case,
    to_pascal_case,
    to_getter,
    to_record_accessor,
    to_setter,
    to_with_method,
)
from backend.generators.rules.utils_literals import (
    get_java_type,
    generate_literal,
    generate_value_expr,
    generate_field_path,
)
from backend.generators.rules.utils_imports import (
    get_common_imports,
    get_logging_imports,
    get_collection_imports,
    get_time_imports,
    get_concurrent_imports,
    get_runtime_imports,
)

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


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
