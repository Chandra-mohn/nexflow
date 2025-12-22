# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Input Block

Input-related dataclasses for process AST.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from .common import SourceLocation


class ConnectorType(Enum):
    """Supported source connector types."""
    KAFKA = "kafka"
    REDIS = "redis"
    STATE_STORE = "state_store"
    MONGODB = "mongodb"
    SCHEDULER = "scheduler"
    PARQUET = "parquet"        # v0.8.0+: Parquet file source
    CSV = "csv"                # v0.8.0+: CSV file source


@dataclass
class SchemaDecl:
    """Schema reference declaration."""
    schema_name: str
    location: Optional[SourceLocation] = None


@dataclass
class ProjectClause:
    """Field projection clause."""
    fields: List[str]
    is_except: bool = False
    location: Optional[SourceLocation] = None


@dataclass
class StoreAction:
    """Store in state action."""
    state_name: str
    location: Optional[SourceLocation] = None


@dataclass
class MatchAction:
    """Match from state action."""
    state_name: str
    on_fields: List[str]
    location: Optional[SourceLocation] = None


@dataclass
class RedisConfig:
    """Redis-specific configuration."""
    pattern: str  # Redis key pattern (e.g., "user:*", "cache:events:*")
    mode: str = "subscribe"  # subscribe, scan, stream
    batch_size: int = 100
    location: Optional[SourceLocation] = None


@dataclass
class StateStoreConfig:
    """State store-specific configuration."""
    store_name: str
    key_type: Optional[str] = None
    value_type: Optional[str] = None
    location: Optional[SourceLocation] = None


@dataclass
class SchedulerConfig:
    """Scheduler-specific configuration."""
    cron_expression: str
    timezone: str = "UTC"
    location: Optional[SourceLocation] = None


@dataclass
class TimestampBounds:
    """Timestamp bounds for bounded reads (v0.8.0+).

    Used for:
    - Kafka: Read from specific time range
    - Parquet: Filter by timestamp column
    """
    from_timestamp: Optional[str] = None  # ISO8601 format: "2024-01-01T00:00:00Z"
    to_timestamp: Optional[str] = None    # ISO8601 format: "2024-12-31T23:59:59Z"
    location: Optional[SourceLocation] = None


@dataclass
class ParquetConfig:
    """Parquet-specific configuration (v0.8.0+)."""
    path: str                                  # File path or glob pattern
    partition_columns: Optional[List[str]] = None  # Partition columns
    schema_path: Optional[str] = None          # External schema file path
    timestamp_bounds: Optional[TimestampBounds] = None
    location: Optional[SourceLocation] = None


@dataclass
class CsvConfig:
    """CSV-specific configuration (v0.8.0+)."""
    path: str                                  # File path or glob pattern
    delimiter: str = ","                       # Field delimiter
    quote_char: str = '"'                      # Quote character
    escape_char: str = "\\"                    # Escape character
    has_header: bool = True                    # First row is header
    null_value: str = ""                       # Null representation
    timestamp_bounds: Optional[TimestampBounds] = None
    location: Optional[SourceLocation] = None


@dataclass
class ReceiveDecl:
    """Input receive declaration."""
    source: str
    connector_type: ConnectorType = ConnectorType.KAFKA
    alias: Optional[str] = None
    schema: Optional[SchemaDecl] = None
    project: Optional[ProjectClause] = None
    store_action: Optional[StoreAction] = None
    match_action: Optional[MatchAction] = None
    redis_config: Optional[RedisConfig] = None
    state_store_config: Optional[StateStoreConfig] = None
    scheduler_config: Optional[SchedulerConfig] = None
    parquet_config: Optional[ParquetConfig] = None  # v0.8.0+
    csv_config: Optional[CsvConfig] = None          # v0.8.0+
    timestamp_bounds: Optional[TimestampBounds] = None  # v0.8.0+: For Kafka bounded reads
    location: Optional[SourceLocation] = None


@dataclass
class InputBlock:
    """Process input declarations."""
    receives: List[ReceiveDecl]
    location: Optional[SourceLocation] = None
