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
    location: Optional[SourceLocation] = None


@dataclass
class InputBlock:
    """Process input declarations."""
    receives: List[ReceiveDecl]
    location: Optional[SourceLocation] = None
