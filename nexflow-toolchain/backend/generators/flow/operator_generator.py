"""
Operator Generator Mixin

Generates Flink processing operators from L1 enrich, transform, route declarations.
"""

from typing import List, Set, Union

from backend.ast import proc_ast as ast


class OperatorGeneratorMixin:
    """
    Mixin for generating Flink processing operators.

    Generates:
    - Transform operators (MapFunction calls to L3 transforms)
    - Enrich operators (AsyncFunction for lookups)
    - Route operators (ProcessFunction for L4 rules)
    - Aggregate operators (AggregateFunction)
    """

    def generate_operators_code(self, process: ast.ProcessDefinition, input_stream: str) -> str:
        """Generate processing pipeline operators."""
        if not process.processing:
            return f"// No processing steps defined\n{input_stream}"

        lines = []
        current_stream = input_stream

        for idx, op in enumerate(process.processing):
            op_code, new_stream = self._generate_operator(op, current_stream, idx)
            lines.append(op_code)
            current_stream = new_stream

        return '\n'.join(lines), current_stream

    def _generate_operator(self, op: Union[ast.EnrichDecl, ast.TransformDecl, ast.RouteDecl,
                                           ast.AggregateDecl, ast.WindowDecl, ast.JoinDecl,
                                           ast.MergeDecl],
                           input_stream: str, idx: int) -> tuple:
        """Generate code for a single processing operator."""
        if isinstance(op, ast.TransformDecl):
            return self._generate_transform(op, input_stream, idx)
        elif isinstance(op, ast.EnrichDecl):
            return self._generate_enrich(op, input_stream, idx)
        elif isinstance(op, ast.RouteDecl):
            return self._generate_route(op, input_stream, idx)
        elif isinstance(op, ast.AggregateDecl):
            return self._generate_aggregate(op, input_stream, idx)
        elif isinstance(op, ast.MergeDecl):
            return self._generate_merge(op, input_stream, idx)
        else:
            return f"// Unsupported operator: {type(op).__name__}\n", input_stream

    def _generate_transform(self, transform: ast.TransformDecl, input_stream: str, idx: int) -> tuple:
        """Generate transform operator (MapFunction)."""
        transform_name = transform.transform_name
        transform_class = self._to_pascal_case(transform_name) + "Transform"
        output_stream = f"transformed{idx}Stream"

        code = f'''// Transform: {transform_name}
DataStream<TransformResult> {output_stream} = {input_stream}
    .map(new {transform_class}())
    .name("transform-{transform_name}");
'''
        return code, output_stream

    def _generate_enrich(self, enrich: ast.EnrichDecl, input_stream: str, idx: int) -> tuple:
        """Generate enrich operator (AsyncDataStream for lookups)."""
        lookup_name = enrich.lookup_name
        lookup_class = self._to_pascal_case(lookup_name) + "Lookup"
        output_stream = f"enriched{idx}Stream"
        on_fields = ', '.join(f'"{f}"' for f in enrich.on_fields)

        code = f'''// Enrich: {lookup_name} on [{', '.join(enrich.on_fields)}]
SingleOutputStreamOperator<EnrichedRecord> {output_stream} = AsyncDataStream
    .unorderedWait(
        {input_stream},
        new {lookup_class}(new String[]{{{on_fields}}}),
        30, TimeUnit.SECONDS,
        100  // capacity
    )
    .name("enrich-{lookup_name}");
'''
        return code, output_stream

    def _generate_route(self, route: ast.RouteDecl, input_stream: str, idx: int) -> tuple:
        """Generate route operator (ProcessFunction for L4 rules)."""
        rule_name = route.rule_name
        rule_class = self._to_pascal_case(rule_name) + "Rules"
        output_stream = f"routed{idx}Stream"

        code = f'''// Route: {rule_name}
SingleOutputStreamOperator<RoutedRecord> {output_stream} = {input_stream}
    .process(new {rule_class}())
    .name("route-{rule_name}");
'''
        return code, output_stream

    def _generate_aggregate(self, aggregate: ast.AggregateDecl, input_stream: str, idx: int) -> tuple:
        """Generate aggregate operator."""
        transform_name = aggregate.transform_name
        agg_class = self._to_pascal_case(transform_name) + "Aggregator"
        output_stream = f"aggregated{idx}Stream"

        code = f'''// Aggregate: {transform_name}
DataStream<AggregatedResult> {output_stream} = {input_stream}
    .windowAll(TumblingEventTimeWindows.of(Time.minutes(1)))
    .aggregate(new {agg_class}())
    .name("aggregate-{transform_name}");
'''
        return code, output_stream

    def _generate_merge(self, merge: ast.MergeDecl, input_stream: str, idx: int) -> tuple:
        """Generate merge operator (union streams)."""
        streams = merge.streams
        output_alias = merge.output_alias or f"merged{idx}"
        output_stream = f"{self._to_camel_case(output_alias)}Stream"

        if len(streams) == 2:
            code = f'''// Merge: {', '.join(streams)}
DataStream<MergedRecord> {output_stream} = {self._to_camel_case(streams[0])}Stream
    .union({self._to_camel_case(streams[1])}Stream)
    .name("merge-{output_alias}");
'''
        else:
            other_streams = ', '.join(f"{self._to_camel_case(s)}Stream" for s in streams[1:])
            code = f'''// Merge: {', '.join(streams)}
DataStream<MergedRecord> {output_stream} = {self._to_camel_case(streams[0])}Stream
    .union({other_streams})
    .name("merge-{output_alias}");
'''
        return code, output_stream

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_operator_imports(self) -> Set[str]:
        """Get required imports for operator generation."""
        return {
            'org.apache.flink.streaming.api.datastream.DataStream',
            'org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator',
            'org.apache.flink.streaming.api.datastream.AsyncDataStream',
            'org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows',
            'org.apache.flink.streaming.api.windowing.time.Time',
            'java.util.concurrent.TimeUnit',
        }
