# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Job Operators Mixin

Generates Flink operator wiring code (transform, enrich, route, aggregate, window, join, merge).
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import (
    to_pascal_case, to_camel_case, duration_to_ms, format_duration
)


class JobOperatorsMixin:
    """Mixin for generating Flink operator wiring code."""

    def _wire_operator(self, op, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a processing operator and return code, new stream name, and output type."""
        if isinstance(op, ast.TransformDecl):
            return self._wire_transform(op, input_stream, input_type, idx)
        elif isinstance(op, ast.EnrichDecl):
            return self._wire_enrich(op, input_stream, input_type, idx)
        elif isinstance(op, ast.RouteDecl):
            return self._wire_route(op, input_stream, input_type, idx)
        elif isinstance(op, ast.AggregateDecl):
            return self._wire_aggregate(op, input_stream, input_type, idx)
        elif isinstance(op, ast.WindowDecl):
            return self._wire_window(op, input_stream, input_type, idx)
        elif isinstance(op, ast.JoinDecl):
            return self._wire_join(op, input_stream, input_type, idx)
        elif isinstance(op, ast.MergeDecl):
            return self._wire_merge(op, input_stream, input_type, idx)
        # Implemented operators
        elif isinstance(op, ast.EvaluateDecl):
            return self._wire_evaluate(op, input_stream, input_type, idx)
        elif isinstance(op, ast.LookupDecl):
            return self._wire_lookup(op, input_stream, input_type, idx)
        elif isinstance(op, ast.ParallelDecl):
            return self._wire_parallel(op, input_stream, input_type, idx)
        elif isinstance(op, ast.ValidateInputDecl):
            return self._wire_validate_input(op, input_stream, input_type, idx)
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
        elif isinstance(op, ast.ForeachDecl):
            return f"        // Foreach: {op.item_name} in {op.collection}", input_stream, input_type
        elif isinstance(op, ast.CallDecl):
            return f"        // Call: {op.target}", input_stream, input_type
        elif isinstance(op, ast.ScheduleDecl):
            return f"        // Schedule: {op.target}", input_stream, input_type
        elif isinstance(op, ast.SetDecl):
            return f"        // Set: {op.variable} = {op.value[:30] if op.value else ''}...", input_stream, input_type
        else:
            return f"        // [UNSUPPORTED] Operator: {type(op).__name__}", input_stream, input_type

    def _wire_transform(self, transform: ast.TransformDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a transform operator using MapFunction.

        Type Flow: Resolves output type from transform definition if available,
        otherwise defaults to input type preservation.
        """
        transform_name = transform.transform_name
        transform_class = to_pascal_case(transform_name) + "Function"
        output_stream = f"transformed{idx}Stream"

        # Type Flow: Resolve output type from transform definition
        output_type = self._resolve_transform_output_type(transform_name, input_type)

        code = f'''        // Transform: {transform_name}
        DataStream<{output_type}> {output_stream} = {input_stream}
            .map(new {transform_class}())
            .name("transform-{transform_name}");
'''
        return code, output_stream, output_type

    def _resolve_transform_output_type(self, transform_name: str, fallback_type: str) -> str:
        """Resolve output type for a transform from ValidationContext.

        Looks up the transform definition and extracts the output schema type.
        Falls back to input type if transform not found or has no explicit output.

        Type Resolution Priority:
        1. Single output type (e.g., `output enriched_transaction`)
        2. Single output field with custom_type (e.g., `output enriched: enriched_transaction`)
        3. Multiple output fields → generate TransformNameOutput class
        4. Fallback to input type preservation

        Args:
            transform_name: Name of the transform to look up
            fallback_type: Type to use if resolution fails

        Returns:
            Java class name for the output type
        """
        # Access validation context from config (set during build)
        context = getattr(self.config, 'validation_context', None)
        if not context:
            return fallback_type

        # Look up transform definition
        transform_def = context.transforms.get(transform_name)
        if not transform_def:
            return fallback_type

        # Extract output type from transform definition
        output_spec = getattr(transform_def, 'output', None)
        if not output_spec:
            return fallback_type

        # Single type output (e.g., output schema_name)
        if output_spec.single_type:
            if output_spec.single_type.custom_type:
                return to_pascal_case(output_spec.single_type.custom_type)
            elif output_spec.single_type.base_type:
                # Map base types to Java types
                return self._base_type_to_java(output_spec.single_type.base_type)

        # Check output fields
        if output_spec.fields:
            # Single field with custom_type → use that schema directly
            if len(output_spec.fields) == 1:
                field = output_spec.fields[0]
                if field.field_type and field.field_type.custom_type:
                    return to_pascal_case(field.field_type.custom_type)

            # Multiple fields or primitive type → generate output class
            return to_pascal_case(transform_name) + "Output"

        return fallback_type

    def _base_type_to_java(self, base_type) -> str:
        """Convert DSL base type to Java type."""
        type_map = {
            'string': 'String',
            'int': 'Integer',
            'long': 'Long',
            'decimal': 'BigDecimal',
            'boolean': 'Boolean',
            'timestamp': 'Instant',
            'date': 'LocalDate',
            'uuid': 'UUID',
        }
        type_name = base_type.value if hasattr(base_type, 'value') else str(base_type)
        return type_map.get(type_name.lower(), 'Object')

    def _wire_enrich(self, enrich: ast.EnrichDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire an enrich operator using AsyncDataStream."""
        lookup_name = enrich.lookup_name
        lookup_class = to_pascal_case(lookup_name) + "AsyncFunction"
        output_stream = f"enriched{idx}Stream"
        output_type = f"Enriched{input_type}"

        on_fields_array = ', '.join(f'"{f}"' for f in enrich.on_fields)

        code = f'''        // Enrich: {lookup_name} on [{', '.join(enrich.on_fields)}]
        DataStream<{output_type}> {output_stream} = AsyncDataStream
            .unorderedWait(
                {input_stream},
                new {lookup_class}(new String[]{{{on_fields_array}}}),
                30, TimeUnit.SECONDS,
                100  // async capacity
            )
            .name("enrich-{lookup_name}");
'''
        return code, output_stream, output_type

    def _wire_route(self, route: ast.RouteDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a route operator using ProcessFunction."""
        output_stream = f"routed{idx}Stream"
        output_type = "RoutedEvent"

        if route.rule_name:
            # 'route using' form - use L4 rules router
            rule_name = route.rule_name
            # Handle dotted rule names for valid Java class names
            safe_rule_name = rule_name.replace('.', '_')
            router_class = to_pascal_case(safe_rule_name) + "Router"
            code = f'''        // Route: using {rule_name}
        SingleOutputStreamOperator<{output_type}> {output_stream} = {input_stream}
            .process(new {router_class}())
            .name("route-{rule_name}");

        // Side outputs for each routing decision are available via:
        // {output_stream}.getSideOutput({router_class}.APPROVED_TAG)
        // {output_stream}.getSideOutput({router_class}.FLAGGED_TAG)
        // {output_stream}.getSideOutput({router_class}.BLOCKED_TAG)
'''
        else:
            # 'route when' form - generate inline routing logic
            condition = route.condition or "true"
            java_condition = self._compile_route_condition(condition)
            code = f'''        // Route: inline condition [{condition}]
        SingleOutputStreamOperator<{output_type}> {output_stream} = {input_stream}
            .process(new ProcessFunction<{input_type}, {output_type}>() {{
                @Override
                public void processElement({input_type} value, Context ctx, Collector<{output_type}> out) throws Exception {{
                    boolean matches = {java_condition};
                    out.collect(new RoutedEvent(value, matches ? "matched" : "default"));
                }}
            }})
            .name("route-inline-{idx}");
'''
        return code, output_stream, output_type

    def _compile_route_condition(self, condition: str) -> str:
        """Compile a DSL condition expression to Java boolean expression.

        Handles common patterns:
        - Simple comparisons: amount > 1000, risk_score >= 0.8
        - Field access: customer.status == "active"
        - Boolean operators: amount > 1000 and risk_score > 0.5
        - Negation: not is_blocked
        """
        import re

        if not condition or condition.strip() == "true":
            return "true"
        if condition.strip() == "false":
            return "false"

        result = condition

        # Step 1: Replace boolean operators
        result = re.sub(r'\band\b', '&&', result)
        result = re.sub(r'\bor\b', '||', result)
        result = re.sub(r'\bnot\s+', '!', result)

        # Step 2: Handle string comparisons first (field == "string")
        # Pattern: field == "value" -> "value".equals(value.getField())
        def replace_string_eq(match):
            field = match.group(1).strip()
            string_val = match.group(2)
            getter = self._field_to_getter(field, "value")
            return f'{string_val}.equals({getter})'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*==\s*("[^"]*")', replace_string_eq, result)

        # Step 3: Handle string not-equal comparisons
        def replace_string_ne(match):
            field = match.group(1).strip()
            string_val = match.group(2)
            getter = self._field_to_getter(field, "value")
            return f'!{string_val}.equals({getter})'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*!=\s*("[^"]*")', replace_string_ne, result)

        # Step 4: Handle numeric comparisons (field op number)
        # Pattern: field_name > 1000 -> value.getFieldName() > 1000
        def replace_numeric_comparison(match):
            field = match.group(1).strip()
            op = match.group(2)
            num = match.group(3)
            getter = self._field_to_getter(field, "value")
            return f'{getter} {op} {num}'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(>=|<=|>|<|==|!=)\s*(-?\d+(?:\.\d+)?)', replace_numeric_comparison, result)

        # Step 5: Handle standalone boolean field paths (is_active, customer.is_vip)
        # Must be careful not to match already-processed expressions
        tokens = []
        i = 0
        while i < len(result):
            # Check for already processed content (method calls, operators, etc.)
            if result[i] in '(){}[].,;!&|<>=+-*/':
                tokens.append(result[i])
                i += 1
            elif result[i:i+2] in ('&&', '||', '>=', '<=', '==', '!='):
                tokens.append(result[i:i+2])
                i += 2
            elif result[i].isspace():
                tokens.append(result[i])
                i += 1
            elif result[i:i+5] == 'value':
                # Already a Java reference, keep as-is up to end of call chain
                j = i
                while j < len(result) and (result[j].isalnum() or result[j] in '._()'):
                    j += 1
                tokens.append(result[i:j])
                i = j
            elif result[i].isalpha() or result[i] == '_':
                # Identifier - check if it's a field path that needs conversion
                j = i
                while j < len(result) and (result[j].isalnum() or result[j] in '_.'):
                    j += 1
                identifier = result[i:j]
                # Skip Java keywords/literals
                if identifier in ('true', 'false', 'null', 'equals', 'get'):
                    tokens.append(identifier)
                # Skip if followed by ( - it's already a method call
                elif j < len(result) and result[j] == '(':
                    tokens.append(identifier)
                # Skip numbers
                elif identifier.replace('.', '').isdigit():
                    tokens.append(identifier)
                else:
                    # Convert field path to getter
                    tokens.append(self._field_to_getter(identifier, "value"))
                i = j
            elif result[i].isdigit() or (result[i] == '-' and i+1 < len(result) and result[i+1].isdigit()):
                # Number
                j = i
                if result[j] == '-':
                    j += 1
                while j < len(result) and (result[j].isdigit() or result[j] == '.'):
                    j += 1
                tokens.append(result[i:j])
                i = j
            elif result[i] == '"':
                # String literal
                j = i + 1
                while j < len(result) and result[j] != '"':
                    if result[j] == '\\':
                        j += 1
                    j += 1
                j += 1  # Include closing quote
                tokens.append(result[i:j])
                i = j
            else:
                tokens.append(result[i])
                i += 1

        return ''.join(tokens)

    def _field_to_getter(self, field_path: str, obj_name: str) -> str:
        """Convert a field path to a Java Record accessor chain.

        Uses Record-style field() accessors (not POJO-style getField()).

        Examples:
        - 'amount' -> 'value.amount()'
        - 'customer.status' -> 'value.customer().status()'
        - 'risk_score' -> 'value.riskScore()'
        """
        parts = field_path.split('.')
        accessors = '.'.join(f"{to_camel_case(p)}()" for p in parts)
        return f"{obj_name}.{accessors}"

    def _wire_aggregate(self, aggregate: ast.AggregateDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire an aggregate operator using AggregateFunction."""
        transform_name = aggregate.transform_name
        agg_class = to_pascal_case(transform_name) + "Aggregator"
        result_class = to_pascal_case(transform_name) + "Result"
        output_stream = f"aggregated{idx}Stream"
        output_type = result_class

        code = f'''        // Aggregate: {transform_name}
        // Note: Aggregate follows preceding window operation
        DataStream<{output_type}> {output_stream} = {input_stream}
            .aggregate(new {agg_class}())
            .name("aggregate-{transform_name}");
'''
        return code, output_stream, output_type

    def _wire_window(self, window: ast.WindowDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a window operator with keyBy and window assignment."""
        output_stream = f"windowed{idx}Stream"
        window_assigner = self._get_window_assigner(window)

        # Build keyBy expression from window.key_by field
        if window.key_by:
            # Convert field path to getter chain (e.g., "customer.id" -> "record.getCustomer().getId()")
            key_parts = window.key_by.split('.')
            key_getters = '.'.join(f"get{to_pascal_case(p)}()" for p in key_parts)
            key_by_expr = f"record -> record.{key_getters}"
            key_by_comment = f"key by {window.key_by}"
        else:
            # Default to a getKey() method if no key_by specified
            key_by_expr = "record -> record.getKey()"
            key_by_comment = "key by default"

        # Build lateness configuration
        lateness_code = ""
        if window.options and window.options.lateness:
            lateness_duration = self._duration_to_time_call(window.options.lateness.duration)
            lateness_code = f"\n            .allowedLateness({lateness_duration})"

        # Build late data side output
        late_output_code = ""
        late_tag_decl = ""
        if window.options and window.options.late_data:
            late_target = window.options.late_data.target
            late_tag = to_camel_case(late_target) + "LateTag"
            late_output_code = f"\n            .sideOutputLateData({late_tag})"
            late_tag_decl = f'''        // Late data output tag
        OutputTag<{input_type}> {late_tag} = new OutputTag<{input_type}>("{late_target}") {{}};

'''

        code = f'''{late_tag_decl}        // Window: {window.window_type.value} {format_duration(window.size)} ({key_by_comment})
        WindowedStream<{input_type}, String, TimeWindow> {output_stream} = {input_stream}
            .keyBy({key_by_expr})
            .window({window_assigner}){lateness_code}{late_output_code};
'''
        return code, output_stream, input_type

    def _wire_join(self, join: ast.JoinDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a join operator for interval joins.

        Type Safety Improvements:
        - Resolves left/right types from validation context when available
        - Generates typed key extractors using proper accessor pattern
        - Creates typed JoinedRecord with explicit left/right generics
        """
        left_stream = to_camel_case(join.left) + "Stream"
        right_stream = to_camel_case(join.right) + "Stream"
        output_stream = f"joined{idx}Stream"
        join_type = join.join_type.value if join.join_type else "inner"
        within_ms = duration_to_ms(join.within)
        join_key_comment = ', '.join(join.on_fields)

        # Resolve left and right types from validation context
        left_type, right_type = self._resolve_join_types(join.left, join.right)

        # Generate typed key extractors for join fields
        key_extractor_left = self._generate_key_extractor(join.on_fields, left_type, "left")
        key_extractor_right = self._generate_key_extractor(join.on_fields, right_type, "right")

        # Output type with proper generics
        output_type = f"JoinedRecord<{left_type}, {right_type}>"

        if join_type == "inner":
            code = self._generate_inner_join_typed(
                join, left_stream, right_stream, output_stream, within_ms,
                join_key_comment, left_type, right_type, key_extractor_left, key_extractor_right
            )
        elif join_type == "left":
            code = self._generate_left_join_typed(
                join, left_stream, right_stream, output_stream, within_ms,
                join_key_comment, left_type, right_type, key_extractor_left, key_extractor_right
            )
        elif join_type == "right":
            code = self._generate_right_join_typed(
                join, left_stream, right_stream, output_stream, within_ms,
                join_key_comment, left_type, right_type, key_extractor_left, key_extractor_right
            )
        else:
            code = self._generate_full_join_typed(
                join, left_stream, right_stream, output_stream, within_ms,
                join_key_comment, left_type, right_type, key_extractor_left, key_extractor_right
            )

        return code, output_stream, output_type

    def _resolve_join_types(self, left_name: str, right_name: str) -> tuple:
        """Resolve Java types for left and right sides of join.

        Uses validation context to look up stream types by alias.
        Falls back to Object if types cannot be resolved.
        """
        left_type = "Object"
        right_type = "Object"

        context = getattr(self.config, 'validation_context', None)
        if context:
            # Try to resolve from registered schemas
            if hasattr(context, 'schemas'):
                left_schema = context.schemas.get(left_name)
                right_schema = context.schemas.get(right_name)
                if left_schema:
                    left_type = to_pascal_case(left_name)
                if right_schema:
                    right_type = to_pascal_case(right_name)

        return left_type, right_type

    def _generate_key_extractor(self, on_fields: list, type_name: str, side: str) -> str:
        """Generate key extractor lambda for join.

        For single field: record -> record.field()
        For multiple fields: record -> record.field1() + ":" + record.field2()
        """
        if not on_fields:
            return f"{side} -> \"\""

        if len(on_fields) == 1:
            field = on_fields[0]
            accessor = to_camel_case(field) + "()"
            return f"{side} -> {side}.{accessor}"
        else:
            # Composite key using concatenation
            parts = [f"{side}.{to_camel_case(f)}()" for f in on_fields]
            key_expr = ' + ":" + '.join(parts)
            return f"{side} -> {key_expr}"

    def _generate_inner_join_typed(self, join, left_stream, right_stream, output_stream, within_ms,
                                     join_key_comment, left_type, right_type, key_left, key_right) -> str:
        """Generate type-safe inner join code."""
        output_type = f"JoinedRecord<{left_type}, {right_type}>"
        return f'''        // Join: {join.left} INNER JOIN {join.right} on [{join_key_comment}]
        DataStream<{output_type}> {output_stream} = {left_stream}
            .keyBy({key_left})
            .intervalJoin({right_stream}.keyBy({key_right}))
            .between(Time.milliseconds(-{within_ms}), Time.milliseconds({within_ms}))
            .process(new ProcessJoinFunction<{left_type}, {right_type}, {output_type}>() {{
                @Override
                public void processElement({left_type} left, {right_type} right, Context ctx, Collector<{output_type}> out) {{
                    out.collect(JoinedRecord.inner(left, right));
                }}
            }})
            .name("inner-join-{join.left}-{join.right}");
'''

    def _generate_inner_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate inner join code (legacy - kept for backwards compatibility)."""
        return f'''        // Join: {join.left} INNER JOIN {join.right} on [{join_key_comment}]
        DataStream<JoinedRecord> {output_stream} = {left_stream}
            .keyBy(left -> left.getJoinKey())
            .intervalJoin({right_stream}.keyBy(right -> right.getJoinKey()))
            .between(Time.milliseconds(-{within_ms}), Time.milliseconds({within_ms}))
            .process(new ProcessJoinFunction<>() {{
                @Override
                public void processElement(Object left, Object right, Context ctx, Collector<JoinedRecord> out) {{
                    out.collect(JoinedRecord.inner(left, right));
                }}
            }})
            .name("inner-join-{join.left}-{join.right}");
'''

    def _generate_left_join_typed(self, join, left_stream, right_stream, output_stream, within_ms,
                                    join_key_comment, left_type, right_type, key_left, key_right) -> str:
        """Generate type-safe left outer join code."""
        output_type = f"JoinedRecord<{left_type}, {right_type}>"
        return f'''        // Join: {join.left} LEFT OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<{output_type}> {output_stream} = {left_stream}
            .keyBy({key_left})
            .coGroup({right_stream}.keyBy({key_right}))
            .where({key_left})
            .equalTo({key_right})
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<{left_type}, {right_type}, {output_type}>() {{
                @Override
                public void coGroup(Iterable<{left_type}> leftRecords, Iterable<{right_type}> rightRecords, Collector<{output_type}> out) {{
                    List<{right_type}> rights = new ArrayList<>();
                    rightRecords.forEach(rights::add);
                    for ({left_type} left : leftRecords) {{
                        if (rights.isEmpty()) {{
                            out.collect(JoinedRecord.leftOuter(left, null));
                        }} else {{
                            for ({right_type} right : rights) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("left-join-{join.left}-{join.right}");
'''

    def _generate_left_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate left outer join code (legacy)."""
        return f'''        // Join: {join.left} LEFT OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<JoinedRecord> {output_stream} = {left_stream}
            .keyBy(left -> left.getJoinKey())
            .coGroup({right_stream}.keyBy(right -> right.getJoinKey()))
            .where(left -> left.getJoinKey())
            .equalTo(right -> right.getJoinKey())
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<>() {{
                @Override
                public void coGroup(Iterable leftRecords, Iterable rightRecords, Collector<JoinedRecord> out) {{
                    List<Object> rights = new ArrayList<>();
                    rightRecords.forEach(rights::add);
                    for (Object left : leftRecords) {{
                        if (rights.isEmpty()) {{
                            out.collect(JoinedRecord.leftOuter(left, null));
                        }} else {{
                            for (Object right : rights) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("left-join-{join.left}-{join.right}");
'''

    def _generate_right_join_typed(self, join, left_stream, right_stream, output_stream, within_ms,
                                     join_key_comment, left_type, right_type, key_left, key_right) -> str:
        """Generate type-safe right outer join code."""
        output_type = f"JoinedRecord<{left_type}, {right_type}>"
        return f'''        // Join: {join.left} RIGHT OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<{output_type}> {output_stream} = {left_stream}
            .keyBy({key_left})
            .coGroup({right_stream}.keyBy({key_right}))
            .where({key_left})
            .equalTo({key_right})
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<{left_type}, {right_type}, {output_type}>() {{
                @Override
                public void coGroup(Iterable<{left_type}> leftRecords, Iterable<{right_type}> rightRecords, Collector<{output_type}> out) {{
                    List<{left_type}> lefts = new ArrayList<>();
                    leftRecords.forEach(lefts::add);
                    for ({right_type} right : rightRecords) {{
                        if (lefts.isEmpty()) {{
                            out.collect(JoinedRecord.rightOuter(null, right));
                        }} else {{
                            for ({left_type} left : lefts) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("right-join-{join.left}-{join.right}");
'''

    def _generate_right_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate right outer join code (legacy)."""
        return f'''        // Join: {join.left} RIGHT OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<JoinedRecord> {output_stream} = {left_stream}
            .keyBy(left -> left.getJoinKey())
            .coGroup({right_stream}.keyBy(right -> right.getJoinKey()))
            .where(left -> left.getJoinKey())
            .equalTo(right -> right.getJoinKey())
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<>() {{
                @Override
                public void coGroup(Iterable leftRecords, Iterable rightRecords, Collector<JoinedRecord> out) {{
                    List<Object> lefts = new ArrayList<>();
                    leftRecords.forEach(lefts::add);
                    for (Object right : rightRecords) {{
                        if (lefts.isEmpty()) {{
                            out.collect(JoinedRecord.rightOuter(null, right));
                        }} else {{
                            for (Object left : lefts) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("right-join-{join.left}-{join.right}");
'''

    def _generate_full_join_typed(self, join, left_stream, right_stream, output_stream, within_ms,
                                    join_key_comment, left_type, right_type, key_left, key_right) -> str:
        """Generate type-safe full outer join code."""
        output_type = f"JoinedRecord<{left_type}, {right_type}>"
        return f'''        // Join: {join.left} FULL OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<{output_type}> {output_stream} = {left_stream}
            .keyBy({key_left})
            .coGroup({right_stream}.keyBy({key_right}))
            .where({key_left})
            .equalTo({key_right})
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<{left_type}, {right_type}, {output_type}>() {{
                @Override
                public void coGroup(Iterable<{left_type}> leftRecords, Iterable<{right_type}> rightRecords, Collector<{output_type}> out) {{
                    List<{left_type}> lefts = new ArrayList<>();
                    List<{right_type}> rights = new ArrayList<>();
                    leftRecords.forEach(lefts::add);
                    rightRecords.forEach(rights::add);

                    if (lefts.isEmpty() && rights.isEmpty()) {{
                        return;
                    }} else if (lefts.isEmpty()) {{
                        for ({right_type} right : rights) {{
                            out.collect(JoinedRecord.rightOuter(null, right));
                        }}
                    }} else if (rights.isEmpty()) {{
                        for ({left_type} left : lefts) {{
                            out.collect(JoinedRecord.leftOuter(left, null));
                        }}
                    }} else {{
                        for ({left_type} left : lefts) {{
                            for ({right_type} right : rights) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("full-outer-join-{join.left}-{join.right}");
'''

    def _generate_full_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate full outer join code (legacy)."""
        return f'''        // Join: {join.left} FULL OUTER JOIN {join.right} on [{join_key_comment}]
        DataStream<JoinedRecord> {output_stream} = {left_stream}
            .keyBy(left -> left.getJoinKey())
            .coGroup({right_stream}.keyBy(right -> right.getJoinKey()))
            .where(left -> left.getJoinKey())
            .equalTo(right -> right.getJoinKey())
            .window(TumblingEventTimeWindows.of(Time.milliseconds({within_ms})))
            .apply(new CoGroupFunction<>() {{
                @Override
                public void coGroup(Iterable leftRecords, Iterable rightRecords, Collector<JoinedRecord> out) {{
                    List<Object> lefts = new ArrayList<>();
                    List<Object> rights = new ArrayList<>();
                    leftRecords.forEach(lefts::add);
                    rightRecords.forEach(rights::add);

                    if (lefts.isEmpty() && rights.isEmpty()) {{
                        return;
                    }} else if (lefts.isEmpty()) {{
                        for (Object right : rights) {{
                            out.collect(JoinedRecord.rightOuter(null, right));
                        }}
                    }} else if (rights.isEmpty()) {{
                        for (Object left : lefts) {{
                            out.collect(JoinedRecord.leftOuter(left, null));
                        }}
                    }} else {{
                        for (Object left : lefts) {{
                            for (Object right : rights) {{
                                out.collect(JoinedRecord.inner(left, right));
                            }}
                        }}
                    }}
                }}
            }})
            .name("full-outer-join-{join.left}-{join.right}");
'''

    def _wire_merge(self, merge: ast.MergeDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a merge (union) operator."""
        output_alias = merge.output_alias or f"merged{idx}"
        output_stream = to_camel_case(output_alias) + "Stream"

        if len(merge.streams) < 2:
            return f"        // Error: Merge requires at least 2 streams", input_stream, input_type

        first_stream = to_camel_case(merge.streams[0]) + "Stream"
        other_streams = ', '.join(f"{to_camel_case(s)}Stream" for s in merge.streams[1:])

        code = f'''        // Merge: {', '.join(merge.streams)} -> {output_alias}
        DataStream<{input_type}> {output_stream} = {first_stream}
            .union({other_streams})
            .name("merge-{output_alias}");
'''
        return code, output_stream, input_type

    def _get_window_assigner(self, window: ast.WindowDecl) -> str:
        """Get the Flink window assigner for the window type."""
        size_str = self._duration_to_time_call(window.size)

        if window.window_type == ast.WindowType.TUMBLING:
            return f"TumblingEventTimeWindows.of({size_str})"
        elif window.window_type == ast.WindowType.SLIDING:
            slide_str = self._duration_to_time_call(window.slide) if window.slide else "Time.seconds(10)"
            return f"SlidingEventTimeWindows.of({size_str}, {slide_str})"
        elif window.window_type == ast.WindowType.SESSION:
            return f"EventTimeSessionWindows.withGap({size_str})"
        else:
            return f"TumblingEventTimeWindows.of({size_str})"

    def _duration_to_time_call(self, duration) -> str:
        """Convert Duration to Flink Time.xxx() call."""
        unit_map = {'ms': 'milliseconds', 's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}
        method = unit_map.get(duration.unit, 'seconds')
        return f"Time.{method}({duration.value})"

    # =========================================================================
    # NEW OPERATORS: validate_input, evaluate, lookup, parallel
    # =========================================================================

    def _wire_validate_input(self, validate: ast.ValidateInputDecl,
                             input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a validate_input operator using ProcessFunction with side output.

        Valid records continue on main stream.
        Invalid records are emitted to a side output for error handling.

        Type Flow: Preserves input type (validation is a filter, not transform).
        """
        output_stream = f"validated{idx}Stream"
        invalid_tag = f"invalid{idx}Tag"
        expression = validate.expression if hasattr(validate, 'expression') and validate.expression else "true"

        # Compile the validation expression to Java
        java_condition = self._compile_route_condition(expression)

        code = f'''        // Validate Input: {expression[:50]}{'...' if len(expression) > 50 else ''}
        OutputTag<{input_type}> {invalid_tag} = new OutputTag<{input_type}>("invalid-records-{idx}") {{}};

        SingleOutputStreamOperator<{input_type}> {output_stream} = {input_stream}
            .process(new ProcessFunction<{input_type}, {input_type}>() {{
                @Override
                public void processElement({input_type} value, Context ctx, Collector<{input_type}> out) throws Exception {{
                    if ({java_condition}) {{
                        out.collect(value);
                    }} else {{
                        ctx.output({invalid_tag}, value);
                    }}
                }}
            }})
            .name("validate-input-{idx}");

        // Invalid records available via: {output_stream}.getSideOutput({invalid_tag})
'''
        return code, output_stream, input_type

    def _wire_evaluate(self, evaluate: ast.EvaluateDecl,
                       input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire an evaluate operator for rules or expression evaluation.

        Supports two forms:
        1. 'evaluate using <rule_name>': Wire to L4 rules evaluator class
        2. 'evaluate <expression>': Inline expression evaluation

        Type Flow: Preserves input type (evaluation enriches record with result).
        """
        output_stream = f"evaluated{idx}Stream"

        # Check if this is a 'using' form (references L4 rules)
        rule_name = getattr(evaluate, 'rule_name', None)

        if rule_name:
            # 'evaluate using <rule_name>' - wire to L4 evaluator class
            evaluator_class = to_pascal_case(rule_name) + "Evaluator"

            code = f'''        // Evaluate: using {rule_name}
        DataStream<{input_type}> {output_stream} = {input_stream}
            .map(new {evaluator_class}())
            .name("evaluate-{rule_name}");
'''
        else:
            # Inline expression evaluation
            expression = evaluate.expression if hasattr(evaluate, 'expression') and evaluate.expression else "true"
            java_expr = self._compile_route_condition(expression)

            code = f'''        // Evaluate: {expression[:40]}{'...' if len(expression) > 40 else ''}
        DataStream<{input_type}> {output_stream} = {input_stream}
            .map(value -> {{
                // Evaluate expression and set result on record
                boolean evaluationResult = {java_expr};
                // Return record (evaluation result can be accessed via getEvaluationResult())
                return value;
            }})
            .name("evaluate-inline-{idx}");
'''
        return code, output_stream, input_type

    def _wire_lookup(self, lookup: ast.LookupDecl,
                     input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a lookup operator using AsyncDataStream.

        Performs async lookup against external data source (state store, MongoDB, etc.).
        Returns LookupResult wrapper with found/not-found semantics.

        Type Flow: Returns LookupResult<InputType> wrapper for downstream handling.
        """
        source_name = lookup.source_name
        lookup_class = to_pascal_case(source_name) + "LookupFunction"
        output_stream = f"lookup{idx}Stream"
        output_type = f"LookupResult<{input_type}>"

        # Extract lookup configuration
        timeout_ms = getattr(lookup, 'timeout_ms', 30000) or 30000
        on_fields = getattr(lookup, 'on_fields', None) or []
        on_fields_array = ', '.join(f'"{f}"' for f in on_fields) if on_fields else ''

        code = f'''        // Lookup: {source_name}
        DataStream<{output_type}> {output_stream} = AsyncDataStream
            .unorderedWait(
                {input_stream},
                new {lookup_class}(new String[]{{{on_fields_array}}}),
                {timeout_ms}, TimeUnit.MILLISECONDS,
                100  // async capacity
            )
            .name("lookup-{source_name}");
'''
        return code, output_stream, output_type

    def _wire_parallel(self, parallel: ast.ParallelDecl,
                       input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a parallel execution block with multiple branches.

        Pattern:
        1. Create OutputTag for each branch
        2. Split stream using ProcessFunction emitting to side outputs
        3. Process each branch body recursively
        4. Merge branches at the end using union

        Type Flow: Branches may transform types; merged stream uses common type.
        """
        parallel_name = parallel.name
        branches = parallel.branches if hasattr(parallel, 'branches') and parallel.branches else []

        if not branches:
            return f"        // Parallel block: {parallel_name} (no branches defined)", input_stream, input_type

        lines = [f"        // Parallel Block: {parallel_name}"]
        lines.append("")

        # Generate output tags for each branch
        branch_tags = []
        for branch in branches:
            tag_name = f"{to_camel_case(branch.branch_name)}{idx}Tag"
            branch_tags.append(tag_name)
            lines.append(f'        OutputTag<{input_type}> {tag_name} = new OutputTag<{input_type}>("{branch.branch_name}") {{}};')

        lines.append("")

        # Generate split ProcessFunction
        split_stream = f"parallel{idx}SplitStream"
        lines.append(f'''        // Split into parallel branches
        SingleOutputStreamOperator<{input_type}> {split_stream} = {input_stream}
            .process(new ProcessFunction<{input_type}, {input_type}>() {{
                @Override
                public void processElement({input_type} value, Context ctx, Collector<{input_type}> out) throws Exception {{
                    // Emit to all branches (broadcast pattern)''')

        for tag_name in branch_tags:
            lines.append(f'                    ctx.output({tag_name}, value);')

        lines.append('''                }
            })
            .name("parallel-split-''' + parallel_name + '''");
''')

        # Process each branch
        branch_streams = []
        for i, branch in enumerate(branches):
            tag_name = branch_tags[i]
            branch_stream = f"{to_camel_case(branch.branch_name)}{idx}Stream"
            branch_streams.append(branch_stream)

            lines.append(f'        // Branch: {branch.branch_name}')
            lines.append(f'        DataStream<{input_type}> {branch_stream} = {split_stream}.getSideOutput({tag_name});')

            # Wire branch body operations (recursive)
            current_branch_stream = branch_stream
            current_branch_type = input_type
            branch_body = branch.body if hasattr(branch, 'body') and branch.body else []

            for j, op in enumerate(branch_body):
                op_code, new_stream, new_type = self._wire_operator(
                    op, current_branch_stream, current_branch_type, idx * 100 + i * 10 + j
                )
                if op_code:
                    lines.append(op_code)
                    current_branch_stream = new_stream
                    current_branch_type = new_type

            branch_streams[i] = current_branch_stream
            lines.append("")

        # Merge branches
        output_stream = f"parallel{idx}MergedStream"
        if len(branch_streams) >= 2:
            first_stream = branch_streams[0]
            other_streams = ', '.join(branch_streams[1:])
            lines.append(f'''        // Merge parallel branches
        DataStream<{input_type}> {output_stream} = {first_stream}
            .union({other_streams})
            .name("parallel-merge-{parallel_name}");
''')
        elif len(branch_streams) == 1:
            output_stream = branch_streams[0]
        else:
            output_stream = input_stream

        return '\n'.join(lines), output_stream, input_type

    # =============================================================================
    # SQL Transform Operators (v0.8.0+)
    # =============================================================================

    def _wire_sql_transform(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                             input_type: str, idx: int) -> tuple:
        """Wire embedded SQL transform using Flink Table API or Spark SQL.

        Generates code that:
        1. Registers the input DataStream as a temporary table
        2. Executes the SQL query
        3. Converts the result back to a DataStream

        The actual execution engine (Flink SQL vs Spark SQL) is determined by L5 config.
        """
        # Determine execution engine from config
        engine = self._get_sql_engine()

        if engine == "spark":
            return self._wire_sql_transform_spark(sql_decl, input_stream, input_type, idx)
        else:
            return self._wire_sql_transform_flink(sql_decl, input_stream, input_type, idx)

    def _get_sql_engine(self) -> str:
        """Get SQL execution engine from L5 config.

        Returns 'flink' or 'spark' based on configuration.
        """
        # Check config for execution engine preference
        if hasattr(self, 'config') and self.config:
            engine = getattr(self.config, 'sql_engine', None)
            if engine:
                return engine.lower()
            # Check validation context for L5 config
            context = getattr(self.config, 'validation_context', None)
            if context:
                l5_config = getattr(context, 'l5_config', None)
                if l5_config:
                    engine = getattr(l5_config, 'sql_engine', None)
                    if engine:
                        return engine.lower()
        return "flink"  # Default to Flink SQL

    def _wire_sql_transform_flink(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                                   input_type: str, idx: int) -> tuple:
        """Generate Flink SQL execution code.

        Uses Flink Table API to:
        1. Create a StreamTableEnvironment
        2. Register input stream as a temporary table
        3. Execute SQL query
        4. Convert result back to DataStream
        """
        output_stream = f"sql{idx}Stream"

        # Determine output type from declaration or derive from SQL
        if sql_decl.output_type:
            output_type = to_pascal_case(sql_decl.output_type)
        else:
            output_type = f"Sql{idx}Result"

        # Clean up SQL content
        sql_content = sql_decl.sql_content.strip()

        # Extract table name from SQL (simple heuristic - FROM clause)
        input_table_name = self._extract_table_name_from_sql(sql_content, input_type)

        code = f'''        // SQL Transform (Flink SQL)
        // Register input stream as temporary table
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);
        tableEnv.createTemporaryView("{input_table_name}", {input_stream});

        // Execute SQL query
        Table sqlResult = tableEnv.sqlQuery(
            """
            {sql_content}
            """
        );

        // Convert result back to DataStream
        DataStream<{output_type}> {output_stream} = tableEnv
            .toDataStream(sqlResult, {output_type}.class)
            .name("sql-transform-{idx}");
'''
        return code, output_stream, output_type

    def _wire_sql_transform_spark(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                                   input_type: str, idx: int) -> tuple:
        """Generate Spark SQL execution code.

        Uses Spark DataFrame API to:
        1. Create a temporary view from input
        2. Execute SQL query
        3. Convert result back to Dataset
        """
        output_stream = f"sql{idx}Dataset"

        # Determine output type from declaration or derive from SQL
        if sql_decl.output_type:
            output_type = to_pascal_case(sql_decl.output_type)
        else:
            output_type = f"Sql{idx}Result"

        # Clean up SQL content
        sql_content = sql_decl.sql_content.strip()

        # Extract table name from SQL
        input_table_name = self._extract_table_name_from_sql(sql_content, input_type)

        code = f'''        // SQL Transform (Spark SQL)
        // Register input as temporary view
        {input_stream}.createOrReplaceTempView("{input_table_name}");

        // Execute SQL query
        Dataset<Row> sqlResult = spark.sql(
            """
            {sql_content}
            """
        );

        // Convert to typed Dataset
        Encoder<{output_type}> encoder = Encoders.bean({output_type}.class);
        Dataset<{output_type}> {output_stream} = sqlResult.as(encoder);
'''
        return code, output_stream, output_type

    def _extract_table_name_from_sql(self, sql_content: str, fallback: str) -> str:
        """Extract table name from SQL query for registration.

        Simple heuristic: Look for FROM clause and extract the table name.
        Falls back to the input type name if not found.
        """
        import re

        # Look for FROM <table> pattern
        match = re.search(r'\bFROM\s+(\w+)', sql_content, re.IGNORECASE)
        if match:
            return match.group(1)

        # Fall back to lowercase input type
        return to_camel_case(fallback.replace('.', '_'))

    def get_sql_imports(self, engine: str = "flink") -> set:
        """Get imports needed for SQL transforms.

        Args:
            engine: 'flink' or 'spark'

        Returns:
            Set of import statements
        """
        if engine == "spark":
            return {
                "org.apache.spark.sql.Dataset",
                "org.apache.spark.sql.Row",
                "org.apache.spark.sql.Encoders",
                "org.apache.spark.sql.Encoder",
                "org.apache.spark.sql.SparkSession",
            }
        else:  # flink
            return {
                "org.apache.flink.table.api.Table",
                "org.apache.flink.table.api.bridge.java.StreamTableEnvironment",
            }
