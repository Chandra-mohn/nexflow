"""
Source Generator Mixin

Generates Flink DataStream source connections from L1 receive declarations.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L1 Input Block Features:
- receive X from source (with optional alias)
- schema S (type-safe deserialization)
- project [fields] / project except [fields] (field projection)
- store in buffer (buffered storage for correlation)
- match from buffer on [fields] (stream matching)
─────────────────────────────────────────────────────────────────────
"""

from typing import Dict, List, Optional, Set, Tuple

from backend.ast import proc_ast as ast


class SourceGeneratorMixin:
    """
    Mixin for generating Flink source connectors.

    Generates:
    - KafkaSource builders for Kafka topics
    - Schema deserialization setup
    - Watermark strategies
    - Field projection (map to subset of fields)
    - Store actions (buffer to ListState)
    - Match actions (join with buffered state)
    """

    # Track streams that are stored in buffers for later matching
    _stored_streams: Dict[str, Tuple[str, str]] = {}  # buffer_name -> (stream_var, schema_class)

    def generate_source_code(self, process: ast.ProcessDefinition) -> str:
        """Generate source connection code for a process."""
        if not process.input or not process.input.receives:
            return "// No input sources defined\n"

        # Reset stored streams for this process
        self._stored_streams = {}

        lines = []
        for receive in process.input.receives:
            source_code = self._generate_source(receive, process)
            lines.append(source_code)

        return '\n'.join(lines)

    def _generate_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate source code for a single receive declaration."""
        source_name = receive.source
        # Feature 1: Use alias if provided, otherwise use source name
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        lines = []

        # Build Kafka source
        lines.extend([
            f"// Source: {source_name}" + (f" (alias: {stream_alias})" if receive.alias else ""),
            f"KafkaSource<{schema_class}> {self._to_camel_case(source_name)}Source = KafkaSource",
            f"    .<{schema_class}>builder()",
            f"    .setBootstrapServers(KAFKA_BOOTSTRAP_SERVERS)",
            f"    .setTopics(\"{source_name}\")",
            f"    .setGroupId(\"{process.name}-consumer\")",
            f"    .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))",
            f"    .setValueOnlyDeserializer(new JsonDeserializationSchema<>({schema_class}.class))",
            "    .build();",
            "",
        ])

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process, schema_class)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource(",
            f"        {self._to_camel_case(source_name)}Source,",
            f"        {watermark_strategy},",
            f"        \"{source_name}\"",
            f"    );",
            "",
        ])

        # Feature 2: Field projection
        if receive.project:
            projection_code, projected_var = self._generate_projection(
                receive, stream_var, schema_class, stream_alias
            )
            lines.append(projection_code)
            stream_var = projected_var

        # Feature 3a: Store action (buffer for later matching)
        if receive.store_action:
            store_code = self._generate_store_action(
                receive.store_action, stream_var, schema_class, stream_alias
            )
            lines.append(store_code)
            # Track this stored stream for match operations
            self._stored_streams[receive.store_action.state_name] = (stream_var, schema_class)

        # Feature 3b: Match action (join with buffered state)
        if receive.match_action:
            match_code, matched_var = self._generate_match_action(
                receive.match_action, stream_var, schema_class, stream_alias
            )
            lines.append(match_code)
            stream_var = matched_var

        return '\n'.join(lines)

    def _generate_projection(
        self,
        receive: ast.ReceiveDecl,
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """
        Generate field projection code.

        Feature 2: project [fields] / project except [fields]

        Strategy: Post-deserialization projection using Map<String, Object>
        - Deserialize full schema first
        - Map to only needed fields
        - Reduces memory footprint for downstream operators
        """
        project = receive.project
        projected_var = f"projected{self.to_java_class_name(stream_alias)}Stream"

        if project.is_except:
            # project except [fields] - include all EXCEPT these fields
            # This requires knowing all fields, so we generate runtime exclusion
            excluded_fields = ', '.join(f'"{f}"' for f in project.fields)
            lines = [
                f"// Projection: exclude [{', '.join(project.fields)}]",
                f"DataStream<Map<String, Object>> {projected_var} = {stream_var}",
                f"    .map(event -> {{",
                f"        Map<String, Object> projected = new HashMap<>();",
                f"        java.util.Set<String> excluded = java.util.Set.of({excluded_fields});",
                f"        // Copy all fields except excluded ones",
                f"        // Note: For production, use reflection or generated field list",
                f"        java.lang.reflect.Method[] methods = event.getClass().getMethods();",
                f"        for (java.lang.reflect.Method method : methods) {{",
                f"            String name = method.getName();",
                f"            if (name.startsWith(\"get\") && !name.equals(\"getClass\") && method.getParameterCount() == 0) {{",
                f"                String fieldName = Character.toLowerCase(name.charAt(3)) + name.substring(4);",
                f"                // Convert camelCase to snake_case for DSL field names",
                f"                String snakeCase = fieldName.replaceAll(\"([a-z])([A-Z])\", \"$1_$2\").toLowerCase();",
                f"                if (!excluded.contains(snakeCase)) {{",
                f"                    try {{",
                f"                        projected.put(snakeCase, method.invoke(event));",
                f"                    }} catch (Exception e) {{ /* skip */ }}",
                f"                }}",
                f"            }}",
                f"        }}",
                f"        return projected;",
                f"    }})",
                f"    .name(\"project-except-{stream_alias}\");",
                "",
            ]
        else:
            # project [fields] - include ONLY these fields
            field_mappings = []
            for field in project.fields:
                getter = f"event.get{self._to_pascal_case(field)}()"
                field_mappings.append(f'        projected.put("{field}", {getter});')

            lines = [
                f"// Projection: include only [{', '.join(project.fields)}]",
                f"DataStream<Map<String, Object>> {projected_var} = {stream_var}",
                f"    .map(event -> {{",
                f"        Map<String, Object> projected = new HashMap<>({len(project.fields)});",
                '\n'.join(field_mappings),
                f"        return projected;",
                f"    }})",
                f"    .name(\"project-{stream_alias}\");",
                "",
            ]

        return '\n'.join(lines), projected_var

    def _generate_store_action(
        self,
        store_action: ast.StoreAction,
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> str:
        """
        Generate store action code.

        Feature 3a: store in buffer

        Stores incoming events in a named buffer (ListState) for later
        correlation with match operations.
        """
        buffer_name = store_action.state_name

        lines = [
            f"// Store: buffer events in '{buffer_name}' for later matching",
            f"// Note: Actual buffering implemented in KeyedProcessFunction",
            f"// The buffer '{buffer_name}' will be populated when processing keyed stream",
            f"// See: {self.to_java_class_name(buffer_name)}BufferFunction",
            "",
        ]

        return '\n'.join(lines)

    def _generate_match_action(
        self,
        match_action: ast.MatchAction,
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """
        Generate match action code.

        Feature 3b: match from buffer on [fields]

        Joins incoming stream with previously buffered events based on
        specified correlation fields.
        """
        buffer_name = match_action.state_name
        on_fields = match_action.on_fields
        matched_var = f"matched{self.to_java_class_name(stream_alias)}Stream"
        function_class = f"{self.to_java_class_name(buffer_name)}MatchFunction"

        # Generate key selector for matching
        if len(on_fields) == 1:
            key_selector = f"event -> event.get{self._to_pascal_case(on_fields[0])}().toString()"
        else:
            getters = ' + \":\" + '.join(
                f"event.get{self._to_pascal_case(f)}().toString()" for f in on_fields
            )
            key_selector = f"event -> {getters}"

        # Check if we have a stored stream for this buffer
        if buffer_name in self._stored_streams:
            buffered_stream_var, buffered_schema = self._stored_streams[buffer_name]
            # Build correlation key array outside f-string (backslash not allowed in f-string)
            quoted_fields = ', '.join('"' + f + '"' for f in on_fields)
            correlation_key_array = 'new String[]{' + quoted_fields + '}'
            lines = [
                f"// Match: join with buffered '{buffer_name}' on [{', '.join(on_fields)}]",
                f"KeyedStream<{schema_class}, String> keyed{self.to_java_class_name(stream_alias)} = {stream_var}",
                f"    .keyBy({key_selector});",
                "",
                f"KeyedStream<{buffered_schema}, String> keyed{self.to_java_class_name(buffer_name)} = {buffered_stream_var}",
                f"    .keyBy(event -> event.getCorrelationKey({correlation_key_array}));",
                "",
                f"DataStream<MatchedEvent> {matched_var} = keyed{self.to_java_class_name(stream_alias)}",
                f"    .connect(keyed{self.to_java_class_name(buffer_name)})",
                f"    .process(new {function_class}())",
                f"    .name(\"match-{stream_alias}-from-{buffer_name}\");",
                "",
            ]
        else:
            # Buffer not yet defined - generate placeholder
            lines = [
                f"// Match: join with buffered '{buffer_name}' on [{', '.join(on_fields)}]",
                f"// Note: Buffer '{buffer_name}' must be defined earlier in the pipeline",
                f"KeyedStream<{schema_class}, String> keyed{self.to_java_class_name(stream_alias)} = {stream_var}",
                f"    .keyBy({key_selector});",
                "",
                f"// Connect with buffered stream and process matches",
                f"DataStream<MatchedEvent> {matched_var} = keyed{self.to_java_class_name(stream_alias)}",
                f"    .process(new {function_class}())",
                f"    .name(\"match-{stream_alias}-from-{buffer_name}\");",
                "",
            ]

        return '\n'.join(lines), matched_var

    def _generate_watermark_strategy(self, process: ast.ProcessDefinition, schema_class: str) -> str:
        """Generate watermark strategy based on time configuration."""
        if not process.execution or not process.execution.time:
            return f"WatermarkStrategy.<{schema_class}>noWatermarks()"

        time_decl = process.execution.time
        time_field = time_decl.time_field.parts[-1]  # Get last part of field path

        if time_decl.watermark:
            delay_ms = self._duration_to_ms(time_decl.watermark.delay)
            return f'''WatermarkStrategy
                .<{schema_class}>forBoundedOutOfOrderness(Duration.ofMillis({delay_ms}))
                .withTimestampAssigner((event, timestamp) -> event.get{self._to_pascal_case(time_field)}().toEpochMilli())'''

        return f"WatermarkStrategy.<{schema_class}>noWatermarks()"

    def _generate_key_selector(self, schema_class: str, fields: List[str]) -> str:
        """Generate KeySelector for partitioning."""
        if len(fields) == 1:
            field = fields[0]
            return f"event -> event.get{self._to_pascal_case(field)}()"
        else:
            # Composite key - generate Tuple
            getters = ', '.join(f"event.get{self._to_pascal_case(f)}()" for f in fields)
            return f"event -> Tuple{len(fields)}.of({getters})"

    def _get_schema_class(self, receive: ast.ReceiveDecl) -> str:
        """Get the schema class name for a receive declaration."""
        if receive.schema and receive.schema.schema_name:
            return self.to_java_class_name(receive.schema.schema_name)
        # Default to source name as schema
        return self.to_java_class_name(receive.source)

    def _to_stream_var(self, name: str) -> str:
        """Convert source name to stream variable name."""
        return self._to_camel_case(name) + "Stream"

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def _duration_to_ms(self, duration) -> int:
        """Convert Duration to milliseconds."""
        if hasattr(duration, 'to_milliseconds'):
            return duration.to_milliseconds()
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return duration.value * multipliers.get(duration.unit, 1)

    def get_source_imports(self) -> Set[str]:
        """Get required imports for source generation."""
        return {
            'org.apache.flink.api.common.eventtime.WatermarkStrategy',
            'org.apache.flink.connector.kafka.source.KafkaSource',
            'org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer',
            'org.apache.kafka.clients.consumer.OffsetResetStrategy',
            'org.apache.flink.streaming.api.datastream.DataStream',
            'org.apache.flink.streaming.api.datastream.KeyedStream',
            'org.apache.flink.formats.json.JsonDeserializationSchema',
            'java.time.Duration',
            'java.util.Map',
            'java.util.HashMap',
        }

    def get_match_imports(self) -> Set[str]:
        """Get additional imports needed for match operations."""
        return {
            'org.apache.flink.streaming.api.datastream.ConnectedStreams',
            'org.apache.flink.streaming.api.functions.co.KeyedCoProcessFunction',
        }
