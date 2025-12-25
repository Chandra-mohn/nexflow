# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Job Imports Mixin

Generates import statements for Flink job classes.
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case


class JobImportsMixin:
    """Mixin for generating job imports based on used operators."""

    def _generate_job_imports(self, process: ast.ProcessDefinition) -> str:
        """Generate import statements for job class.

        COVENANT: Only imports classes that are actually used in the generated code.
        """
        imports = self._get_core_imports()
        imports.extend(self._get_operator_imports(process))
        imports.extend(self._get_schema_imports(process))
        imports.extend(self._get_transform_imports(process))
        imports.extend(self._get_correlation_imports(process))
        imports.extend(self._get_completion_imports(process))
        imports.extend(self._get_persistence_imports(process))
        imports.extend(self._get_source_connector_imports(process))

        # Remove duplicates and sort
        imports = sorted(set(imports))
        return '\n'.join(f"import {imp};" for imp in imports)

    def _get_core_imports(self) -> list:
        """Get core imports always needed."""
        return [
            "org.apache.flink.streaming.api.environment.StreamExecutionEnvironment",
            "org.apache.flink.streaming.api.datastream.DataStream",
            "org.apache.flink.api.common.eventtime.WatermarkStrategy",
            "org.apache.flink.connector.kafka.source.KafkaSource",
            "org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer",
            "org.apache.flink.connector.kafka.sink.KafkaSink",
            "org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema",
            "org.apache.flink.connector.base.DeliveryGuarantee",
            "org.apache.flink.formats.json.JsonDeserializationSchema",
            "org.apache.flink.formats.json.JsonSerializationSchema",
            "org.apache.kafka.clients.consumer.OffsetResetStrategy",
            "java.time.Duration",
        ]

    def _get_operator_imports(self, process: ast.ProcessDefinition) -> list:
        """Get imports based on used operators."""
        imports = []

        # Analyze what operators are used
        has_transforms = False
        has_enrich = False
        has_route = False
        has_aggregate = False
        has_window = False
        has_join = False
        has_late_data = False
        has_sql = False
        has_parallel = False
        has_validate_input = False
        has_lookup = False
        has_evaluate = False

        def scan_operators(ops):
            """Recursively scan operators including nested ones in parallel blocks."""
            nonlocal has_transforms, has_enrich, has_route, has_aggregate
            nonlocal has_window, has_join, has_late_data, has_sql
            nonlocal has_parallel, has_validate_input, has_lookup, has_evaluate

            for op in ops:
                if isinstance(op, ast.TransformDecl):
                    has_transforms = True
                elif isinstance(op, ast.EnrichDecl):
                    has_enrich = True
                elif isinstance(op, ast.RouteDecl):
                    has_route = True
                elif isinstance(op, ast.AggregateDecl):
                    has_aggregate = True
                elif isinstance(op, ast.WindowDecl):
                    has_window = True
                    if op.options and op.options.late_data:
                        has_late_data = True
                elif isinstance(op, ast.JoinDecl):
                    has_join = True
                elif isinstance(op, ast.SqlTransformDecl):
                    has_sql = True
                elif isinstance(op, ast.ParallelDecl):
                    has_parallel = True
                    # Scan branch bodies
                    if hasattr(op, 'branches') and op.branches:
                        for branch in op.branches:
                            if hasattr(branch, 'body') and branch.body:
                                scan_operators(branch.body)
                elif isinstance(op, ast.ValidateInputDecl):
                    has_validate_input = True
                elif isinstance(op, ast.LookupDecl):
                    has_lookup = True
                elif isinstance(op, ast.EvaluateDecl):
                    has_evaluate = True

        if process.processing:
            scan_operators(process.processing)

        # Check global late data config
        if process.execution and process.execution.time and process.execution.time.late_data:
            has_late_data = True

        if has_transforms:
            imports.append("java.util.Map")

        if has_enrich:
            imports.extend([
                "org.apache.flink.streaming.api.datastream.AsyncDataStream",
                "java.util.concurrent.TimeUnit",
            ])

        if has_route:
            imports.extend([
                "org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator",
                "org.apache.flink.streaming.api.functions.ProcessFunction",
                "org.apache.flink.util.Collector",
            ])

        if has_window or has_aggregate:
            imports.extend([
                "org.apache.flink.streaming.api.windowing.time.Time",
                "org.apache.flink.streaming.api.windowing.windows.TimeWindow",
            ])

        if has_window:
            imports.extend([
                "org.apache.flink.streaming.api.datastream.WindowedStream",
                "org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows",
                "org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows",
                "org.apache.flink.streaming.api.windowing.assigners.EventTimeSessionWindows",
            ])

        if has_late_data:
            imports.append("org.apache.flink.util.OutputTag")

        if has_join:
            imports.append("org.apache.flink.streaming.api.windowing.time.Time")

        # Parallel block imports
        if has_parallel:
            imports.extend([
                "org.apache.flink.util.OutputTag",
                "org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator",
                "org.apache.flink.streaming.api.functions.ProcessFunction",
                "org.apache.flink.util.Collector",
            ])

        # Validate input imports
        if has_validate_input:
            imports.extend([
                "org.apache.flink.util.OutputTag",
                "org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator",
                "org.apache.flink.streaming.api.functions.ProcessFunction",
                "org.apache.flink.util.Collector",
            ])

        # Lookup imports
        if has_lookup:
            imports.extend([
                "org.apache.flink.streaming.api.datastream.AsyncDataStream",
                "java.util.concurrent.TimeUnit",
            ])

        # SQL transform imports (Flink SQL / Table API)
        if has_sql:
            imports.extend([
                "org.apache.flink.table.api.Table",
                "org.apache.flink.table.api.bridge.java.StreamTableEnvironment",
            ])

        # Checkpoint imports
        if process.resilience and process.resilience.checkpoint:
            imports.append("org.apache.flink.streaming.api.CheckpointingMode")

        return imports

    def _get_schema_imports(self, process: ast.ProcessDefinition) -> list:
        """Get schema-related imports."""
        imports = []
        schema_package = f"{self.config.package_prefix}.schema"

        # Check for enrich to determine if Enriched types are needed
        has_enrich = False
        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.EnrichDecl):
                    has_enrich = True
                    break

        # v0.5.0+: process.receives is a direct list
        if process.receives:
            for receive in process.receives:
                if receive.schema and receive.schema.schema_name:
                    schema_class = to_pascal_case(receive.schema.schema_name)
                    imports.append(f"{schema_package}.{schema_class}")
                    if has_enrich:
                        imports.append(f"{schema_package}.Enriched{schema_class}")

        return imports

    def _get_transform_imports(self, process: ast.ProcessDefinition) -> list:
        """Get transform function imports."""
        imports = []
        transform_package = f"{self.config.package_prefix}.transform"
        rules_package = f"{self.config.package_prefix}.rules"

        if process.processing:
            for op in process.processing:
                if isinstance(op, ast.TransformDecl):
                    transform_class = to_pascal_case(op.transform_name) + "Function"
                    imports.append(f"{transform_package}.{transform_class}")
                elif isinstance(op, ast.EnrichDecl):
                    async_class = to_pascal_case(op.lookup_name) + "AsyncFunction"
                    imports.append(f"{transform_package}.{async_class}")
                elif isinstance(op, ast.RouteDecl):
                    if op.rule_name:
                        # 'route using' form - import the L4 rules router
                        # Handle dotted rule names (e.g., decision_result.decision)
                        safe_rule_name = op.rule_name.replace('.', '_')
                        router_class = to_pascal_case(safe_rule_name) + "Router"
                        imports.append(f"{rules_package}.{router_class}")
                    # Both forms need RoutedEvent
                    imports.append(f"{rules_package}.RoutedEvent")
                elif isinstance(op, ast.AggregateDecl):
                    agg_class = to_pascal_case(op.transform_name) + "Aggregator"
                    result_class = to_pascal_case(op.transform_name) + "Result"
                    imports.append(f"{transform_package}.{agg_class}")
                    imports.append(f"{transform_package}.{result_class}")
                elif isinstance(op, ast.LookupDecl):
                    lookup_class = to_pascal_case(op.source_name) + "LookupFunction"
                    imports.append(f"{transform_package}.{lookup_class}")
                    imports.append(f"{rules_package}.LookupResult")
                elif isinstance(op, ast.EvaluateDecl):
                    if hasattr(op, 'rule_name') and op.rule_name:
                        evaluator_class = to_pascal_case(op.rule_name) + "Evaluator"
                        imports.append(f"{rules_package}.{evaluator_class}")

        return imports

    def _get_correlation_imports(self, process: ast.ProcessDefinition) -> list:
        """Get correlation-related imports."""
        imports = []

        has_await = isinstance(process.correlation, ast.AwaitDecl) if process.correlation else False
        has_hold = isinstance(process.correlation, ast.HoldDecl) if process.correlation else False

        if has_await or has_hold:
            imports.extend([
                "org.apache.flink.streaming.api.functions.co.KeyedCoProcessFunction",
                "org.apache.flink.streaming.api.datastream.KeyedStream",
                "org.apache.flink.util.OutputTag",
                "org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator",
            ])

        if has_await:
            imports.append("org.apache.flink.streaming.api.datastream.ConnectedStreams")

        if has_hold:
            imports.extend([
                "org.apache.flink.api.common.state.ListState",
                "org.apache.flink.api.common.state.ListStateDescriptor",
            ])

        correlation_package = f"{self.config.package_prefix}.correlation"
        if process.correlation:
            if isinstance(process.correlation, ast.AwaitDecl):
                await_decl = process.correlation
                await_class = f"{to_pascal_case(await_decl.initial_event)}{to_pascal_case(await_decl.trigger_event)}AwaitFunction"
                imports.append(f"{correlation_package}.{await_class}")
                imports.append(f"{correlation_package}.CorrelatedEvent")
            elif isinstance(process.correlation, ast.HoldDecl):
                hold_decl = process.correlation
                hold_class = f"{to_pascal_case(hold_decl.event)}HoldFunction"
                imports.append(f"{correlation_package}.{hold_class}")
                imports.append(f"{correlation_package}.HeldBatch")

        return imports

    def _get_completion_imports(self, process: ast.ProcessDefinition) -> list:
        """Get completion-related imports."""
        imports = []

        if process.completion:
            imports.append("org.apache.flink.api.common.serialization.SimpleStringSchema")
            completion_package = f"{self.config.package_prefix}.completion"
            if process.completion.on_commit or process.completion.on_commit_failure:
                imports.append(f"{completion_package}.CompletionEvent")

        return imports

    def _get_persistence_imports(self, process: ast.ProcessDefinition) -> list:
        """Get MongoDB persistence imports (L5 integration)."""
        imports = []

        # Check if any emit has persist clause
        has_persist = False
        if process.emits:
            for emit in process.emits:
                if isinstance(emit, ast.EmitDecl) and emit.persist:
                    has_persist = True
                    break

        if has_persist:
            imports.extend([
                "com.mongodb.client.model.WriteConcern",
                "org.apache.flink.connector.mongodb.sink.MongoSink",
                "org.apache.flink.connector.mongodb.sink.config.MongoWriteOptions",
                "java.util.Arrays",
            ])

            # Add serializer imports for each persist target
            serializer_package = f"{self.config.package_prefix}.serializer"
            for emit in process.emits:
                if isinstance(emit, ast.EmitDecl) and emit.persist:
                    if emit.schema and emit.schema.schema_name:
                        schema_class = to_pascal_case(emit.schema.schema_name)
                    else:
                        schema_class = to_pascal_case(emit.target)
                    imports.append(f"{serializer_package}.{schema_class}MongoSerializer")

        return imports

    def _get_source_connector_imports(self, process: ast.ProcessDefinition) -> list:
        """Get source connector imports based on connector types (v0.8.0+).

        Supports Parquet, CSV, and other file-based connectors.
        """
        imports = []

        has_parquet = False
        has_csv = False

        if process.receives:
            for receive in process.receives:
                connector_type = getattr(receive, 'connector_type', None)
                if connector_type:
                    if connector_type == ast.ConnectorType.PARQUET:
                        has_parquet = True
                    elif connector_type == ast.ConnectorType.CSV:
                        has_csv = True

        # Parquet source imports
        if has_parquet:
            imports.extend([
                "org.apache.flink.connector.file.src.FileSource",
                "org.apache.flink.core.fs.Path",
                "org.apache.flink.formats.parquet.ParquetColumnarRowInputFormat",
                "org.apache.flink.formats.parquet.avro.AvroParquetReaders",
                "org.apache.flink.table.types.logical.RowType",
            ])

        # CSV source imports
        if has_csv:
            imports.extend([
                "org.apache.flink.connector.file.src.FileSource",
                "org.apache.flink.core.fs.Path",
                "org.apache.flink.formats.csv.CsvReaderFormat",
                "org.apache.flink.formats.csv.CsvRowDataDeserializationSchema",
            ])

        return imports
