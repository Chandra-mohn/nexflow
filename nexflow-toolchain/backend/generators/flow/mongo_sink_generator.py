# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
MongoDB Sink Generator Mixin

Generates Flink MongoDB async sink code for L5 persist clauses.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L5 INTEGRATION:
The persist clause on emit triggers async MongoDB writes:
  emit to processed_events
      persist to transaction_store async
      batch size 100
      flush interval 5s
      on error continue

This generates MongoSink with AsyncSinkWriter pattern.
─────────────────────────────────────────────────────────────────────
"""

from typing import Optional, Set

from backend.ast.proc import EmitDecl, PersistDecl, PersistMode, PersistErrorAction
from backend.generators.infra import BindingResolver, ResolvedMongoDBPersistence


class MongoSinkGeneratorMixin:
    """
    Mixin for generating MongoDB async sink code.

    Generates:
    - MongoSink builder configuration
    - Async batch writes with configurable batch size and flush interval
    - Error handling (continue, fail, or emit to DLQ)
    """

    # Binding resolver is set by FlowGenerator
    _binding_resolver: BindingResolver

    def generate_mongo_sink_code(
        self,
        emit: EmitDecl,
        input_stream: str,
        input_type: str
    ) -> str:
        """Generate MongoDB async sink code for a persist clause.

        Args:
            emit: The emit declaration with persist clause
            input_stream: The Flink stream variable to sink from
            input_type: The Java type of the stream elements

        Returns:
            Java code for MongoDB async sink
        """
        if not emit.persist:
            return ""

        persist = emit.persist

        # Resolve persistence target from L5 config
        resolved = self._binding_resolver.resolve_persistence(
            persist.target,
            batch_size_override=persist.batch_size,
            flush_interval_override=persist.flush_interval
        )

        sink_name = self._to_camel_case(persist.target) + "MongoSink"

        return self._generate_mongo_sink(
            sink_name=sink_name,
            resolved=resolved,
            persist=persist,
            input_stream=input_stream,
            input_type=input_type
        )

    def _generate_mongo_sink(
        self,
        sink_name: str,
        resolved: ResolvedMongoDBPersistence,
        persist: PersistDecl,
        input_stream: str,
        input_type: str
    ) -> str:
        """Generate the MongoDB sink builder code."""

        # Build connection string with auth
        connection_uri = resolved.uri
        if resolved.auth_source and "authSource" not in connection_uri:
            separator = "&" if "?" in connection_uri else "?"
            connection_uri = f"{connection_uri}{separator}authSource={resolved.auth_source}"

        # TLS configuration
        tls_config = ""
        if resolved.tls_enabled:
            tls_config = "\n            .tls(true)"

        # Error handling configuration
        error_handling = self._generate_error_handling(persist)

        # Async mode configuration
        async_mode = persist.mode == PersistMode.ASYNC
        sink_mode = "async" if async_mode else "sync"

        lines = [
            f"        // MongoDB Persistence: {persist.target} ({sink_mode})",
            f"        // Database: {resolved.database}, Collection: {resolved.collection}",
            f"        MongoSink<{input_type}> {sink_name} = MongoSink",
            f"            .<{input_type}>builder()",
            f"            .setUri(\"{connection_uri}\")",
            f"            .setDatabase(\"{resolved.database}\")",
            f"            .setCollection(\"{resolved.collection}\")",
            f"            .setBatchSize({resolved.batch_size})",
            f"            .setBatchIntervalMs({resolved.flush_interval_ms})",
        ]

        # Add write concern
        write_concern_code = self._get_write_concern_code(resolved.write_concern)
        if write_concern_code:
            lines.append(f"            .setWriteConcern({write_concern_code})")

        # Add upsert configuration if present
        if resolved.upsert_key:
            key_fields = ', '.join(f'"{k}"' for k in resolved.upsert_key)
            lines.append(f"            .setUpsertKey(Arrays.asList({key_fields}))")

        if tls_config:
            lines.append(tls_config)

        lines.extend([
            f"            .setDocumentSerializer(new {input_type}MongoSerializer())",
            "            .build();",
            "",
        ])

        # Connect stream to sink
        if async_mode:
            lines.extend([
                f"        // Async write to MongoDB (non-blocking)",
                f"        {input_stream}",
                f"            .sinkTo({sink_name})",
                f"            .name(\"mongo-persist-{persist.target}\");",
            ])
        else:
            lines.extend([
                f"        // Sync write to MongoDB (blocking)",
                f"        {input_stream}",
                f"            .sinkTo({sink_name})",
                f"            .name(\"mongo-persist-{persist.target}\");",
            ])

        # Add error handling if configured
        if error_handling:
            lines.append("")
            lines.append(error_handling)

        return '\n'.join(lines)

    def _generate_error_handling(self, persist: PersistDecl) -> str:
        """Generate error handling code for MongoDB persistence."""
        if not persist.error_handler:
            return ""

        handler = persist.error_handler

        if handler.action == PersistErrorAction.CONTINUE:
            return f"        // Error handling: CONTINUE - failures are logged and ignored"
        elif handler.action == PersistErrorAction.FAIL:
            return f"        // Error handling: FAIL - failures will cause job to fail"
        elif handler.action == PersistErrorAction.EMIT:
            dlq = handler.dlq_target or f"{persist.target}_dlq"
            return f"        // Error handling: EMIT to DLQ topic: {dlq}"

        return ""

    def _get_write_concern_code(self, write_concern: str) -> str:
        """Convert write concern string to MongoDB Java code."""
        concern_mapping = {
            "w1": "WriteConcern.W1",
            "w2": "WriteConcern.W2",
            "w3": "WriteConcern.W3",
            "majority": "WriteConcern.MAJORITY",
            "acknowledged": "WriteConcern.ACKNOWLEDGED",
            "unacknowledged": "WriteConcern.UNACKNOWLEDGED",
            "journaled": "WriteConcern.JOURNALED",
        }
        return concern_mapping.get(write_concern, "WriteConcern.MAJORITY")

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.replace('-', '_').split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_mongo_sink_imports(self) -> Set[str]:
        """Get required imports for MongoDB sink generation."""
        return {
            'com.mongodb.client.model.WriteConcern',
            'org.apache.flink.connector.mongodb.sink.MongoSink',
            'org.apache.flink.connector.mongodb.sink.config.MongoWriteOptions',
            'java.util.Arrays',
        }

    def needs_mongo_sink(self, emit: EmitDecl) -> bool:
        """Check if emit requires MongoDB sink generation."""
        return emit.persist is not None
