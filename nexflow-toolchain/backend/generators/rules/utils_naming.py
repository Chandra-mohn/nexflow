# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules Generator Naming Utilities

Naming convention utilities for L4 Rules code generation.

Re-exports from common java_utils plus rules-specific utilities.
"""

from backend.generators.common.java_utils import (
    to_camel_case,
    to_pascal_case,
    to_getter,
    to_setter,
)

# Re-export for backwards compatibility
__all__ = ['to_camel_case', 'to_pascal_case', 'to_getter', 'to_setter',
           'to_record_accessor', 'to_with_method']


def to_record_accessor(field_name: str) -> str:
    """Convert field name to Java Record accessor method call.

    Java Records use fieldName() instead of getFieldName().

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        Record accessor call string (e.g., 'userName()')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "()"
    return f"{camel}()"


def to_with_method(field_name: str) -> str:
    """Convert field name to Java Record withField method name.

    Java Records are immutable. Use withField() to create modified copies.

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        With method name (e.g., 'withUserName')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "with"
    return f"with{camel[0].upper()}{camel[1:]}"
