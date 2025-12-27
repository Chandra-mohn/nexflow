# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Common Generator Utilities

Shared utilities for all Nexflow code generators.
All functions consolidated in java_utils.py as single source of truth.
"""

from .java_utils import (
    # Naming utilities
    to_camel_case,
    to_pascal_case,
    to_snake_case,
    to_getter,
    to_setter,
    to_constant,
    get_java_type,
    duration_to_ms,
    format_duration,
    duration_to_time_call,
    # Template utilities
    generate_java_header,
    generate_package_declaration,
    generate_imports,
    generate_class_header,
    generate_method_signature,
    indent,
    # Safe attribute access
    safe_get_attr,
    safe_get_nested,
)

__all__ = [
    # Naming utilities
    'to_camel_case',
    'to_pascal_case',
    'to_snake_case',
    'to_getter',
    'to_setter',
    'to_constant',
    'get_java_type',
    'duration_to_ms',
    'format_duration',
    'duration_to_time_call',
    # Template utilities
    'generate_java_header',
    'generate_package_declaration',
    'generate_imports',
    'generate_class_header',
    'generate_method_signature',
    'indent',
    # Safe attribute access
    'safe_get_attr',
    'safe_get_nested',
]
