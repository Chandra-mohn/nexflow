"""
Job Sinks Mixin

Generates Flink sink wiring code (emit, late data, completion callbacks).
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case


class JobSinksMixin:
    """Mixin for generating Flink sink wiring code."""

    def _generate_sink_with_json(self, emit: ast.EmitDecl, input_stream: str, input_type: str) -> str:
        """Generate Kafka sink with JSON serialization."""
        target = emit.target
        sink_type = input_type
        sink_name = to_camel_case(target) + "Sink"

        return f'''        // Sink: {target}
        KafkaSink<{sink_type}> {sink_name} = KafkaSink
            .<{sink_type}>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setRecordSerializer(
                KafkaRecordSerializationSchema.<{sink_type}>builder()
                    .setTopic("{target}")
                    .setValueSerializationSchema(new JsonSerializationSchema<{sink_type}>())
                    .build()
            )
            .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build();

        {input_stream}.sinkTo({sink_name}).name("sink-{target}");
'''

    def _generate_late_data_sinks(self, process: ast.ProcessDefinition) -> list:
        """Generate late data sinks for window operations."""
        late_data_sinks = []

        for idx, op in enumerate(process.processing):
            if isinstance(op, ast.WindowDecl) and op.options and op.options.late_data:
                late_sink_code = self._generate_late_data_sink(
                    op.options.late_data.target,
                    self._get_input_type_at_op(process, idx),
                    f"windowed{idx}Stream"
                )
                late_data_sinks.append(late_sink_code)

        return late_data_sinks

    def _generate_late_data_sink(self, target: str, input_type: str, windowed_stream: str) -> str:
        """Generate Kafka sink for late data side output."""
        late_tag = to_camel_case(target) + "LateTag"
        sink_name = to_camel_case(target) + "LateSink"

        return f'''        // Late Data Sink: {target}
        KafkaSink<{input_type}> {sink_name} = KafkaSink
            .<{input_type}>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setRecordSerializer(
                KafkaRecordSerializationSchema.<{input_type}>builder()
                    .setTopic("{target}")
                    .setValueSerializationSchema(new JsonSerializationSchema<{input_type}>())
                    .build()
            )
            .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build();

        // To route late data: aggregatedStream.getSideOutput({late_tag}).sinkTo({sink_name});
'''

    def _wire_completion_block(self, completion: ast.CompletionBlock, input_stream: str, input_type: str) -> str:
        """Wire completion event callbacks."""
        lines = []

        if completion.on_commit:
            on_commit = completion.on_commit
            target = on_commit.target
            corr_field = on_commit.correlation.field_path if on_commit.correlation else "correlation_id"
            include_fields = on_commit.include.fields if on_commit.include else []
            include_str = ', '.join(f'"{f}"' for f in include_fields) if include_fields else ""

            lines.append(f'''        // On Commit: emit completion to {target}
        // Correlation field: {corr_field}
        KafkaSink<CompletionEvent> completionSuccessSink = KafkaSink
            .<CompletionEvent>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setRecordSerializer(
                KafkaRecordSerializationSchema.<CompletionEvent>builder()
                    .setTopic("{target}")
                    .setValueSerializationSchema(new JsonSerializationSchema<CompletionEvent>())
                    .build()
            )
            .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build();

        // Create completion event stream from main output
        DataStream<CompletionEvent> completionStream = {input_stream}
            .map(record -> CompletionEvent.success(record, "{corr_field}"{', new String[]{' + include_str + '}' if include_str else ''}))
            .name("completion-event-transform");

        completionStream.sinkTo(completionSuccessSink).name("sink-completion-{target}");
''')

        if completion.on_commit_failure:
            on_failure = completion.on_commit_failure
            target = on_failure.target
            corr_field = on_failure.correlation.field_path if on_failure.correlation else "correlation_id"

            lines.append(f'''        // On Commit Failure: emit completion failure to {target}
        // Correlation field: {corr_field}
        KafkaSink<CompletionEvent> completionFailureSink = KafkaSink
            .<CompletionEvent>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setRecordSerializer(
                KafkaRecordSerializationSchema.<CompletionEvent>builder()
                    .setTopic("{target}")
                    .setValueSerializationSchema(new JsonSerializationSchema<CompletionEvent>())
                    .build()
            )
            .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build();
''')

        return '\n'.join(lines)

    def _get_input_type_at_op(self, process: ast.ProcessDefinition, op_idx: int) -> str:
        """Get the input type at a specific operator index in the pipeline."""
        # Start with initial input type (v0.5.0+: process.receives is direct list)
        if process.receives:
            receive = process.receives[0]
            if receive.schema and receive.schema.schema_name:
                current_type = to_pascal_case(receive.schema.schema_name)
            else:
                current_type = "Object"
        else:
            current_type = "Object"

        # Trace through operators up to op_idx
        if process.processing:
            for idx, op in enumerate(process.processing):
                if idx >= op_idx:
                    break
                if isinstance(op, ast.EnrichDecl):
                    current_type = f"Enriched{current_type}"
                elif isinstance(op, ast.TransformDecl):
                    current_type = "Map<String, Object>"
                elif isinstance(op, ast.RouteDecl):
                    current_type = "RoutedEvent"
                elif isinstance(op, ast.AggregateDecl):
                    current_type = to_pascal_case(op.transform_name) + "Result"

        return current_type
