# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules Generator Naming Utilities

Naming convention utilities for L4 Rules code generation.
"""


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
    """Convert field name to getter method call (POJO pattern).

    DEPRECATED: Use to_record_accessor() for Java Records.

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        Getter call string (e.g., 'getUserName()')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "()"
    return f"get{camel[0].upper()}{camel[1:]}()"


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


def to_setter(field_name: str) -> str:
    """Convert field name to setter method name (POJO pattern).

    DEPRECATED: Java Records are immutable. Use withField() pattern instead.

    Args:
        field_name: Field name (e.g., 'user_name')

    Returns:
        Setter method name (e.g., 'setUserName')
    """
    camel = to_camel_case(field_name)
    if not camel:
        return "set"
    return f"set{camel[0].upper()}{camel[1:]}"


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
