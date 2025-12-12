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
