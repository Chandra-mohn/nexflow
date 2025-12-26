# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Basic Operators Mixin

Generates Flink code for: transform, enrich, route, aggregate operators.
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case


class BasicOperatorsMixin:
    """Mixin for basic Flink operator wiring (transform, enrich, route, aggregate)."""

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
        """
        context = getattr(self.config, 'validation_context', None)
        if not context:
            return fallback_type

        transform_def = context.transforms.get(transform_name)
        if not transform_def:
            return fallback_type

        output_spec = getattr(transform_def, 'output', None)
        if not output_spec:
            return fallback_type

        # Single type output (e.g., output schema_name)
        if output_spec.single_type:
            if output_spec.single_type.custom_type:
                return to_pascal_case(output_spec.single_type.custom_type)
            elif output_spec.single_type.base_type:
                return self._base_type_to_java(output_spec.single_type.base_type)

        # Check output fields
        if output_spec.fields:
            if len(output_spec.fields) == 1:
                field = output_spec.fields[0]
                if field.field_type and field.field_type.custom_type:
                    return to_pascal_case(field.field_type.custom_type)
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
            rule_name = route.rule_name
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
        """Compile a DSL condition expression to Java boolean expression."""
        import re

        if not condition or condition.strip() == "true":
            return "true"
        if condition.strip() == "false":
            return "false"

        result = condition

        # Replace boolean operators
        result = re.sub(r'\band\b', '&&', result)
        result = re.sub(r'\bor\b', '||', result)
        result = re.sub(r'\bnot\s+', '!', result)

        # Handle string comparisons
        def replace_string_eq(match):
            field = match.group(1).strip()
            string_val = match.group(2)
            getter = self._field_to_getter(field, "value")
            return f'{string_val}.equals({getter})'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*==\s*("[^"]*")', replace_string_eq, result)

        def replace_string_ne(match):
            field = match.group(1).strip()
            string_val = match.group(2)
            getter = self._field_to_getter(field, "value")
            return f'!{string_val}.equals({getter})'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*!=\s*("[^"]*")', replace_string_ne, result)

        # Handle numeric comparisons
        def replace_numeric_comparison(match):
            field = match.group(1).strip()
            op = match.group(2)
            num = match.group(3)
            getter = self._field_to_getter(field, "value")
            return f'{getter} {op} {num}'

        result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(>=|<=|>|<|==|!=)\s*(-?\d+(?:\.\d+)?)', replace_numeric_comparison, result)

        # Handle standalone boolean field paths
        tokens = []
        i = 0
        while i < len(result):
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
                j = i
                while j < len(result) and (result[j].isalnum() or result[j] in '._()'):
                    j += 1
                tokens.append(result[i:j])
                i = j
            elif result[i].isalpha() or result[i] == '_':
                j = i
                while j < len(result) and (result[j].isalnum() or result[j] in '_.'):
                    j += 1
                identifier = result[i:j]
                if identifier in ('true', 'false', 'null', 'equals', 'get'):
                    tokens.append(identifier)
                elif j < len(result) and result[j] == '(':
                    tokens.append(identifier)
                elif identifier.replace('.', '').isdigit():
                    tokens.append(identifier)
                else:
                    tokens.append(self._field_to_getter(identifier, "value"))
                i = j
            elif result[i].isdigit() or (result[i] == '-' and i+1 < len(result) and result[i+1].isdigit()):
                j = i
                if result[j] == '-':
                    j += 1
                while j < len(result) and (result[j].isdigit() or result[j] == '.'):
                    j += 1
                tokens.append(result[i:j])
                i = j
            elif result[i] == '"':
                j = i + 1
                while j < len(result) and result[j] != '"':
                    if result[j] == '\\':
                        j += 1
                    j += 1
                j += 1
                tokens.append(result[i:j])
                i = j
            else:
                tokens.append(result[i])
                i += 1

        return ''.join(tokens)

    def _field_to_getter(self, field_path: str, obj_name: str) -> str:
        """Convert a field path to a Java Record accessor chain."""
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
