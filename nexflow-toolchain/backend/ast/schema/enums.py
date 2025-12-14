"""
Schema AST Enumerations

Enum definitions for L2 Schema Registry DSL.
"""

from enum import Enum


class MutationPattern(Enum):
    MASTER_DATA = "master_data"
    IMMUTABLE_LEDGER = "immutable_ledger"
    VERSIONED_CONFIGURATION = "versioned_configuration"
    OPERATIONAL_PARAMETERS = "operational_parameters"
    EVENT_LOG = "event_log"
    STATE_MACHINE = "state_machine"
    TEMPORAL_DATA = "temporal_data"
    REFERENCE_DATA = "reference_data"
    BUSINESS_LOGIC = "business_logic"
    COMMAND = "command"
    RESPONSE = "response"
    AGGREGATE = "aggregate"
    DOCUMENT = "document"
    AUDIT_EVENT = "audit_event"


class CompatibilityMode(Enum):
    BACKWARD = "backward"
    FORWARD = "forward"
    FULL = "full"
    NONE = "none"


class TimeSemantics(Enum):
    EVENT_TIME = "event_time"
    PROCESSING_TIME = "processing_time"
    INGESTION_TIME = "ingestion_time"


class WatermarkStrategy(Enum):
    BOUNDED_OUT_OF_ORDERNESS = "bounded_out_of_orderness"
    PERIODIC = "periodic"
    PUNCTUATED = "punctuated"


class LateDataStrategy(Enum):
    SIDE_OUTPUT = "side_output"
    DROP = "drop"
    UPDATE = "update"


class IdleBehavior(Enum):
    MARK_IDLE = "mark_idle"
    ADVANCE_TO_INFINITY = "advance_to_infinity"
    KEEP_WAITING = "keep_waiting"


class RetentionPolicy(Enum):
    DELETE_OLDEST = "delete_oldest"
    ARCHIVE = "archive"
    COMPACT = "compact"


class BaseType(Enum):
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    UUID = "uuid"
    BYTES = "bytes"
    BIZDATE = "bizdate"  # Business date - validated against calendar


class FieldQualifierType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    PII = "pii"
    ENCRYPTED = "encrypted"
    INDEXED = "indexed"
    SENSITIVE = "sensitive"
    DEFAULT = "default"
