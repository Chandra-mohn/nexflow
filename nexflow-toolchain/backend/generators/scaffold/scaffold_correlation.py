"""
Scaffold Correlation Mixin

Generates scaffold classes for correlation patterns:
- KeyedCoProcessFunction (await)
- KeyedProcessFunction (hold)
- CorrelatedEvent wrapper
- HeldBatch wrapper
"""

from pathlib import Path

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case


class ScaffoldCorrelationMixin:
    """Mixin for generating correlation pattern scaffolds."""

    def _generate_correlation_scaffold(
        self, correlation, correlation_package: str,
        correlation_path: Path, input_type: str
    ) -> None:
        """Generate correlation scaffolds based on pattern type."""
        if isinstance(correlation, ast.AwaitDecl):
            self._generate_await_scaffold(correlation, correlation_package, correlation_path, input_type)
        elif isinstance(correlation, ast.HoldDecl):
            self._generate_hold_scaffold(correlation, correlation_package, correlation_path, input_type)

    def _generate_await_scaffold(
        self, await_decl: ast.AwaitDecl, correlation_package: str,
        correlation_path: Path, input_type: str
    ) -> None:
        """Generate await function and CorrelatedEvent scaffolds."""
        await_class = f"{to_pascal_case(await_decl.initial_event)}{to_pascal_case(await_decl.trigger_event)}AwaitFunction"
        await_content = self._generate_await_function(await_decl, correlation_package, input_type)
        self.result.add_file(correlation_path / f"{await_class}.java", await_content, "java")

        correlated_content = self._generate_correlated_event(correlation_package, input_type)
        self.result.add_file(correlation_path / "CorrelatedEvent.java", correlated_content, "java")

    def _generate_hold_scaffold(
        self, hold_decl: ast.HoldDecl, correlation_package: str,
        correlation_path: Path, input_type: str
    ) -> None:
        """Generate hold function and HeldBatch scaffolds."""
        hold_class = f"{to_pascal_case(hold_decl.event)}HoldFunction"
        hold_content = self._generate_hold_function(hold_decl, correlation_package, input_type)
        self.result.add_file(correlation_path / f"{hold_class}.java", hold_content, "java")

        held_batch_content = self._generate_held_batch(correlation_package, input_type)
        self.result.add_file(correlation_path / "HeldBatch.java", held_batch_content, "java")

    def _generate_await_function(self, await_decl: ast.AwaitDecl, package: str, input_type: str) -> str:
        """Generate KeyedCoProcessFunction scaffold for await correlation pattern."""
        initial_event = await_decl.initial_event
        trigger_event = await_decl.trigger_event
        class_name = f"{to_pascal_case(initial_event)}{to_pascal_case(trigger_event)}AwaitFunction"
        matching_fields = ', '.join(await_decl.matching_fields)

        return f'''/**
 * {class_name}
 *
 * KeyedCoProcessFunction for awaiting correlation between {initial_event} and {trigger_event}.
 * Matching on fields: [{matching_fields}]
 * Input type: {input_type}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with production implementation with actual correlation logic
 */
package {package};

import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.co.KeyedCoProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import {self.config.package_prefix}.schema.{input_type};

public class {class_name} extends KeyedCoProcessFunction<String, {input_type}, {input_type}, CorrelatedEvent> {{

    private final long timeoutMs;
    private final OutputTag<{input_type}> timeoutTag;
    private transient ValueState<{input_type}> initialEventState;
    private transient ValueState<Long> timerState;

    public {class_name}(long timeoutMs, OutputTag<{input_type}> timeoutTag) {{
        this.timeoutMs = timeoutMs;
        this.timeoutTag = timeoutTag;
    }}

    @Override
    public void open(Configuration parameters) throws Exception {{
        initialEventState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("initial-event", TypeInformation.of({input_type}.class))
        );
        timerState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("timer", Long.class)
        );
    }}

    @Override
    public void processElement1({input_type} initialEvent, Context ctx, Collector<CorrelatedEvent> out) throws Exception {{
        // Store initial event and set timeout timer
        initialEventState.update(initialEvent);
        long timerTimestamp = ctx.timerService().currentProcessingTime() + timeoutMs;
        ctx.timerService().registerProcessingTimeTimer(timerTimestamp);
        timerState.update(timerTimestamp);
    }}

    @Override
    public void processElement2({input_type} triggerEvent, Context ctx, Collector<CorrelatedEvent> out) throws Exception {{
        // Check if initial event exists for this key
        {input_type} initialEvent = initialEventState.value();
        if (initialEvent != null) {{
            // Correlation successful - emit correlated event
            out.collect(new CorrelatedEvent(initialEvent, triggerEvent, ctx.getCurrentKey()));
            // Clear state and cancel timer
            Long timerTimestamp = timerState.value();
            if (timerTimestamp != null) {{
                ctx.timerService().deleteProcessingTimeTimer(timerTimestamp);
            }}
            initialEventState.clear();
            timerState.clear();
        }}
        // If no initial event, trigger is ignored (could log or handle differently)
    }}

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<CorrelatedEvent> out) throws Exception {{
        // Timeout occurred - emit to side output
        {input_type} initialEvent = initialEventState.value();
        if (initialEvent != null) {{
            ctx.output(timeoutTag, initialEvent);
            initialEventState.clear();
            timerState.clear();
        }}
    }}
}}
'''

    def _generate_correlated_event(self, package: str, input_type: str) -> str:
        """Generate CorrelatedEvent wrapper class."""
        return f'''/**
 * CorrelatedEvent
 *
 * Wrapper class containing correlated initial and trigger events.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

public class CorrelatedEvent {{

    private final Object initialEvent;
    private final Object triggerEvent;
    private final String correlationKey;

    public CorrelatedEvent(Object initialEvent, Object triggerEvent, String correlationKey) {{
        this.initialEvent = initialEvent;
        this.triggerEvent = triggerEvent;
        this.correlationKey = correlationKey;
    }}

    public Object getInitialEvent() {{
        return initialEvent;
    }}

    public Object getTriggerEvent() {{
        return triggerEvent;
    }}

    public String getCorrelationKey() {{
        return correlationKey;
    }}

    @SuppressWarnings("unchecked")
    public <T> T getInitialAs(Class<T> clazz) {{
        return (T) initialEvent;
    }}

    @SuppressWarnings("unchecked")
    public <T> T getTriggerAs(Class<T> clazz) {{
        return (T) triggerEvent;
    }}

    public String getKey() {{
        return correlationKey;
    }}

    @Override
    public String toString() {{
        return "CorrelatedEvent{{key='" + correlationKey + "', initial=" + initialEvent + ", trigger=" + triggerEvent + "}}";
    }}
}}
'''

    def _generate_hold_function(self, hold_decl: ast.HoldDecl, package: str, input_type: str) -> str:
        """Generate KeyedProcessFunction scaffold for hold buffer pattern."""
        event_name = hold_decl.event
        class_name = f"{to_pascal_case(event_name)}HoldFunction"
        keyed_by = ', '.join(hold_decl.keyed_by)
        buffer_name = hold_decl.buffer_name or f"{event_name}_buffer"

        # Determine completion signature
        completion_params = ""
        completion_init = ""
        if hold_decl.completion and hold_decl.completion.condition:
            cond = hold_decl.completion.condition
            if cond.condition_type.value == "count":
                completion_params = ", int countThreshold"
                completion_init = "        this.countThreshold = countThreshold;"
            elif cond.condition_type.value == "marker":
                completion_params = ", boolean markerMode"
                completion_init = "        this.markerMode = markerMode;"
            elif cond.condition_type.value == "rule":
                completion_params = ', String ruleName'
                completion_init = "        this.ruleName = ruleName;"

        return f'''/**
 * {class_name}
 *
 * KeyedProcessFunction for buffering {event_name} events keyed by [{keyed_by}].
 * Buffer: {buffer_name}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with production implementation with actual completion logic
 */
package {package};

import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import java.util.ArrayList;
import java.util.List;

public class {class_name} extends KeyedProcessFunction<String, Object, HeldBatch> {{

    private final long timeoutMs;
    private final OutputTag<Object> timeoutTag;
    private transient ListState<Object> bufferState;
    private transient org.apache.flink.api.common.state.ValueState<Long> timerState;
{completion_init}

    public {class_name}(long timeoutMs, OutputTag<Object> timeoutTag{completion_params}) {{
        this.timeoutMs = timeoutMs;
        this.timeoutTag = timeoutTag;
    }}

    @Override
    public void open(Configuration parameters) throws Exception {{
        bufferState = getRuntimeContext().getListState(
            new ListStateDescriptor<>("hold-buffer", Object.class)
        );
        timerState = getRuntimeContext().getState(
            new org.apache.flink.api.common.state.ValueStateDescriptor<>("timer", Long.class)
        );
    }}

    @Override
    public void processElement(Object event, Context ctx, Collector<HeldBatch> out) throws Exception {{
        // Add event to buffer
        bufferState.add(event);

        // Set or extend timeout timer on first event
        Long existingTimer = timerState.value();
        if (existingTimer == null) {{
            long timerTimestamp = ctx.timerService().currentProcessingTime() + timeoutMs;
            ctx.timerService().registerProcessingTimeTimer(timerTimestamp);
            timerState.update(timerTimestamp);
        }}

        // Check completion condition
        // TODO: Implement actual completion logic based on count/marker/rule
        List<Object> bufferedEvents = new ArrayList<>();
        for (Object e : bufferState.get()) {{
            bufferedEvents.add(e);
        }}

        // Scaffold: Complete when we have 10 items (placeholder)
        if (bufferedEvents.size() >= 10) {{
            emitBatch(ctx, out, bufferedEvents);
        }}
    }}

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<HeldBatch> out) throws Exception {{
        // Timeout occurred - emit incomplete batch to side output
        List<Object> bufferedEvents = new ArrayList<>();
        for (Object e : bufferState.get()) {{
            bufferedEvents.add(e);
        }}

        if (!bufferedEvents.isEmpty()) {{
            for (Object event : bufferedEvents) {{
                ctx.output(timeoutTag, event);
            }}
        }}

        bufferState.clear();
        timerState.clear();
    }}

    private void emitBatch(Context ctx, Collector<HeldBatch> out, List<Object> events) throws Exception {{
        out.collect(new HeldBatch(ctx.getCurrentKey(), events));
        // Clear state after emitting
        Long timerTimestamp = timerState.value();
        if (timerTimestamp != null) {{
            ctx.timerService().deleteProcessingTimeTimer(timerTimestamp);
        }}
        bufferState.clear();
        timerState.clear();
    }}
}}
'''

    def _generate_held_batch(self, package: str, input_type: str) -> str:
        """Generate HeldBatch wrapper class."""
        return f'''/**
 * HeldBatch
 *
 * Wrapper class containing a batch of held events that completed together.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

import java.util.Collections;
import java.util.List;

public class HeldBatch {{

    private final String bufferKey;
    private final List<Object> events;

    public HeldBatch(String bufferKey, List<Object> events) {{
        this.bufferKey = bufferKey;
        this.events = Collections.unmodifiableList(events);
    }}

    public String getBufferKey() {{
        return bufferKey;
    }}

    public List<Object> getEvents() {{
        return events;
    }}

    public int size() {{
        return events.size();
    }}

    @SuppressWarnings("unchecked")
    public <T> List<T> getEventsAs(Class<T> clazz) {{
        return (List<T>) events;
    }}

    public String getKey() {{
        return bufferKey;
    }}

    @Override
    public String toString() {{
        return "HeldBatch{{key='" + bufferKey + "', count=" + events.size() + "}}";
    }}
}}
'''
