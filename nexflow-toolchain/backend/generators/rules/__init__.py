# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Rules Generator Module
# Generates Java rule evaluators from L4 Rules DSL

from .rules_generator import RulesGenerator
from .decision_table_generator import DecisionTableGeneratorMixin
from .procedural_generator import ProceduralGeneratorMixin
from .condition_generator import ConditionGeneratorMixin
from .action_generator import ActionGeneratorMixin
from .lookup_generator import LookupGeneratorMixin
from .emit_generator import EmitGeneratorMixin
from .execute_generator import ExecuteGeneratorMixin
from .pojo_generator import RulesPojoGeneratorMixin
from .services_generator import ServicesGeneratorMixin
from .action_methods_generator import ActionMethodsGeneratorMixin
from .collection_generator import CollectionGeneratorMixin

# Shared utilities
from .utils import (
    to_camel_case,
    to_pascal_case,
    to_getter,
    to_record_accessor,
    to_setter,
    to_with_method,
    get_java_type,
    generate_literal,
    generate_value_expr,
    generate_field_path,
    generate_unsupported_comment,
    generate_null_safe_equals,
    generate_null_safe_comparison,
    generate_null_safe_string_equals,
    get_common_imports,
    get_logging_imports,
    get_collection_imports,
    get_time_imports,
    get_concurrent_imports,
    get_runtime_imports,
    DEFAULT_CACHE_TTL_SECONDS,
)

__all__ = [
    # Main generator
    'RulesGenerator',
    # Mixins
    'DecisionTableGeneratorMixin',
    'ProceduralGeneratorMixin',
    'ConditionGeneratorMixin',
    'ActionGeneratorMixin',
    'LookupGeneratorMixin',
    'EmitGeneratorMixin',
    'ExecuteGeneratorMixin',
    'RulesPojoGeneratorMixin',
    'ServicesGeneratorMixin',
    'ActionMethodsGeneratorMixin',
    'CollectionGeneratorMixin',
    # Utilities
    'to_camel_case',
    'to_pascal_case',
    'to_getter',
    'to_record_accessor',
    'to_setter',
    'to_with_method',
    'get_java_type',
    'generate_literal',
    'generate_value_expr',
    'generate_field_path',
    'generate_unsupported_comment',
    'generate_null_safe_equals',
    'generate_null_safe_comparison',
    'generate_null_safe_string_equals',
    'get_common_imports',
    'get_logging_imports',
    'get_collection_imports',
    'get_time_imports',
    'get_concurrent_imports',
    'get_runtime_imports',
    'DEFAULT_CACHE_TTL_SECONDS',
]
