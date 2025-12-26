# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Window and Join Operators Mixin

Generates Flink code for: window, join (all types), merge operators.
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import (
    to_pascal_case, to_camel_case, duration_to_ms, format_duration
)


class WindowJoinOperatorsMixin:
    """Mixin for window and join Flink operator wiring."""

    def _wire_window(self, window: ast.WindowDecl, input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a window operator with keyBy and window assignment."""
        output_stream = f"windowed{idx}Stream"
        window_assigner = self._get_window_assigner(window)

        if window.key_by:
            key_parts = window.key_by.split('.')
            key_getters = '.'.join(f"get{to_pascal_case(p)}()" for p in key_parts)
            key_by_expr = f"record -> record.{key_getters}"
            key_by_comment = f"key by {window.key_by}"
        else:
            key_by_expr = "record -> record.getKey()"
            key_by_comment = "key by default"

        lateness_code = ""
        if window.options and window.options.lateness:
            lateness_duration = self._duration_to_time_call(window.options.lateness.duration)
            lateness_code = f"\n            .allowedLateness({lateness_duration})"

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
        """Wire a join operator for interval joins."""
        left_stream = to_camel_case(join.left) + "Stream"
        right_stream = to_camel_case(join.right) + "Stream"
        output_stream = f"joined{idx}Stream"
        join_type = join.join_type.value if join.join_type else "inner"
        within_ms = duration_to_ms(join.within)
        join_key_comment = ', '.join(join.on_fields)

        left_type, right_type = self._resolve_join_types(join.left, join.right)
        key_extractor_left = self._generate_key_extractor(join.on_fields, left_type, "left")
        key_extractor_right = self._generate_key_extractor(join.on_fields, right_type, "right")
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
        """Resolve Java types for left and right sides of join."""
        left_type = "Object"
        right_type = "Object"

        context = getattr(self.config, 'validation_context', None)
        if context and hasattr(context, 'schemas'):
            left_schema = context.schemas.get(left_name)
            right_schema = context.schemas.get(right_name)
            if left_schema:
                left_type = to_pascal_case(left_name)
            if right_schema:
                right_type = to_pascal_case(right_name)

        return left_type, right_type

    def _generate_key_extractor(self, on_fields: list, type_name: str, side: str) -> str:
        """Generate key extractor lambda for join."""
        if not on_fields:
            return f"{side} -> \"\""

        if len(on_fields) == 1:
            field = on_fields[0]
            accessor = to_camel_case(field) + "()"
            return f"{side} -> {side}.{accessor}"
        else:
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
