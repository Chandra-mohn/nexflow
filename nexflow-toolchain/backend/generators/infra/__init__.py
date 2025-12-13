"""
L5 Infrastructure Generator

Provides binding resolution and infrastructure-aware code generation.
"""

from .binding_resolver import (
    BindingResolver,
    BindingError,
    ResolvedKafkaSource,
    ResolvedKafkaSink,
    ResolvedMongoDBPersistence,
    ResolvedResources,
)

__all__ = [
    "BindingResolver",
    "BindingError",
    "ResolvedKafkaSource",
    "ResolvedKafkaSink",
    "ResolvedMongoDBPersistence",
    "ResolvedResources",
]
