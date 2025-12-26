# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Message Decoder Module

Decodes binary-serialized Kafka messages (Avro, Protobuf, Confluent Avro) to JSON.
Supports both online (schema registry) and offline (local schema files) modes.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

from backend.ast.serialization import SerializationFormat


class DecodingError(Exception):
    """Error during message decoding."""
    pass


@dataclass
class DecodedMessage:
    """A decoded Kafka message."""
    offset: int
    partition: int
    timestamp: Optional[int]
    timestamp_type: Optional[str]
    key: Optional[Any]
    value: Any
    headers: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'offset': self.offset,
            'partition': self.partition,
            'timestamp': self.timestamp,
            'timestamp_type': self.timestamp_type,
            'key': self.key,
            'value': self.value,
            'headers': self.headers,
        }


class Decoder(ABC):
    """Abstract base class for message decoders."""

    @abstractmethod
    def decode(self, data: bytes) -> Any:
        """Decode binary data to Python object."""
        pass

    @abstractmethod
    def get_format(self) -> SerializationFormat:
        """Get the serialization format this decoder handles."""
        pass


class JsonDecoder(Decoder):
    """Decoder for JSON-serialized messages."""

    def decode(self, data: bytes) -> Any:
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise DecodingError(f"Failed to decode JSON: {e}")

    def get_format(self) -> SerializationFormat:
        return SerializationFormat.JSON


class AvroDecoder(Decoder):
    """Decoder for Avro-serialized messages (local schema file)."""

    def __init__(self, schema_path: Optional[Path] = None, schema_str: Optional[str] = None):
        try:
            import fastavro
            from fastavro.schema import parse_schema
        except ImportError:
            raise DecodingError("fastavro is required for Avro decoding. "
                              "Install with: pip install fastavro")

        self._fastavro = fastavro

        if schema_path:
            with open(schema_path, 'r') as f:
                schema_str = f.read()

        if not schema_str:
            raise DecodingError("Schema required for Avro decoding")

        self._schema = parse_schema(json.loads(schema_str))

    def decode(self, data: bytes) -> Any:
        import io
        try:
            reader = self._fastavro.reader(io.BytesIO(data), self._schema)
            records = list(reader)
            return records[0] if len(records) == 1 else records
        except Exception as e:
            raise DecodingError(f"Failed to decode Avro: {e}")

    def get_format(self) -> SerializationFormat:
        return SerializationFormat.AVRO


class ConfluentAvroDecoder(Decoder):
    """Decoder for Confluent Avro-serialized messages (schema registry)."""

    def __init__(self, registry_url: str, registry_config: Optional[Dict[str, Any]] = None):
        try:
            from confluent_kafka.schema_registry import SchemaRegistryClient
            from confluent_kafka.schema_registry.avro import AvroDeserializer
        except ImportError:
            raise DecodingError("confluent-kafka is required for Confluent Avro decoding. "
                              "Install with: pip install confluent-kafka[avro]")

        config = {'url': registry_url}
        if registry_config:
            config.update(registry_config)

        self._registry = SchemaRegistryClient(config)
        self._deserializers: Dict[int, Any] = {}

    def decode(self, data: bytes) -> Any:
        from confluent_kafka.schema_registry.avro import AvroDeserializer

        if len(data) < 5:
            raise DecodingError("Invalid Confluent Avro message: too short")

        # Confluent wire format: magic byte (0) + 4-byte schema ID + Avro data
        if data[0] != 0:
            raise DecodingError(f"Invalid Confluent Avro magic byte: {data[0]}")

        schema_id = int.from_bytes(data[1:5], 'big')

        # Cache deserializers by schema ID
        if schema_id not in self._deserializers:
            schema = self._registry.get_schema(schema_id)
            self._deserializers[schema_id] = AvroDeserializer(
                self._registry,
                schema.schema_str
            )

        deserializer = self._deserializers[schema_id]

        try:
            # AvroDeserializer expects the full message including magic byte
            return deserializer(data, None)
        except Exception as e:
            raise DecodingError(f"Failed to decode Confluent Avro: {e}")

    def get_format(self) -> SerializationFormat:
        return SerializationFormat.CONFLUENT_AVRO


