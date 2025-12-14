# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Collection Expression Generator Mixin

Generates Java code for L4 collection expressions.
RFC: Collection Operations Instead of Loops in L4
"""

import logging
from typing import Set, TYPE_CHECKING

from backend.ast.rules.collections import (
    CollectionExpr,
    CollectionFunctionType,
    CollectionPredicate,
    CollectionPredicateComparison,
    CollectionPredicateIn,
    CollectionPredicateNull,
    CollectionPredicateNot,
    CollectionPredicateCompound,
    LambdaPredicate,
    MultiParamLambdaPredicate,
)
from backend.ast.rules.enums import ComparisonOp, LogicalOp

if TYPE_CHECKING:
    from backend.ast import rules_ast as ast

LOG = logging.getLogger(__name__)


class CollectionGeneratorMixin:
    """
    Mixin for generating Java code for collection expressions.

    Generates calls to NexflowRuntime collection functions:
    - Predicate functions: any(), all(), none()
    - Aggregate functions: sum(), count(), avg(), max(), min()
    - Transform functions: filter(), find(), distinct()

    RFC: Collection Operations Instead of Loops in L4
    """

    def generate_collection_expr(self, expr: CollectionExpr, item_var: str = "item") -> str:
        """Generate Java code for a collection expression.

        Args:
            expr: CollectionExpr AST node
            item_var: Name of the lambda parameter variable (default: "item")

        Returns:
            Java code string for the collection expression
        """
        collection_code = self._generate_value_expr_code(expr.collection)

        if expr.function_type in (CollectionFunctionType.ANY, CollectionFunctionType.ALL,
                                   CollectionFunctionType.NONE):
            return self._generate_predicate_function(expr, collection_code, item_var)
        elif expr.function_type in (CollectionFunctionType.SUM, CollectionFunctionType.COUNT,
                                     CollectionFunctionType.AVG, CollectionFunctionType.MAX,
                                     CollectionFunctionType.MIN):
            return self._generate_aggregate_function(expr, collection_code, item_var)
        elif expr.function_type in (CollectionFunctionType.FILTER, CollectionFunctionType.FIND,
                                     CollectionFunctionType.DISTINCT):
            return self._generate_transform_function(expr, collection_code, item_var)
        else:
            LOG.warning(f"Unknown collection function type: {expr.function_type}")
            return f"/* UNSUPPORTED: {expr.function_type.value} */"

    def _generate_predicate_function(self, expr: CollectionExpr, collection_code: str,
                                      item_var: str) -> str:
        """Generate predicate function call (any, all, none)."""
        func_name = expr.function_type.value  # any, all, none
        predicate_code = self._generate_collection_predicate(expr.predicate, item_var)

        return f"NexflowRuntime.{func_name}({collection_code}, {item_var} -> {predicate_code})"

    def _generate_aggregate_function(self, expr: CollectionExpr, collection_code: str,
                                      item_var: str) -> str:
        """Generate aggregate function call (sum, count, avg, max, min)."""
        func_name = expr.function_type.value  # sum, count, avg, max, min

        if expr.function_type == CollectionFunctionType.COUNT:
            if expr.predicate:
                # count with predicate: count(items, predicate)
                predicate_code = self._generate_collection_predicate(expr.predicate, item_var)
                return f"NexflowRuntime.count({collection_code}, {item_var} -> {predicate_code})"
            else:
                # Simple count: count(items)
                return f"NexflowRuntime.count({collection_code})"
        elif expr.field_extractor:
            # Aggregate with field extractor: sum(items, price) -> sum(items, item -> item.getPrice())
            field_accessor = self._generate_field_accessor(expr.field_extractor, item_var)
            return f"NexflowRuntime.{func_name}({collection_code}, {item_var} -> {field_accessor})"
        else:
            # Aggregate without field (e.g., sum of numeric collection)
            return f"NexflowRuntime.{func_name}({collection_code})"

    def _generate_transform_function(self, expr: CollectionExpr, collection_code: str,
                                      item_var: str) -> str:
        """Generate transform function call (filter, find, distinct)."""
        func_name = expr.function_type.value  # filter, find, distinct

        if func_name == "distinct":
            # Distinct doesn't need a predicate
            return f"NexflowRuntime.distinct({collection_code})"
        elif expr.predicate:
            predicate_code = self._generate_collection_predicate(expr.predicate, item_var)
            return f"NexflowRuntime.{func_name}({collection_code}, {item_var} -> {predicate_code})"
        else:
            LOG.warning(f"Transform function {func_name} requires a predicate")
            return f"/* ERROR: {func_name} requires predicate */"

    def _generate_collection_predicate(self, predicate: CollectionPredicate, item_var: str) -> str:
        """Generate Java code for a collection predicate."""
        if isinstance(predicate, LambdaPredicate):
            # Full lambda: t -> t.amount > 1000
            body_code = self._generate_value_expr_code(predicate.body)
            # Replace the lambda parameter with item_var if they differ
            return body_code

        elif isinstance(predicate, MultiParamLambdaPredicate):
            # Multi-param lambda: (x, y) -> expr
            body_code = self._generate_value_expr_code(predicate.body)
            return body_code

        elif isinstance(predicate, CollectionPredicateComparison):
            # Simple comparison: amount > 1000
            field_accessor = self._generate_field_accessor(predicate.field, item_var)
            op = self._java_comparison_op(predicate.operator)
            value_code = self._generate_value_expr_code(predicate.value)
            return self._generate_comparison_code(field_accessor, op, value_code, predicate.operator)

        elif isinstance(predicate, CollectionPredicateIn):
            # Set membership: type in ("A", "B")
            field_accessor = self._generate_field_accessor(predicate.field, item_var)
            values_code = ", ".join(self._generate_value_expr_code(v) for v in predicate.values)
            if predicate.negated:
                return f"!java.util.Set.of({values_code}).contains({field_accessor})"
            else:
                return f"java.util.Set.of({values_code}).contains({field_accessor})"

        elif isinstance(predicate, CollectionPredicateNull):
            # Null check: field is null
            field_accessor = self._generate_field_accessor(predicate.field, item_var)
            if predicate.is_not_null:
                return f"{field_accessor} != null"
            else:
                return f"{field_accessor} == null"

        elif isinstance(predicate, CollectionPredicateNot):
            # Negation: not predicate
            inner_code = self._generate_collection_predicate(predicate.predicate, item_var)
            return f"!({inner_code})"

        elif isinstance(predicate, CollectionPredicateCompound):
            # Compound: pred1 and pred2, pred1 or pred2
            parts = []
            for i, p in enumerate(predicate.predicates):
                parts.append(self._generate_collection_predicate(p, item_var))

            if not predicate.operators:
                return parts[0]

            result = parts[0]
            for i, op in enumerate(predicate.operators):
                java_op = "&&" if op == LogicalOp.AND else "||"
                result = f"({result}) {java_op} ({parts[i + 1]})"

            return result

        else:
            LOG.warning(f"Unknown predicate type: {type(predicate)}")
            return "true /* UNKNOWN PREDICATE */"

    def _generate_field_accessor(self, field_path, item_var: str) -> str:
        """Generate Java field accessor for a field path.

        Converts field.subfield to item.getField().getSubfield()
        """
        if hasattr(field_path, 'parts'):
            parts = field_path.parts
        else:
            parts = [str(field_path)]

        if not parts:
            return item_var

        # Start with item_var
        accessor = item_var
        for part in parts:
            getter = self._to_getter(part)
            accessor = f"{accessor}.{getter}()"

        return accessor

    def _to_getter(self, field_name: str) -> str:
        """Convert field name to getter method name."""
        if not field_name:
            return "get"
        return f"get{field_name[0].upper()}{field_name[1:]}"

    def _java_comparison_op(self, op: ComparisonOp) -> str:
        """Convert AST comparison operator to Java operator."""
        op_map = {
            ComparisonOp.EQ: "==",
            ComparisonOp.NE: "!=",
            ComparisonOp.LT: "<",
            ComparisonOp.GT: ">",
            ComparisonOp.LE: "<=",
            ComparisonOp.GE: ">=",
        }
        return op_map.get(op, "==")

    def _generate_comparison_code(self, left: str, op: str, right: str, ast_op: ComparisonOp) -> str:
        """Generate comparison code with proper null handling for equals."""
        if ast_op == ComparisonOp.EQ:
            # Use Objects.equals for null-safe equality
            return f"java.util.Objects.equals({left}, {right})"
        elif ast_op == ComparisonOp.NE:
            return f"!java.util.Objects.equals({left}, {right})"
        else:
            # Numeric/comparable comparison
            return f"{left} {op} {right}"

    def _generate_value_expr_code(self, expr) -> str:
        """Generate Java code for a value expression.

        This method should be implemented by the main generator or
        delegate to existing expression generation logic.
        """
        # This is a placeholder - the actual implementation should delegate
        # to the existing expression generation methods in the main generator
        if hasattr(self, 'generate_value_expr'):
            return self.generate_value_expr(expr)

        # Fallback: try to use existing utilities
        from backend.generators.rules.utils import generate_value_expr
        return generate_value_expr(expr)

    def get_collection_imports(self) -> Set[str]:
        """Get required imports for collection expression generation."""
        return {
            # NexflowRuntime is imported via static import
            'java.util.Objects',
            'java.util.Set',
            'java.util.List',
            'java.util.Optional',
            'java.math.BigDecimal',
            'java.util.function.Predicate',
            'java.util.function.Function',
        }

    def has_collection_expressions(self, program: 'ast.Program') -> bool:
        """Check if program uses collection expressions.

        This would require walking the AST to find CollectionExpr nodes.
        For simplicity, we'll return False and let it be manually determined.
        """
        # TODO: Implement AST walking to detect collection expressions
        return False
