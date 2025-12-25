# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Configuration Module

Provides configuration resolution for Nexflow builds:
- Serialization format configuration (JSON, Avro, Protobuf)
- Hierarchical config loading from nexflow.toml files
- Environment-specific overlays
"""

from backend.config.serialization_resolver import (
    SerializationResolver,
    resolve_serialization,
)

__all__ = [
    "SerializationResolver",
    "resolve_serialization",
]
