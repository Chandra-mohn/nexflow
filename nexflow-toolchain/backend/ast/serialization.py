# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Serialization Configuration AST

Defines AST classes for serialization format configuration.
Used by both SchemaDSL (schema-level declaration) and ProcDSL (process-level override).

Hierarchy:
1. Process-level override (in .proc file)
2. Schema-level declaration (in .schema file)
3. Team config (nexflow.toml)
4. Environment overlay (nexflow.{env}.toml)
5. Built-in default (json)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from backend.ast.common import SourceLocation


class SerializationFormat(Enum):
    """Supported Kafka serialization formats."""

    JSON = "json"
    AVRO = "avro"
    CONFLUENT_AVRO = "confluent_avro"
    PROTOBUF = "protobuf"

    @classmethod
    def from_string(cls, value: str) -> "SerializationFormat":
        """Convert string to SerializationFormat enum."""
        normalized = value.lower().strip()
        for fmt in cls:
            if fmt.value == normalized:
                return fmt
        raise ValueError(f"Unknown serialization format: {value}")


class CompatibilityMode(Enum):
    """Schema compatibility modes for schema registry."""

    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"
    NONE = "NONE"

    @classmethod
    def from_string(cls, value: str) -> "CompatibilityMode":
        """Convert string to CompatibilityMode enum."""
        normalized = value.upper().strip()
        # Handle aliases
        if normalized in ("BACKWARD_COMPATIBLE", "BACKWARD"):
            return cls.BACKWARD
        if normalized in ("FORWARD_COMPATIBLE", "FORWARD"):
            return cls.FORWARD
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Unknown compatibility mode: {value}")


@dataclass
class SerializationConfig:
    """
    Serialization configuration for a schema or connector.

    Can be declared at:
    - Schema level (in .schema file serialization block)
    - Connector level (format override in .proc file)
    - Config level (nexflow.toml)
    """

    format: SerializationFormat = SerializationFormat.JSON
    compatibility: Optional[CompatibilityMode] = None
    registry_url: Optional[str] = None
    subject: Optional[str] = None
    location: Optional[SourceLocation] = None

    def __post_init__(self):
        """Validate configuration."""
        # Avro formats require registry URL for full functionality
        if self.format in (
            SerializationFormat.AVRO,
            SerializationFormat.CONFLUENT_AVRO,
        ):
            if self.subject is None and self.registry_url:
                # Default subject naming will be applied at code generation
                pass

    @property
    def requires_registry(self) -> bool:
        """Check if this format requires a schema registry."""
        return self.format in (
            SerializationFormat.AVRO,
            SerializationFormat.CONFLUENT_AVRO,
        )

    @property
    def is_binary(self) -> bool:
        """Check if this format produces binary output."""
        return self.format != SerializationFormat.JSON

    def merge_with(self, other: Optional["SerializationConfig"]) -> "SerializationConfig":
        """
        Merge this config with another, with self taking priority.

        Used for hierarchical config resolution:
        process_override.merge_with(schema_config).merge_with(team_config)
        """
        if other is None:
            return self

        return SerializationConfig(
            format=self.format,  # Self always wins for format
            compatibility=self.compatibility or other.compatibility,
            registry_url=self.registry_url or other.registry_url,
            subject=self.subject or other.subject,
            location=self.location,
        )


@dataclass
class RegistryConfig:
    """
    Schema Registry configuration.

    Loaded from nexflow.toml [serialization.registry] section.
    """

    url: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    ssl_enabled: bool = True
    cache_capacity: int = 1000

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryConfig":
        """Create from dictionary (TOML config)."""
        return cls(
            url=data.get("url", ""),
            api_key=data.get("api_key"),
            api_secret=data.get("api_secret"),
            ssl_enabled=data.get("ssl_enabled", True),
            cache_capacity=data.get("cache_capacity", 1000),
        )


@dataclass
class GlobalSerializationConfig:
    """
    Global serialization configuration loaded from nexflow.toml.

    Represents the [serialization] section of the config file.
    """

    default_format: SerializationFormat = SerializationFormat.JSON
    registry: Optional[RegistryConfig] = None
    avro_compatibility: CompatibilityMode = CompatibilityMode.BACKWARD
    avro_subject_naming: str = "TopicNameStrategy"
    avro_use_logical_types: bool = True
    protobuf_include_default_values: bool = False
    protobuf_use_proto3: bool = True
    json_include_null_fields: bool = False
    json_date_format: str = "ISO8601"

    @classmethod
    def from_dict(cls, data: dict) -> "GlobalSerializationConfig":
        """Create from dictionary (TOML config)."""
        config = cls()

        if "default_format" in data:
            config.default_format = SerializationFormat.from_string(data["default_format"])

        if "registry" in data:
            config.registry = RegistryConfig.from_dict(data["registry"])

        avro_section = data.get("avro", {})
        if "compatibility" in avro_section:
            config.avro_compatibility = CompatibilityMode.from_string(
                avro_section["compatibility"]
            )
        if "subject_naming" in avro_section:
            config.avro_subject_naming = avro_section["subject_naming"]
        if "use_logical_types" in avro_section:
            config.avro_use_logical_types = avro_section["use_logical_types"]

        protobuf_section = data.get("protobuf", {})
        if "include_default_values" in protobuf_section:
            config.protobuf_include_default_values = protobuf_section[
                "include_default_values"
            ]
        if "use_proto3" in protobuf_section:
            config.protobuf_use_proto3 = protobuf_section["use_proto3"]

        json_section = data.get("json", {})
        if "include_null_fields" in json_section:
            config.json_include_null_fields = json_section["include_null_fields"]
        if "date_format" in json_section:
            config.json_date_format = json_section["date_format"]

        return config

    def get_effective_config(
        self,
        schema_config: Optional[SerializationConfig] = None,
        process_override: Optional[SerializationConfig] = None,
    ) -> SerializationConfig:
        """
        Resolve effective serialization config using hierarchy.

        Priority: process_override > schema_config > global_config
        """
        # Start with global defaults
        effective = SerializationConfig(
            format=self.default_format,
            compatibility=self.avro_compatibility,
            registry_url=self.registry.url if self.registry else None,
        )

        # Merge schema-level config
        if schema_config:
            effective = schema_config.merge_with(effective)

        # Merge process-level override (highest priority)
        if process_override:
            effective = process_override.merge_with(effective)

        return effective
