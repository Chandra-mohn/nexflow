# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Job Correlation Mixin

Generates Flink correlation wiring code (await and hold patterns).
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import (
    to_pascal_case, to_camel_case, duration_to_ms, format_duration, to_snake_case
)


class JobCorrelationMixin:
    """Mixin for generating Flink correlation wiring code."""

    def _wire_correlation(
        self,
        correlation,
        process: ast.ProcessDefinition,
        input_stream: str,
        input_type: str
    ) -> tuple:
        """Wire a correlation block (await or hold)."""
        if isinstance(correlation, ast.AwaitDecl):
            return self._wire_await(correlation, process, input_stream, input_type)
        elif isinstance(correlation, ast.HoldDecl):
            return self._wire_hold(correlation, process, input_stream, input_type)
        else:
            return "        // [UNSUPPORTED] Unknown correlation type", input_stream, input_type

    def _wire_await(
        self,
        await_decl: ast.AwaitDecl,
        process: ast.ProcessDefinition,
        input_stream: str,
        input_type: str
    ) -> tuple:
        """Wire an await (event-driven correlation) pattern."""
        initial_event = await_decl.initial_event
        trigger_event = await_decl.trigger_event
        matching_fields = await_decl.matching_fields
        timeout_ms = duration_to_ms(await_decl.timeout)
        timeout_action = await_decl.timeout_action

        # Build class names
        await_class = f"{to_pascal_case(initial_event)}{to_pascal_case(trigger_event)}AwaitFunction"
        output_stream = "correlatedStream"
        output_type = "CorrelatedEvent"

        initial_stream = input_stream
        trigger_stream = to_camel_case(trigger_event) + "Stream"
        trigger_topic = self._to_snake_case(trigger_event) + "_events"
        trigger_source_var = to_camel_case(trigger_event) + "Source"

        matching_fields_str = ', '.join(f'"{f}"' for f in matching_fields)
        matching_comment = ', '.join(matching_fields)

        code = f'''        // Await: {initial_event} until {trigger_event} arrives matching on [{matching_comment}]
        // Timeout: {format_duration(await_decl.timeout)} -> {timeout_action.action_type.value}

        // Generate second source for trigger events
        KafkaSource<{input_type}> {trigger_source_var} = KafkaSource
            .<{input_type}>builder()
            .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)
            .setTopics("{trigger_topic}")
            .setGroupId("{process.name}-{trigger_event}-consumer")
            .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
            .setValueOnlyDeserializer(new JsonDeserializationSchema<>({input_type}.class))
            .build();

        DataStream<{input_type}> {trigger_stream} = env
            .fromSource(
                {trigger_source_var},
                WatermarkStrategy.<{input_type}>forBoundedOutOfOrderness(Duration.ofMillis(5000)),
                "{trigger_event}"
            );

        OutputTag<{input_type}> timeoutTag = new OutputTag<{input_type}>("timeout") {{}};

        KeyedStream<{input_type}, String> keyed{to_pascal_case(initial_event)} = {initial_stream}
            .keyBy(event -> event.getCorrelationKey(new String[]{{{matching_fields_str}}}));

        KeyedStream<{input_type}, String> keyed{to_pascal_case(trigger_event)} = {trigger_stream}
            .keyBy(event -> event.getCorrelationKey(new String[]{{{matching_fields_str}}}));

        ConnectedStreams<{input_type}, {input_type}> connectedStreams = keyed{to_pascal_case(initial_event)}
            .connect(keyed{to_pascal_case(trigger_event)});

        SingleOutputStreamOperator<{output_type}> {output_stream} = connectedStreams
            .process(new {await_class}({timeout_ms}L, timeoutTag))
            .name("await-{initial_event}-until-{trigger_event}");

        // Timed-out events are available via side output:
        // {output_stream}.getSideOutput(timeoutTag)
'''
        return code, output_stream, output_type

    def _wire_hold(
        self,
        hold_decl: ast.HoldDecl,
        process: ast.ProcessDefinition,
        input_stream: str,
        input_type: str
    ) -> tuple:
        """Wire a hold (buffer-based correlation) pattern."""
        event_name = hold_decl.event
        buffer_name = hold_decl.buffer_name or f"{event_name}_buffer"
        keyed_by = hold_decl.keyed_by
        timeout_ms = duration_to_ms(hold_decl.timeout) if hold_decl.timeout else 60000

        # Build class names
        hold_class = f"{to_pascal_case(event_name)}HoldFunction"
        output_stream = "heldBatchStream"
        output_type = "HeldBatch"

        key_fields_str = ', '.join(f'"{f}"' for f in keyed_by)
        key_comment = ', '.join(keyed_by)

        # Completion condition configuration
        completion_config = ""
        if hold_decl.completion and hold_decl.completion.condition:
            cond = hold_decl.completion.condition
            if cond.condition_type == ast.CompletionConditionType.COUNT:
                completion_config = f", {cond.count_threshold}"
            elif cond.condition_type == ast.CompletionConditionType.MARKER:
                completion_config = ", true"
            elif cond.condition_type == ast.CompletionConditionType.RULE:
                completion_config = f', "{cond.rule_name}"'

        # Timeout action description
        timeout_action_code = ""
        if hold_decl.timeout_action:
            if hold_decl.timeout_action.action_type == ast.TimeoutActionType.EMIT:
                timeout_action_code = f' -> emit to {hold_decl.timeout_action.target}'
            elif hold_decl.timeout_action.action_type == ast.TimeoutActionType.DEAD_LETTER:
                timeout_action_code = f' -> dead_letter {hold_decl.timeout_action.target}'
            elif hold_decl.timeout_action.action_type == ast.TimeoutActionType.SKIP:
                timeout_action_code = ' -> skip'

        timeout_display = format_duration(hold_decl.timeout) if hold_decl.timeout else "60sec"

        code = f'''        // Hold: {event_name} in {buffer_name} keyed by [{key_comment}]
        // Timeout: {timeout_display}{timeout_action_code}
        OutputTag<{input_type}> timeoutHoldTag = new OutputTag<{input_type}>("hold-timeout") {{}};

        DataStream<{output_type}> {output_stream} = {input_stream}
            .keyBy(event -> event.getBufferKey(new String[]{{{key_fields_str}}}))
            .process(new {hold_class}({timeout_ms}L, timeoutHoldTag{completion_config}))
            .name("hold-{buffer_name}");

        // Timed-out incomplete batches are available via side output:
        // {output_stream}.getSideOutput(timeoutHoldTag)
'''
        return code, output_stream, output_type

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase or PascalCase to snake_case."""
        return to_snake_case(name)
