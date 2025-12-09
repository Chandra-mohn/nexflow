# Common Generator Utilities
# Shared utilities for all Nexflow code generators

from .java_utils import (
    to_camel_case,
    to_pascal_case,
    to_snake_case,
    to_getter,
    to_setter,
    to_constant,
    get_java_type,
    duration_to_ms,
    format_duration,
)

from .java_templates import (
    generate_java_header,
    generate_package_declaration,
    generate_imports,
    generate_class_header,
    indent,
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
    # Template utilities
    'generate_java_header',
    'generate_package_declaration',
    'generate_imports',
    'generate_class_header',
    'indent',
]
