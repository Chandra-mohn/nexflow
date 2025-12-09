"""
Scaffold Operators Mixin

Generates scaffold classes for processing operators:
- AsyncFunction (enrich)
- MapFunction (transform)
- ProcessFunction/Router (route)
- AggregateFunction (aggregate)
"""

from pathlib import Path

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case


class ScaffoldOperatorsMixin:
    """Mixin for generating processing operator scaffolds."""

    def _generate_enrich_scaffold(
        self, enrich: ast.EnrichDecl, transform_package: str, transform_path: Path,
        schema_package: str, schema_path: Path, input_type: str
    ) -> None:
        """Generate AsyncFunction and Enriched wrapper scaffolds for enrich operator."""
        async_class = to_pascal_case(enrich.lookup_name) + "AsyncFunction"
        content = self._generate_async_function(enrich, transform_package, input_type)
        self.result.add_file(transform_path / f"{async_class}.java", content, "java")

        enriched_class = f"Enriched{input_type}"
        enriched_content = self._generate_enriched_wrapper(enriched_class, schema_package, input_type)
        self.result.add_file(schema_path / f"{enriched_class}.java", enriched_content, "java")

    def _generate_transform_scaffold(
        self, transform: ast.TransformDecl, transform_package: str,
        transform_path: Path, input_type: str
    ) -> None:
        """Generate MapFunction scaffold for transform operator."""
        transform_class = to_pascal_case(transform.transform_name) + "Function"
        content = self._generate_transform_function(transform, transform_package, input_type)
        self.result.add_file(transform_path / f"{transform_class}.java", content, "java")

    def _generate_route_scaffold(
        self, route: ast.RouteDecl, rules_package: str,
        rules_path: Path, input_type: str
    ) -> None:
        """Generate Router ProcessFunction scaffold for route operator."""
        router_class = to_pascal_case(route.rule_name) + "Router"
        content = self._generate_router(route, rules_package, input_type)
        self.result.add_file(rules_path / f"{router_class}.java", content, "java")

    def _generate_aggregate_scaffold(
        self, aggregate: ast.AggregateDecl, transform_package: str,
        transform_path: Path, input_type: str
    ) -> None:
        """Generate AggregateFunction, Result, and Accumulator scaffolds."""
        agg_class = to_pascal_case(aggregate.transform_name) + "Aggregator"
        result_class = to_pascal_case(aggregate.transform_name) + "Result"
        accumulator_class = to_pascal_case(aggregate.transform_name) + "Accumulator"

        agg_content = self._generate_aggregator(
            aggregate, transform_package, input_type, result_class, accumulator_class
        )
        self.result.add_file(transform_path / f"{agg_class}.java", agg_content, "java")

        result_content = self._generate_result_class(result_class, transform_package)
        self.result.add_file(transform_path / f"{result_class}.java", result_content, "java")

        accumulator_content = self._generate_accumulator_class(accumulator_class, transform_package)
        self.result.add_file(transform_path / f"{accumulator_class}.java", accumulator_content, "java")

    def _generate_async_function(self, enrich: ast.EnrichDecl, package: str, input_type: str) -> str:
        """Generate AsyncFunction scaffold for enrich operator."""
        class_name = to_pascal_case(enrich.lookup_name) + "AsyncFunction"
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
        """Generate MapFunction scaffold for transform operator."""
        class_name = to_pascal_case(transform.transform_name) + "Function"
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
        class_name = to_pascal_case(route.rule_name) + "Router"

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

    def _generate_aggregator(
        self, aggregate: ast.AggregateDecl, package: str, input_type: str,
        result_class: str, accumulator_class: str
    ) -> str:
        """Generate AggregateFunction scaffold for aggregate operator."""
        class_name = to_pascal_case(aggregate.transform_name) + "Aggregator"

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
