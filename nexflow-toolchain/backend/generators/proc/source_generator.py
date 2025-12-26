# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Source Generator Mixin (Backward Compatibility)

This module re-exports SourceGeneratorMixin from the modular sources package.
The implementation has been refactored into focused sub-modules:

- sources/kafka_source.py: Kafka source connectors
- sources/alternative_sources.py: Redis, StateStore, MongoDB, Scheduler
- sources/file_sources.py: Parquet, CSV file sources
- sources/serialization.py: Format detection and deserializer generation
- sources/dispatcher.py: main source routing dispatcher

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
"""

from backend.generators.proc.sources import SourceGeneratorMixin

__all__ = ['SourceGeneratorMixin']
