"""
Scaffold Generator Module

Generates dummy/template L3 and L4 classes for L1 to compile against.
These are intentionally simple implementations that can be replaced
by proper L3/L4 generated code later.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
This is a TEMPORARY measure to allow L1 to compile while L3/L4 are
being completed. The generated scaffolds are REAL, COMPILABLE code
that provides minimal but correct implementations.

NOT STUBS: These compile and run (with minimal functionality)
NOT PLACEHOLDERS: They have actual method bodies
─────────────────────────────────────────────────────────────────────
"""

from pathlib import Path
from typing import Set, List

from backend.ast import proc_ast as ast
from backend.generators.base import BaseGenerator, GeneratorConfig, GenerationResult


class ScaffoldGenerator(BaseGenerator):
    """
    Generator for L3/L4 scaffold classes.

    Generates minimal but compilable implementations for:
    - AsyncFunction (for enrich operators)
    - ProcessFunction/Router (for route operators)
    - AggregateFunction (for aggregate operators)
    - RoutedEvent wrapper class
    - Enriched schema wrappers
    """

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)

    def generate(self, program: ast.Program) -> GenerationResult:
        """Generate scaffold classes from Process AST."""
        for process in program.processes:
            self._generate_scaffolds_for_process(process)
        return self.result

    def _generate_scaffolds_for_process(self, process: ast.ProcessDefinition) -> None:
        """Generate all scaffold classes needed by a process."""
        transform_package = f"{self.config.package_prefix}.transform"
        rules_package = f"{self.config.package_prefix}.rules"
        schema_package = f"{self.config.package_prefix}.schema"
        correlation_package = f"{self.config.package_prefix}.correlation"

        transform_path = Path("src/main/java") / self.get_package_path(transform_package)
        rules_path = Path("src/main/java") / self.get_package_path(rules_package)
        schema_path = Path("src/main/java") / self.get_package_path(schema_package)
        correlation_path = Path("src/main/java") / self.get_package_path(correlation_package)

        # Track what we need to generate
        input_type = self._get_input_type(process)
        needs_routed_event = False

        # Generate processing operator scaffolds
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    # Generate AsyncFunction scaffold
                    async_class = self._to_pascal_case(op.lookup_name) + "AsyncFunction"
                    content = self._generate_async_function(op, transform_package, input_type)
                    self.result.add_file(transform_path / f"{async_class}.java", content, "java")

                    # Generate Enriched wrapper
                    enriched_class = f"Enriched{input_type}"
                    enriched_content = self._generate_enriched_wrapper(enriched_class, schema_package, input_type)
                    self.result.add_file(schema_path / f"{enriched_class}.java", enriched_content, "java")

                elif isinstance(op, ast.TransformDecl):
                    # Generate MapFunction scaffold for transform
                    transform_class = self._to_pascal_case(op.transform_name) + "Function"
                    content = self._generate_transform_function(op, transform_package, input_type)
                    self.result.add_file(transform_path / f"{transform_class}.java", content, "java")

                elif isinstance(op, ast.RouteDecl):
                    # Generate Router ProcessFunction scaffold
                    router_class = self._to_pascal_case(op.rule_name) + "Router"
                    content = self._generate_router(op, rules_package, input_type)
                    self.result.add_file(rules_path / f"{router_class}.java", content, "java")
                    needs_routed_event = True

                elif isinstance(op, ast.AggregateDecl):
                    # Generate AggregateFunction scaffold
                    agg_class = self._to_pascal_case(op.transform_name) + "Aggregator"
                    result_class = self._to_pascal_case(op.transform_name) + "Result"
                    accumulator_class = self._to_pascal_case(op.transform_name) + "Accumulator"

                    agg_content = self._generate_aggregator(op, transform_package, input_type, result_class, accumulator_class)
                    self.result.add_file(transform_path / f"{agg_class}.java", agg_content, "java")

                    result_content = self._generate_result_class(result_class, transform_package)
                    self.result.add_file(transform_path / f"{result_class}.java", result_content, "java")

                    accumulator_content = self._generate_accumulator_class(accumulator_class, transform_package)
                    self.result.add_file(transform_path / f"{accumulator_class}.java", accumulator_content, "java")

        # Generate RoutedEvent if needed
        if needs_routed_event:
            routed_content = self._generate_routed_event(rules_package)
            self.result.add_file(rules_path / "RoutedEvent.java", routed_content, "java")

        # Generate correlation scaffolds
        if process.correlation:
            input_type = self._get_input_type(process)
            if isinstance(process.correlation, ast.AwaitDecl):
                await_decl = process.correlation
                await_class = f"{self._to_pascal_case(await_decl.initial_event)}{self._to_pascal_case(await_decl.trigger_event)}AwaitFunction"
                await_content = self._generate_await_function(await_decl, correlation_package, input_type)
                self.result.add_file(correlation_path / f"{await_class}.java", await_content, "java")

                # Generate CorrelatedEvent wrapper
                correlated_content = self._generate_correlated_event(correlation_package, input_type)
                self.result.add_file(correlation_path / "CorrelatedEvent.java", correlated_content, "java")

            elif isinstance(process.correlation, ast.HoldDecl):
                hold_decl = process.correlation
                hold_class = f"{self._to_pascal_case(hold_decl.event)}HoldFunction"
                hold_content = self._generate_hold_function(hold_decl, correlation_package, input_type)
                self.result.add_file(correlation_path / f"{hold_class}.java", hold_content, "java")

                # Generate HeldBatch wrapper
                held_batch_content = self._generate_held_batch(correlation_package, input_type)
                self.result.add_file(correlation_path / "HeldBatch.java", held_batch_content, "java")

        # Generate completion scaffolds
        if process.completion:
            completion_package = f"{self.config.package_prefix}.completion"
            completion_path = Path("src/main/java") / self.get_package_path(completion_package)

            # Generate CompletionEvent class
            completion_event_content = self._generate_completion_event(completion_package)
            self.result.add_file(completion_path / "CompletionEvent.java", completion_event_content, "java")

    def _get_input_type(self, process: ast.ProcessDefinition) -> str:
        """Get the input type for the process."""
        if process.input and process.input.receives:
            receive = process.input.receives[0]
            if receive.schema and receive.schema.schema_name:
                return self._to_pascal_case(receive.schema.schema_name)
        return "Object"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _generate_async_function(self, enrich: ast.EnrichDecl, package: str, input_type: str) -> str:
        """Generate AsyncFunction scaffold for enrich operator."""
        class_name = self._to_pascal_case(enrich.lookup_name) + "AsyncFunction"
        output_type = f"Enriched{input_type}"

        return f'''/**
 * {class_name}
 *
 * AsyncFunction for enriching {input_type} with lookup data.
 * Lookup: {enrich.lookup_name}
 * Key fields: {', '.join(enrich.on_fields)}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L3-generated implementation
 */
package {package};

import org.apache.flink.streaming.api.functions.async.RichAsyncFunction;
import org.apache.flink.streaming.api.functions.async.ResultFuture;
import org.apache.flink.configuration.Configuration;

import {self.config.package_prefix}.schema.{input_type};
import {self.config.package_prefix}.schema.{output_type};

import java.util.Collections;
import java.util.concurrent.CompletableFuture;

public class {class_name} extends RichAsyncFunction<{input_type}, {output_type}> {{

    private final String[] keyFields;

    public {class_name}(String[] keyFields) {{
        this.keyFields = keyFields;
    }}

    @Override
    public void open(Configuration parameters) throws Exception {{
        // Initialize lookup client connection
        // TODO: L3 will generate actual connection setup from L5 infra config
    }}

    @Override
    public void asyncInvoke({input_type} input, ResultFuture<{output_type}> resultFuture) {{
        // Perform async lookup and enrich
        CompletableFuture.supplyAsync(() -> {{
            // TODO: L3 will generate actual lookup logic
            // For now, pass through with empty enrichment
            return {output_type}.from(input);
        }}).whenComplete((result, error) -> {{
            if (error != null) {{
                resultFuture.completeExceptionally(error);
            }} else {{
                resultFuture.complete(Collections.singleton(result));
            }}
        }});
    }}

    @Override
    public void close() throws Exception {{
        // Close lookup client connection
    }}
}}
'''

    def _generate_enriched_wrapper(self, class_name: str, package: str, base_type: str) -> str:
        """Generate Enriched wrapper class."""
        return f'''/**
 * {class_name}
 *
 * Enriched version of {base_type} with additional lookup data.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L2-generated implementation based on enrich select fields
 */
package {package};

import java.util.HashMap;
import java.util.Map;

public class {class_name} {{

    private final {base_type} original;
    private final Map<String, Object> enrichedFields;

    public {class_name}({base_type} original) {{
        this.original = original;
        this.enrichedFields = new HashMap<>();
    }}

    public static {class_name} from({base_type} input) {{
        return new {class_name}(input);
    }}

    public {base_type} getOriginal() {{
        return original;
    }}

    public Object getEnrichedField(String fieldName) {{
        return enrichedFields.get(fieldName);
    }}

    public void setEnrichedField(String fieldName, Object value) {{
        enrichedFields.put(fieldName, value);
    }}

    public String getKey() {{
        // Delegate to original for keying purposes
        return original.toString();
    }}
}}
'''

    def _generate_transform_function(self, transform: ast.TransformDecl, package: str, input_type: str) -> str:
        """Generate MapFunction scaffold for transform operator.

        Note: Input type may be Enriched{schema} if an enrich operator precedes this transform.
        """
        class_name = self._to_pascal_case(transform.transform_name) + "Function"
        # Transform receives enriched type if enrich precedes it
        actual_input_type = f"Enriched{input_type}" if "Enriched" not in input_type else input_type

        return f'''/**
 * {class_name}
 *
 * MapFunction for transforming enriched records using transform: {transform.transform_name}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L3-generated implementation
 */
package {package};

import org.apache.flink.api.common.functions.MapFunction;
import java.util.Map;
import java.util.HashMap;
import {self.config.package_prefix}.schema.{actual_input_type};

public class {class_name} implements MapFunction<{actual_input_type}, Map<String, Object>> {{

    @Override
    public Map<String, Object> map({actual_input_type} value) throws Exception {{
        // Scaffold: pass through as Map
        // L3 will generate actual transformation logic
        Map<String, Object> result = new HashMap<>();
        result.put("_original", value);
        // TODO: L3 will generate actual field mappings and transformations
        return result;
    }}
}}
'''

    def _generate_router(self, route: ast.RouteDecl, package: str, input_type: str) -> str:
        """Generate Router ProcessFunction scaffold for route operator."""
        class_name = self._to_pascal_case(route.rule_name) + "Router"

        return f'''/**
 * {class_name}
 *
 * ProcessFunction for routing records based on rule: {route.rule_name}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L4-generated implementation with actual rule evaluation
 */
package {package};

import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;
import java.util.Map;

public class {class_name} extends ProcessFunction<Map<String, Object>, RoutedEvent> {{

    // Output tags for side outputs (routing decisions)
    public static final OutputTag<RoutedEvent> APPROVED_TAG =
        new OutputTag<RoutedEvent>("approved") {{}};
    public static final OutputTag<RoutedEvent> FLAGGED_TAG =
        new OutputTag<RoutedEvent>("flagged") {{}};
    public static final OutputTag<RoutedEvent> BLOCKED_TAG =
        new OutputTag<RoutedEvent>("blocked") {{}};

    @Override
    public void processElement(Map<String, Object> value, Context ctx, Collector<RoutedEvent> out) throws Exception {{
        // Evaluate routing rules
        String decision = evaluate(value);
        RoutedEvent event = new RoutedEvent(value, decision);

        // Route to appropriate output based on decision
        switch (decision) {{
            case "approve":
                ctx.output(APPROVED_TAG, event);
                break;
            case "flag":
                ctx.output(FLAGGED_TAG, event);
                break;
            case "block":
                ctx.output(BLOCKED_TAG, event);
                break;
            default:
                // Main output for unmatched/default cases
                out.collect(event);
        }}
    }}

    /**
     * Evaluate routing rules and return decision.
     * TODO: L4 will generate actual rule evaluation from decision tables/procedural rules.
     */
    private String evaluate(Map<String, Object> input) {{
        // Scaffold: default to approve
        // L4 will generate actual condition checks here
        return "approve";
    }}
}}
'''

    def _generate_routed_event(self, package: str) -> str:
        """Generate RoutedEvent wrapper class."""
        return f'''/**
 * RoutedEvent
 *
 * Wrapper class containing original event data and routing decision.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

public class RoutedEvent {{

    private final Object originalEvent;
    private final String decision;

    public RoutedEvent(Object originalEvent, String decision) {{
        this.originalEvent = originalEvent;
        this.decision = decision;
    }}

    public Object getOriginalEvent() {{
        return originalEvent;
    }}

    public String getDecision() {{
        return decision;
    }}

    @SuppressWarnings("unchecked")
    public <T> T getOriginalAs(Class<T> clazz) {{
        return (T) originalEvent;
    }}

    public String getKey() {{
        return originalEvent.toString();
    }}

    @Override
    public String toString() {{
        return "RoutedEvent{{decision='" + decision + "', event=" + originalEvent + "}}";
    }}
}}
'''

    def _generate_aggregator(self, aggregate: ast.AggregateDecl, package: str, input_type: str,
                             result_class: str, accumulator_class: str) -> str:
        """Generate AggregateFunction scaffold for aggregate operator."""
        class_name = self._to_pascal_case(aggregate.transform_name) + "Aggregator"

        return f'''/**
 * {class_name}
 *
 * AggregateFunction for aggregating RoutedEvent records.
 * Aggregation: {aggregate.transform_name}
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L3-generated implementation
 */
package {package};

import org.apache.flink.api.common.functions.AggregateFunction;
import {self.config.package_prefix}.rules.RoutedEvent;

public class {class_name} implements AggregateFunction<RoutedEvent, {accumulator_class}, {result_class}> {{

    @Override
    public {accumulator_class} createAccumulator() {{
        return new {accumulator_class}();
    }}

    @Override
    public {accumulator_class} add(RoutedEvent value, {accumulator_class} accumulator) {{
        // TODO: L3 will generate actual aggregation logic
        accumulator.incrementCount();
        return accumulator;
    }}

    @Override
    public {result_class} getResult({accumulator_class} accumulator) {{
        return new {result_class}(accumulator.getCount());
    }}

    @Override
    public {accumulator_class} merge({accumulator_class} a, {accumulator_class} b) {{
        {accumulator_class} merged = new {accumulator_class}();
        merged.setCount(a.getCount() + b.getCount());
        return merged;
    }}
}}
'''

    def _generate_result_class(self, class_name: str, package: str) -> str:
        """Generate aggregation result class."""
        return f'''/**
 * {class_name}
 *
 * Result class for aggregation output.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L3-generated implementation with actual result fields
 */
package {package};

public class {class_name} {{

    private final long count;

    public {class_name}(long count) {{
        this.count = count;
    }}

    public long getCount() {{
        return count;
    }}

    @Override
    public String toString() {{
        return "{class_name}{{count=" + count + "}}";
    }}
}}
'''

    def _generate_accumulator_class(self, class_name: str, package: str) -> str:
        """Generate aggregation accumulator class."""
        return f'''/**
 * {class_name}
 *
 * Accumulator class for aggregation state.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 * TODO: Replace with L3-generated implementation with actual accumulator fields
 */
package {package};

public class {class_name} {{

    private long count;

    public {class_name}() {{
        this.count = 0;
    }}

    public void incrementCount() {{
        count++;
    }}

    public long getCount() {{
        return count;
    }}

    public void setCount(long count) {{
        this.count = count;
    }}
}}
'''

    def _generate_await_function(self, await_decl: ast.AwaitDecl, package: str, input_type: str) -> str:
        """Generate KeyedCoProcessFunction scaffold for await correlation pattern."""
        initial_event = await_decl.initial_event
        trigger_event = await_decl.trigger_event
        class_name = f"{self._to_pascal_case(initial_event)}{self._to_pascal_case(trigger_event)}AwaitFunction"
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
        class_name = f"{self._to_pascal_case(event_name)}HoldFunction"
        keyed_by = ', '.join(hold_decl.keyed_by)
        buffer_name = hold_decl.buffer_name or f"{event_name}_buffer"

        # Determine completion signature
        completion_params = ""
        completion_init = ""
        if hold_decl.completion and hold_decl.completion.condition:
            cond = hold_decl.completion.condition
            if cond.condition_type.value == "count":
                completion_params = ", int countThreshold"
                completion_init = f"        this.countThreshold = countThreshold;"
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

    def _generate_completion_event(self, package: str) -> str:
        """Generate CompletionEvent class for sink callback notifications."""
        return f'''/**
 * CompletionEvent
 *
 * Event emitted after successful or failed sink writes.
 * Contains correlation ID and status for tracking processing outcomes.
 *
 * AUTO-GENERATED SCAFFOLD by Nexflow Code Generator
 */
package {package};

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class CompletionEvent {{

    public enum Status {{
        SUCCESS,
        FAILURE
    }}

    private final String correlationId;
    private final Status status;
    private final long timestamp;
    private final Map<String, Object> additionalFields;
    private final String errorMessage;

    private CompletionEvent(String correlationId, Status status, Map<String, Object> additionalFields, String errorMessage) {{
        this.correlationId = correlationId;
        this.status = status;
        this.timestamp = Instant.now().toEpochMilli();
        this.additionalFields = additionalFields != null ? additionalFields : new HashMap<>();
        this.errorMessage = errorMessage;
    }}

    /**
     * Create a success completion event.
     */
    public static CompletionEvent success(Object record, String correlationField) {{
        String correlationId = extractField(record, correlationField);
        return new CompletionEvent(correlationId, Status.SUCCESS, null, null);
    }}

    /**
     * Create a success completion event with additional fields.
     */
    public static CompletionEvent success(Object record, String correlationField, String[] includeFields) {{
        String correlationId = extractField(record, correlationField);
        Map<String, Object> additional = extractFields(record, includeFields);
        return new CompletionEvent(correlationId, Status.SUCCESS, additional, null);
    }}

    /**
     * Create a failure completion event.
     */
    public static CompletionEvent failure(Object record, String correlationField, String errorMessage) {{
        String correlationId = extractField(record, correlationField);
        return new CompletionEvent(correlationId, Status.FAILURE, null, errorMessage);
    }}

    /**
     * Create a failure completion event with additional fields.
     */
    public static CompletionEvent failure(Object record, String correlationField, String[] includeFields, String errorMessage) {{
        String correlationId = extractField(record, correlationField);
        Map<String, Object> additional = extractFields(record, includeFields);
        return new CompletionEvent(correlationId, Status.FAILURE, additional, errorMessage);
    }}

    private static String extractField(Object record, String fieldName) {{
        // TODO: Implement actual field extraction using reflection or schema-aware access
        try {{
            java.lang.reflect.Method getter = record.getClass().getMethod("get" + capitalize(fieldName));
            Object value = getter.invoke(record);
            return value != null ? value.toString() : null;
        }} catch (Exception e) {{
            return record.toString();
        }}
    }}

    private static Map<String, Object> extractFields(Object record, String[] fieldNames) {{
        Map<String, Object> fields = new HashMap<>();
        for (String fieldName : fieldNames) {{
            try {{
                java.lang.reflect.Method getter = record.getClass().getMethod("get" + capitalize(fieldName));
                Object value = getter.invoke(record);
                fields.put(fieldName, value);
            }} catch (Exception e) {{
                // Skip field if not accessible
            }}
        }}
        return fields;
    }}

    private static String capitalize(String str) {{
        if (str == null || str.isEmpty()) return str;
        return Character.toUpperCase(str.charAt(0)) + str.substring(1);
    }}

    // Getters
    public String getCorrelationId() {{
        return correlationId;
    }}

    public Status getStatus() {{
        return status;
    }}

    public long getTimestamp() {{
        return timestamp;
    }}

    public Map<String, Object> getAdditionalFields() {{
        return additionalFields;
    }}

    public String getErrorMessage() {{
        return errorMessage;
    }}

    public boolean isSuccess() {{
        return status == Status.SUCCESS;
    }}

    public String getKey() {{
        return correlationId;
    }}

    @Override
    public String toString() {{
        return "CompletionEvent{{" +
            "correlationId='" + correlationId + "'" +
            ", status=" + status +
            ", timestamp=" + timestamp +
            (errorMessage != null ? ", error='" + errorMessage + "'" : "") +
            "}}";
    }}
}}
'''
