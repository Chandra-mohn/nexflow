# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Serialization Mixin

Handles format detection and deserializer generation for source connectors.
Supports: JSON, Avro, Confluent Avro, Protobuf
"""

from typing import Set

from backend.ast import proc_ast as ast
from backend.ast.serialization import SerializationConfig, SerializationFormat
from backend.config.policy_validator import PolicyValidator


class SerializationMixin:
    """Mixin for serialization format handling and deserializer generation."""

    def _get_effective_serialization(
        self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition
    ) -> SerializationConfig:
        """Get effective serialization config for a receive declaration.

        Applies organization policy governance:
        1. Determine requested format from hierarchy
        2. Validate against org policy (if configured)
        3. Use org default if format not allowed (with warning)

        Priority: process-level override > schema declaration > team config > org default
        """
        # Determine the requested format from hierarchy
        requested_format = None

        # Check for process-level format override on the receive declaration
        if hasattr(receive, 'format_override') and receive.format_override:
            requested_format = receive.format_override

        # Check for schema-level serialization declaration
        if requested_format is None and hasattr(self, '_serialization_config') and self._serialization_config:
            requested_format = self._serialization_config.format

        # Get organization policy from config (if available)
        org_policy = getattr(self.config, 'org_policy', None) if hasattr(self, 'config') else None

        if org_policy is not None:
            # Use policy validator for governance
            validator = PolicyValidator(org_policy)
            result = validator.validate_format(
                requested_format,
                source_file=getattr(self.config, 'source_file', None) if hasattr(self, 'config') else None,
                context=f"receive from {receive.source}"
            )

            # Notify violation handler if configured
            if result.violations and hasattr(self, 'config'):
                handler = getattr(self.config, 'violation_handler', None)
                if handler:
                    handler(result)

            # Use policy-resolved format
            resolved_format = result.resolved_format or org_policy.default_format
            return SerializationConfig(
                format=resolved_format,
                registry_url=getattr(receive, 'registry_override', None)
            )

        # No org policy - fall back to legacy behavior
        if requested_format:
            return SerializationConfig(
                format=requested_format,
                registry_url=getattr(receive, 'registry_override', None)
            )

        # Default: JSON format
        return SerializationConfig(format=SerializationFormat.JSON)

    def _generate_deserializer(
        self, schema_class: str, serialization: SerializationConfig
    ) -> str:
        """Generate format-specific deserializer code.

        Generates the appropriate deserializer for:
        - JSON: JsonDeserializationSchema
        - Avro: AvroDeserializationSchema (specific records)
        - Confluent Avro: ConfluentRegistryAvroDeserializationSchema
        - Protobuf: ProtobufDeserializationSchema
        """
        fmt = serialization.format

        if fmt == SerializationFormat.JSON:
            return f"new JsonDeserializationSchema<>({schema_class}.class)"

        elif fmt == SerializationFormat.AVRO:
            return f"AvroDeserializationSchema.forSpecific({schema_class}.class)"

        elif fmt == SerializationFormat.CONFLUENT_AVRO:
            registry_url = serialization.registry_url or "SCHEMA_REGISTRY_URL"
            return f'''ConfluentRegistryAvroDeserializationSchema.forSpecific(
            {schema_class}.class,
            {registry_url}
        )'''

        elif fmt == SerializationFormat.PROTOBUF:
            return f"new ProtobufDeserializationSchema<>({schema_class}.class)"

        else:
            # Fallback to JSON
            return f"new JsonDeserializationSchema<>({schema_class}.class)"

    def get_serialization_imports(self, serialization: SerializationConfig) -> Set[str]:
        """Get imports needed for the specified serialization format."""
        fmt = serialization.format
        imports = set()

        if fmt == SerializationFormat.JSON:
            imports.add('org.apache.flink.formats.json.JsonDeserializationSchema')

        elif fmt == SerializationFormat.AVRO:
            imports.add('org.apache.flink.formats.avro.AvroDeserializationSchema')

        elif fmt == SerializationFormat.CONFLUENT_AVRO:
            imports.add('org.apache.flink.formats.avro.registry.confluent.ConfluentRegistryAvroDeserializationSchema')

        elif fmt == SerializationFormat.PROTOBUF:
            imports.add('org.apache.flink.formats.protobuf.ProtobufDeserializationSchema')

        return imports