class ProtobufDecoder(Decoder):
    """Decoder for Protobuf-serialized messages."""

    def __init__(self, proto_path: Path, message_type: str):
        try:
            from google.protobuf import descriptor_pb2
            from google.protobuf.descriptor_pool import DescriptorPool
            from google.protobuf.message_factory import MessageFactory
        except ImportError:
            raise DecodingError("protobuf is required for Protobuf decoding. "
                              "Install with: pip install protobuf")

        # For full protobuf support, we'd need to compile .proto files
        # For now, this is a simplified implementation that requires compiled descriptors
        self._proto_path = proto_path
        self._message_type = message_type
        self._message_class = self._load_message_class()

    def _load_message_class(self):
        """Load the protobuf message class from the proto file."""
        # This is a simplified implementation
        # In production, you'd want to use grpcio-tools to compile .proto files
        raise DecodingError("Protobuf decoding requires pre-compiled message classes. "
                          "Use 'protoc' to generate Python classes from .proto files.")

    def decode(self, data: bytes) -> Any:
        try:
            message = self._message_class()
            message.ParseFromString(data)
            # Convert to dict using MessageToDict
            from google.protobuf.json_format import MessageToDict
            return MessageToDict(message)
        except Exception as e:
            raise DecodingError(f"Failed to decode Protobuf: {e}")

    def get_format(self) -> SerializationFormat:
        return SerializationFormat.PROTOBUF


class MessageDecoder:
    """
    High-level message decoder that auto-detects format and handles
    both online (schema registry) and offline (local schema) modes.
    """

    def __init__(
        self,
        format: Optional[SerializationFormat] = None,
        schema_path: Optional[Path] = None,
        registry_url: Optional[str] = None,
        registry_config: Optional[Dict[str, Any]] = None,
    ):
        self.format = format
        self.schema_path = schema_path
        self.registry_url = registry_url
        self.registry_config = registry_config
        self._decoder: Optional[Decoder] = None

    def _get_decoder(self, data: bytes) -> Decoder:
        """Get or create the appropriate decoder."""
        if self._decoder:
            return self._decoder

        fmt = self.format or self._detect_format(data)

        if fmt == SerializationFormat.JSON:
            self._decoder = JsonDecoder()
        elif fmt == SerializationFormat.AVRO:
            if not self.schema_path:
                raise DecodingError("Schema file required for Avro decoding in offline mode")
            self._decoder = AvroDecoder(schema_path=self.schema_path)
        elif fmt == SerializationFormat.CONFLUENT_AVRO:
            if not self.registry_url:
                raise DecodingError("Schema registry URL required for Confluent Avro decoding")
            self._decoder = ConfluentAvroDecoder(
                registry_url=self.registry_url,
                registry_config=self.registry_config,
            )
        elif fmt == SerializationFormat.PROTOBUF:
            raise DecodingError("Protobuf decoding requires compiled message classes. "
                              "Provide a schema file or pre-compiled protobuf module.")
        else:
            raise DecodingError(f"Unsupported format: {fmt}")

        return self._decoder

    def _detect_format(self, data: bytes) -> SerializationFormat:
        """Auto-detect message format from data."""
        if not data:
            raise DecodingError("Empty message data")

        # Check for Confluent Avro wire format (starts with 0x00)
        if data[0] == 0 and len(data) >= 5:
            return SerializationFormat.CONFLUENT_AVRO

        # Try JSON detection
        try:
            if data[0] in (0x7b, 0x5b):  # '{' or '['
                json.loads(data.decode('utf-8'))
                return SerializationFormat.JSON
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

        # Check for Avro magic bytes (Obj + version byte)
        if data[:4] == b'Obj\x01':
            return SerializationFormat.AVRO

        # Default to JSON as fallback
        return SerializationFormat.JSON

    def decode(self, data: bytes) -> Any:
        """Decode message data."""
        decoder = self._get_decoder(data)
        return decoder.decode(data)

    def decode_message(
        self,
        data: bytes,
        offset: int,
        partition: int,
        timestamp: Optional[int] = None,
        timestamp_type: Optional[str] = None,
        key: Optional[bytes] = None,
        headers: Optional[list] = None,
    ) -> DecodedMessage:
        """Decode a complete Kafka message with metadata."""
        value = self.decode(data)

        # Try to decode key as string
        decoded_key = None
        if key:
            try:
                decoded_key = key.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                decoded_key = key.hex() if isinstance(key, bytes) else str(key)

        # Convert headers to dict
        decoded_headers = None
        if headers:
            decoded_headers = {}
            for h_key, h_value in headers:
                try:
                    decoded_headers[h_key] = h_value.decode('utf-8') if h_value else None
                except (UnicodeDecodeError, AttributeError):
                    decoded_headers[h_key] = h_value.hex() if isinstance(h_value, bytes) else str(h_value)

        return DecodedMessage(
            offset=offset,
            partition=partition,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            key=decoded_key,
            value=value,
            headers=decoded_headers,
        )
