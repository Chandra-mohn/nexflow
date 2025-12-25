# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rules Generator Literal Utilities

Literal and value expression generation for L4 Rules code generation.
"""

import logging
from typing import TYPE_CHECKING

from backend.generators.rules.utils_naming import to_camel_case, to_getter, to_record_accessor

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


def get_java_type(param_type, fallback: str = "Object") -> str:
    """Convert rule type to Java type.

    Args:
        param_type: AST type node or string
        fallback: Default type if unknown

    Returns:
        Java type string
    """
    from backend.ast import rules_ast as ast
    from backend.generators.rules.utils_naming import to_pascal_case

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
        # Handle common string type names
        type_str_map = {
            "text": "String",
            "string": "String",
            "number": "Long",
            "integer": "Long",
            "int": "Long",
            "boolean": "Boolean",
            "bool": "Boolean",
            "date": "LocalDate",
            "timestamp": "Instant",
            "datetime": "Instant",
            "money": "BigDecimal",
            "decimal": "BigDecimal",
            "percentage": "BigDecimal",
        }
        normalized = param_type.lower()
        if normalized in type_str_map:
            return type_str_map[normalized]
        # Unknown string type - use PascalCase as custom type
        return to_pascal_case(param_type)

    LOG.warning(f"Unknown param_type: {type(param_type)}, using fallback: {fallback}")
    return fallback


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
        escaped = literal.value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    if isinstance(literal, ast.IntegerLiteral):
        return f'{literal.value}L'

    if isinstance(literal, ast.DecimalLiteral):
        return f'new BigDecimal("{literal.value}")'

    if isinstance(literal, ast.MoneyLiteral):
        return f'new BigDecimal("{literal.value}")'

    if isinstance(literal, ast.PercentageLiteral):
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
# Built-in Function Mappings
# =============================================================================

# Mapping of DSL built-in functions to Java implementations
BUILTIN_FUNCTION_MAP = {
    # List operations
    'take': lambda args: f'{args[0]}.subList(0, Math.min({args[1]}, {args[0]}.size()))',
    'length': lambda args: f'{args[0]}.size()',
    'append': lambda args: f'NexflowRuntime.append({", ".join(args)})',
    'prepend': lambda args: f'NexflowRuntime.prepend({", ".join(args)})',
    'concat': lambda args: f'NexflowRuntime.concat({", ".join(args)})',
    'first': lambda args: f'{args[0]}.isEmpty() ? null : {args[0]}.get(0)',
    'last': lambda args: f'{args[0]}.isEmpty() ? null : {args[0]}.get({args[0]}.size() - 1)',
    'empty': lambda args: f'{args[0]}.isEmpty()',
    'contains': lambda args: f'{args[0]}.contains({args[1]})',
    'reverse': lambda args: f'NexflowRuntime.reverse({args[0]})',
    'sort': lambda args: f'NexflowRuntime.sort({", ".join(args)})',
    'distinct': lambda args: f'{args[0]}.stream().distinct().toList()',

    # String operations
    'upper': lambda args: f'{args[0]}.toUpperCase()',
    'lower': lambda args: f'{args[0]}.toLowerCase()',
    'trim': lambda args: f'{args[0]}.trim()',
    'substring': lambda args: f'{args[0]}.substring({", ".join(args[1:])})',
    'replace': lambda args: f'{args[0]}.replace({args[1]}, {args[2]})',
    'split': lambda args: f'Arrays.asList({args[0]}.split({args[1]}))',
    'join': lambda args: f'String.join({args[1]}, {args[0]})',
    'starts_with': lambda args: f'{args[0]}.startsWith({args[1]})',
    'ends_with': lambda args: f'{args[0]}.endsWith({args[1]})',
    'matches': lambda args: f'{args[0]}.matches({args[1]})',

    # Math operations
    'abs': lambda args: f'Math.abs({args[0]})',
    'round': lambda args: f'Math.round({args[0]})',
    'floor': lambda args: f'Math.floor({args[0]})',
    'ceil': lambda args: f'Math.ceil({args[0]})',
    'min': lambda args: f'Math.min({", ".join(args)})',
    'max': lambda args: f'Math.max({", ".join(args)})',
    'pow': lambda args: f'Math.pow({args[0]}, {args[1]})',
    'sqrt': lambda args: f'Math.sqrt({args[0]})',

    # Date/time operations
    'now': lambda args: 'Instant.now()',
    'today': lambda args: 'LocalDate.now()',
    'year': lambda args: f'{args[0]}.getYear()',
    'month': lambda args: f'{args[0]}.getMonthValue()',
    'day': lambda args: f'{args[0]}.getDayOfMonth()',
    'days_between': lambda args: f'ChronoUnit.DAYS.between({args[0]}, {args[1]})',
    'add_days': lambda args: f'{args[0]}.plusDays({args[1]})',
    'add_months': lambda args: f'{args[0]}.plusMonths({args[1]})',

    # Type conversions
    'to_string': lambda args: f'String.valueOf({args[0]})',
    'to_number': lambda args: f'Long.parseLong({args[0]})',
    'to_decimal': lambda args: f'new BigDecimal({args[0]})',
    'to_boolean': lambda args: f'Boolean.parseBoolean({args[0]})',

    # Null handling
    'coalesce': lambda args: f'({args[0]} != null ? {args[0]} : {args[1]})',
    'is_null': lambda args: f'({args[0]} == null)',
    'is_not_null': lambda args: f'({args[0]} != null)',
    'if_null': lambda args: f'({args[0]} != null ? {args[0]} : {args[1]})',
}


def _generate_function_call_expr(expr, log_unsupported: bool = True) -> str:
    """Generate Java code for a FunctionCall expression.

    Maps DSL built-in functions to their Java equivalents.

    Args:
        expr: FunctionCall AST node
        log_unsupported: Whether to log warnings for unsupported functions

    Returns:
        Java expression string
    """
    func_name = expr.name.lower() if expr.name else ''
    args = [generate_value_expr(a, log_unsupported) for a in (expr.arguments or [])]

    # Check if this is a built-in function with known mapping
    if func_name in BUILTIN_FUNCTION_MAP:
        try:
            return BUILTIN_FUNCTION_MAP[func_name](args)
        except (IndexError, KeyError) as e:
            LOG.warning(f"Built-in function {func_name} called with wrong number of args: {e}")
            # Fall through to default handling

    # Default: generate as-is (camelCase method call)
    # This handles user-defined functions in actions block
    java_name = to_camel_case(func_name) if func_name else 'unknownFunction'
    return f'{java_name}({", ".join(args)})'


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
        return _generate_function_call_expr(expr, log_unsupported)

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

    if isinstance(expr, ast.BinaryExpr):
        left = generate_value_expr(getattr(expr, 'left', None), log_unsupported)
        right = generate_value_expr(getattr(expr, 'right', None), log_unsupported)
        operator = getattr(expr, 'operator', '+')
        return f'({left} {operator} {right})'

    if isinstance(expr, ast.ParenExpr):
        inner = generate_value_expr(getattr(expr, 'inner', None), log_unsupported)
        return f'({inner})'

    if isinstance(expr, ast.UnaryExpr):
        operand = generate_value_expr(getattr(expr, 'operand', None), log_unsupported)
        return f'-({operand})'

    # Handle CollectionExpr - particularly min/max which are simple Math functions
    if isinstance(expr, ast.CollectionExpr):
        func_type = expr.function_type
        # Handle min/max as Java Math.min/Math.max
        if hasattr(func_type, 'value'):
            func_name = func_type.value
        else:
            func_name = str(func_type)

        if func_name in ('min', 'max'):
            # For min(a, b) style - two arguments
            collection_code = generate_value_expr(expr.collection, log_unsupported)
            if expr.field_extractor:
                field_code = generate_value_expr(expr.field_extractor, log_unsupported)
                return f'Math.{func_name}({collection_code}, {field_code})'
            return f'Math.{func_name}({collection_code})'

        # For other collection functions, generate a placeholder comment
        return f'/* {func_name}(...) - collection operation */'

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
        Java record accessor chain string
    """
    if not fp or not fp.parts:
        LOG.warning("Empty field path provided")
        return ""

    # Use record accessor pattern: fieldName() instead of getFieldName()
    if len(fp.parts) == 1:
        return to_record_accessor(fp.parts[0])

    return ".".join(to_record_accessor(p) for p in fp.parts)
