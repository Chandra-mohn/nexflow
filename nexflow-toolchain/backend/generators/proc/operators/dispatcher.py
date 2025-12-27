# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Job Operators Dispatcher

Main mixin that composes all operator sub-mixins and provides the unified
_wire_operator() dispatcher for routing to appropriate operator handlers.
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case

from .basic_operators import BasicOperatorsMixin
from .window_join_operators import WindowJoinOperatorsMixin
from .advanced_operators import AdvancedOperatorsMixin
from .sql_operators import SqlOperatorsMixin


class JobOperatorsMixin(
    BasicOperatorsMixin,
    WindowJoinOperatorsMixin,
    AdvancedOperatorsMixin,
    SqlOperatorsMixin
):
    """Unified mixin for generating Flink operator wiring code.

    Composes all operator sub-mixins:
    - BasicOperatorsMixin: transform, enrich, route, aggregate
    - WindowJoinOperatorsMixin: window, join (all types), merge
    - AdvancedOperatorsMixin: validate_input, evaluate, lookup, parallel
    - SqlOperatorsMixin: sql_transform (Flink/Spark SQL)
    """

    def _wire_operator(self, op, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a processing operator and return code, new stream name, and output type.

        Routes to appropriate sub-mixin based on operator type.

        Args:
            op: AST operator declaration
            input_stream: Name of the input DataStream variable
            input_type: Java type of elements in input stream
            idx: Unique index for naming generated variables

        Returns:
            Tuple of (generated_code, output_stream_name, output_type)
        """
        # Basic operators (BasicOperatorsMixin)
        if isinstance(op, ast.TransformDecl):
            return self._wire_transform(op, input_stream, input_type, idx)
        elif isinstance(op, ast.EnrichDecl):
            return self._wire_enrich(op, input_stream, input_type, idx)
        elif isinstance(op, ast.RouteDecl):
            return self._wire_route(op, input_stream, input_type, idx)
        elif isinstance(op, ast.AggregateDecl):
            return self._wire_aggregate(op, input_stream, input_type, idx)

        # Window and join operators (WindowJoinOperatorsMixin)
        elif isinstance(op, ast.WindowDecl):
            return self._wire_window(op, input_stream, input_type, idx)
        elif isinstance(op, ast.JoinDecl):
            return self._wire_join(op, input_stream, input_type, idx)
        elif isinstance(op, ast.MergeDecl):
            return self._wire_merge(op, input_stream, input_type, idx)

        # Advanced operators (AdvancedOperatorsMixin)
        elif isinstance(op, ast.EvaluateDecl):
            return self._wire_evaluate(op, input_stream, input_type, idx)
        elif isinstance(op, ast.LookupDecl):
            return self._wire_lookup(op, input_stream, input_type, idx)
        elif isinstance(op, ast.ParallelDecl):
            return self._wire_parallel(op, input_stream, input_type, idx)
        elif isinstance(op, ast.ValidateInputDecl):
            return self._wire_validate_input(op, input_stream, input_type, idx)

        # SQL operators (SqlOperatorsMixin)
        elif isinstance(op, ast.SqlTransformDecl):
            return self._wire_sql_transform(op, input_stream, input_type, idx)

        # Placeholder operators (not yet fully implemented)
        elif isinstance(op, ast.TransitionDecl):
            return f"        // Transition to state: {op.target_state}", input_stream, input_type
        elif isinstance(op, ast.EmitAuditDecl):
            return f"        // Emit audit event: {op.event_name}", input_stream, input_type
        elif isinstance(op, ast.DeduplicateDecl):
            return f"        // Deduplicate by: {op.key_field}", input_stream, input_type
        elif isinstance(op, ast.BranchDecl):
            return f"        // Branch: {op.branch_name}", input_stream, input_type
        elif isinstance(op, ast.CallDecl):
            return f"        // Call: {op.target}", input_stream, input_type
        elif isinstance(op, ast.ScheduleDecl):
            return f"        // Schedule: {op.target}", input_stream, input_type
        elif isinstance(op, ast.SetDecl):
            value_preview = op.value[:30] if op.value else ''
            return f"        // Set: {op.variable} = {value_preview}...", input_stream, input_type
        else:
            return f"        // [UNSUPPORTED] Operator: {type(op).__name__}", input_stream, input_type

    def get_operator_imports(self) -> set:
        """Get all imports needed for operator wiring.

        Aggregates imports from all sub-mixins.
        """
        imports = {
            # Core Flink imports
            "org.apache.flink.streaming.api.datastream.DataStream",
            "org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator",
            "org.apache.flink.streaming.api.datastream.WindowedStream",
            "org.apache.flink.streaming.api.functions.ProcessFunction",
            "org.apache.flink.streaming.api.windowing.windows.TimeWindow",
            "org.apache.flink.util.Collector",
            "org.apache.flink.util.OutputTag",
            # Time imports
            "org.apache.flink.streaming.api.windowing.time.Time",
            "java.util.concurrent.TimeUnit",
            # Join imports
            "org.apache.flink.streaming.api.functions.co.ProcessJoinFunction",
            "org.apache.flink.streaming.api.functions.co.CoGroupFunction",
            "org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows",
            "org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows",
            "org.apache.flink.streaming.api.windowing.assigners.EventTimeSessionWindows",
            # Async imports
            "org.apache.flink.streaming.api.datastream.AsyncDataStream",
            # Collections
            "java.util.List",
            "java.util.ArrayList",
        }
        return imports
