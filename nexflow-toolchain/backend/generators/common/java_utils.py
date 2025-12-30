# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Java Utilities Module

Shared utility functions for Java code generation.
Consolidates duplicated naming and conversion utilities.

Single source of truth for:
- Naming conventions (camelCase, PascalCase, snake_case)
- Type mapping (Nexflow types -> Java types)
- Duration/time utilities
- Java code templates (headers, imports, class declarations)
- Safe attribute access patterns
"""

import re
from typing import Optional, Any


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


# =============================================================================
# Java Code Templates
# =============================================================================

def generate_java_header(class_name: str, description: str = "", generator: str = "") -> str:
    """Generate standard Java file header.

    Args:
        class_name: Name of the class
        description: Optional description
        generator: Optional generator name

    Returns:
        Java header comment block
    """
    desc = f" * {description}\n *\n" if description else ""
    gen_line = f" * Generator: {generator}\n" if generator else ""
    return f'''/**
 * {class_name}
 *
{desc} * AUTO-GENERATED by Nexflow Code Generator
 * DO NOT EDIT - Changes will be overwritten
 *
{gen_line} */'''


def generate_package_declaration(package: str) -> str:
    """Generate Java package declaration."""
    return f"package {package};\n"


def generate_imports(imports: list) -> str:
    """Generate sorted, deduplicated import statements.

    Groups imports by: java.*, javax.*, org.*, com.*, others

    Args:
        imports: List of import class names

    Returns:
        Formatted import block
    """
    if not imports:
        return ''

    unique_imports = sorted(set(imports))

    # Group imports
    java_imports = [i for i in unique_imports if i.startswith('java.')]
    javax_imports = [i for i in unique_imports if i.startswith('javax.')]
    org_imports = [i for i in unique_imports if i.startswith('org.')]
    com_imports = [i for i in unique_imports if i.startswith('com.')]
    other_imports = [i for i in unique_imports
                     if not any(i.startswith(p) for p in ['java.', 'javax.', 'org.', 'com.'])]

    sections = []
    for group in [java_imports, javax_imports, org_imports, com_imports, other_imports]:
        if group:
            sections.append('\n'.join(f"import {imp};" for imp in group))

    return '\n\n'.join(sections) + '\n' if sections else ''


def generate_class_header(
    class_name: str,
    extends: str = None,
    implements: list = None,
    modifiers: str = "public"
) -> str:
    """Generate class declaration line.

    Args:
        class_name: Name of the class
        extends: Optional parent class
        implements: Optional list of interfaces
        modifiers: Access modifiers (default: public)

    Returns:
        Class declaration line
    """
    parts = [modifiers, "class", class_name]

    if extends:
        parts.append(f"extends {extends}")

    if implements:
        parts.append("implements " + ", ".join(implements))

    return " ".join(parts) + " {"


def indent(code: str, level: int = 1, indent_str: str = "    ") -> str:
    """Indent a block of code.

    Args:
        code: Code to indent
        level: Number of indent levels
        indent_str: String for one indent level

    Returns:
        Indented code
    """
    prefix = indent_str * level
    return '\n'.join(prefix + line if line.strip() else line
                     for line in code.split('\n'))


def generate_method_signature(
    name: str,
    return_type: str = "void",
    params: list = None,
    modifiers: str = "public",
    throws: list = None
) -> str:
    """Generate method signature.

    Args:
        name: Method name
        return_type: Return type
        params: List of (type, name) tuples
        modifiers: Access modifiers
        throws: List of exception types

    Returns:
        Method signature line
    """
    param_str = ""
    if params:
        param_str = ", ".join(f"{t} {n}" for t, n in params)

    throws_str = ""
    if throws:
        throws_str = " throws " + ", ".join(throws)

    return f"{modifiers} {return_type} {name}({param_str}){throws_str}"


# =============================================================================
# Safe Attribute Access
# =============================================================================

def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get an attribute with default fallback.

    Handles None objects gracefully, avoiding AttributeError.
    Use this when the object itself might be None.

    Args:
        obj: Object to get attribute from (can be None)
        attr: Attribute name
        default: Default value if attribute doesn't exist or is None

    Returns:
        Attribute value or default

    Examples:
        >>> safe_get_attr(None, 'name', 'unknown')
        'unknown'
        >>> safe_get_attr(obj, 'timeout', 30)
        30  # if obj.timeout is None or doesn't exist
    """
    if obj is None:
        return default
    value = getattr(obj, attr, default)
    return value if value is not None else default


def safe_get_nested(obj: Any, *attrs: str, default: Any = None) -> Any:
    """Safely get nested attributes with default fallback.

    Chains through multiple attribute levels safely.

    Args:
        obj: Root object to start from
        *attrs: Sequence of attribute names to traverse
        default: Default value if any attribute in chain is None

    Returns:
        Final attribute value or default

    Examples:
        >>> safe_get_nested(config, 'registry', 'url', default='')
        ''  # if config.registry is None or config.registry.url is None
    """
    current = obj
    for attr in attrs:
        if current is None:
            return default
        current = getattr(current, attr, None)
    return current if current is not None else default
