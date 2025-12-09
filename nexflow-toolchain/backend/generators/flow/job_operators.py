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
        else:
            return f"        // [UNSUPPORTED] Operator: {type(op).__name__}", input_stream, input_type

    def _wire_transform(self, transform: ast.TransformDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a transform operator using MapFunction."""
        transform_name = transform.transform_name
        transform_class = to_pascal_case(transform_name) + "Function"
        output_stream = f"transformed{idx}Stream"
        output_type = "Map<String, Object>"

        code = f'''        // Transform: {transform_name}
        DataStream<{output_type}> {output_stream} = {input_stream}
            .map(new {transform_class}())
            .name("transform-{transform_name}");
'''
        return code, output_stream, output_type

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
        rule_name = route.rule_name
        router_class = to_pascal_case(rule_name) + "Router"
        output_stream = f"routed{idx}Stream"
        output_type = "RoutedEvent"

        code = f'''        // Route: {rule_name}
        SingleOutputStreamOperator<{output_type}> {output_stream} = {input_stream}
            .process(new {router_class}())
            .name("route-{rule_name}");

        // Side outputs for each routing decision are available via:
        // {output_stream}.getSideOutput({router_class}.APPROVED_TAG)
        // {output_stream}.getSideOutput({router_class}.FLAGGED_TAG)
        // {output_stream}.getSideOutput({router_class}.BLOCKED_TAG)
'''
        return code, output_stream, output_type

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

        code = f'''{late_tag_decl}        // Window: {window.window_type.value} {format_duration(window.size)}
        WindowedStream<{input_type}, String, TimeWindow> {output_stream} = {input_stream}
            .keyBy(record -> record.getKey())
            .window({window_assigner}){lateness_code}{late_output_code};
'''
        return code, output_stream, input_type

    def _wire_join(self, join: ast.JoinDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a join operator for interval joins."""
        left_stream = to_camel_case(join.left) + "Stream"
        right_stream = to_camel_case(join.right) + "Stream"
        output_stream = f"joined{idx}Stream"
        join_type = join.join_type.value if join.join_type else "inner"
        within_ms = duration_to_ms(join.within)
        join_key_comment = ', '.join(join.on_fields)

        if join_type == "inner":
            code = self._generate_inner_join(join, left_stream, right_stream, output_stream, within_ms, join_key_comment)
        elif join_type == "left":
            code = self._generate_left_join(join, left_stream, right_stream, output_stream, within_ms, join_key_comment)
        elif join_type == "right":
            code = self._generate_right_join(join, left_stream, right_stream, output_stream, within_ms, join_key_comment)
        else:
            code = self._generate_full_join(join, left_stream, right_stream, output_stream, within_ms, join_key_comment)

        return code, output_stream, "JoinedRecord"

    def _generate_inner_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate inner join code."""
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

    def _generate_left_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate left outer join code."""
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

    def _generate_right_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate right outer join code."""
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

    def _generate_full_join(self, join, left_stream, right_stream, output_stream, within_ms, join_key_comment) -> str:
        """Generate full outer join code."""
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
