"""
Java Utilities Module

Shared utility functions for Java code generation.
Consolidates duplicated naming and conversion utilities.
"""

import re
from typing import Optional


# =============================================================================
# Naming Convention Utilities
# =============================================================================

def to_camel_case(name: str) -> str:
    """Convert snake_case or kebab-case to camelCase.

    Args:
        name: Snake case or kebab-case string (e.g., 'user_name' or 'user-name')

    Returns:
        Camel case string (e.g., 'userName')
    """
    if not name:
        return name
    # Handle both underscores and hyphens
    name = name.replace('-', '_')
    parts = name.split('_')
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


def to_pascal_case(name: str) -> str:
    """Convert snake_case or kebab-case to PascalCase.

    Args:
        name: Snake case or kebab-case string (e.g., 'user_name' or 'user-name')

    Returns:
        Pascal case string (e.g., 'UserName')
    """
    if not name:
        return name
    # Handle both underscores and hyphens
    name = name.replace('-', '_')
    return ''.join(word.capitalize() for word in name.split('_'))


def to_snake_case(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case.

    Args:
        name: Camel or Pascal case string

    Returns:
        Snake case string
    """
    if not name:
        return name
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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


def to_constant(name: str) -> str:
    """Convert to UPPER_SNAKE_CASE for Java constants.

    Args:
        name: Name to convert

    Returns:
        Valid Java constant name
    """
    if not name:
        return "UNKNOWN"
    result = name.upper()
    result = result.replace('-', '_').replace(' ', '_')
    if result and result[0].isdigit():
        result = '_' + result
    return result


# =============================================================================
# Type Mapping
# =============================================================================

def get_java_type(nexflow_type: str, fallback: str = "Object") -> str:
    """Map Nexflow/DSL type to Java type.

    Args:
        nexflow_type: Type name from DSL
        fallback: Default type if unknown

    Returns:
        Java type string
    """
    type_map = {
        # Basic types
        'string': 'String',
        'text': 'String',
        'integer': 'Long',
        'number': 'Long',
        'decimal': 'BigDecimal',
        'money': 'BigDecimal',
        'percentage': 'BigDecimal',
        'boolean': 'Boolean',
        'date': 'LocalDate',
        'timestamp': 'Instant',
        'uuid': 'UUID',
        'bytes': 'byte[]',
    }
    result = type_map.get(nexflow_type.lower())
    if result:
        return result
    # If not found, treat as custom type (PascalCase)
    return to_pascal_case(nexflow_type) if nexflow_type else fallback


# =============================================================================
# Duration/Time Utilities
# =============================================================================

def duration_to_ms(duration) -> int:
    """Convert Duration object to milliseconds.

    Args:
        duration: Object with 'value' and 'unit' attributes

    Returns:
        Duration in milliseconds
    """
    if duration is None:
        return 0

    multipliers = {
        'ms': 1,
        's': 1000,
        'm': 60000,
        'h': 3600000,
        'd': 86400000
    }
    unit = getattr(duration, 'unit', 'ms')
    value = getattr(duration, 'value', 0)
    return value * multipliers.get(unit, 1)


def format_duration(duration) -> str:
    """Format duration for comments/display.

    Args:
        duration: Object with 'value' and 'unit' attributes

    Returns:
        Formatted string (e.g., '5sec', '10min')
    """
    if duration is None:
        return "0ms"

    unit_names = {'ms': 'ms', 's': 'sec', 'm': 'min', 'h': 'hr', 'd': 'day'}
    unit = getattr(duration, 'unit', 'ms')
    value = getattr(duration, 'value', 0)
    return f"{value}{unit_names.get(unit, unit)}"


def duration_to_time_call(duration) -> str:
    """Convert Duration to Flink Time.xxx() call.

    Args:
        duration: Object with 'value' and 'unit' attributes

    Returns:
        Flink Time method call string
    """
    if duration is None:
        return "Time.seconds(0)"

    unit_map = {
        'ms': 'milliseconds',
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days'
    }
    unit = getattr(duration, 'unit', 's')
    value = getattr(duration, 'value', 0)
    method = unit_map.get(unit, 'seconds')
    return f"Time.{method}({value})"
