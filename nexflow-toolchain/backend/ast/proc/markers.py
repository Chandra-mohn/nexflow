# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Process AST Markers and Phases

AST nodes for EOD markers and phase-based execution control.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union, TYPE_CHECKING

from .common import SourceLocation
from .enums import PhaseType, MarkerConditionType

if TYPE_CHECKING:
    pass


@dataclass
class SignalCondition:
    """Marker condition: external signal received.

    Example: when trades_reconciled
    """
    signal_name: str
    condition_type: MarkerConditionType = field(default=MarkerConditionType.SIGNAL, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class MarkerRefCondition:
    """Marker condition: another marker completed.

    Example: when eod_1
    """
    marker_name: str
    condition_type: MarkerConditionType = field(default=MarkerConditionType.MARKER_REF, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class StreamDrainedCondition:
    """Marker condition: stream has no pending messages.

    Example: when trade_stream.drained
    """
    stream_name: str
    condition_type: MarkerConditionType = field(default=MarkerConditionType.STREAM_DRAINED, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class CountThresholdCondition:
    """Marker condition: message count threshold reached.

    Example: when trades.count >= 1000
    """
    stream_name: str
    operator: str  # '>=', '=', '>'
    threshold: int
    condition_type: MarkerConditionType = field(default=MarkerConditionType.COUNT_THRESHOLD, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class TimeBasedCondition:
    """Marker condition: time threshold reached.

    Example: after 18:00
    """
    time_spec: str  # "18:00", "end_of_day", etc.
    condition_type: MarkerConditionType = field(default=MarkerConditionType.TIME_BASED, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class ApiCheckCondition:
    """Marker condition: external service ready.

    Example: when api.risk_service.ready
    """
    api_name: str
    service_name: str
    check_name: str  # 'ready', 'healthy', etc.
    condition_type: MarkerConditionType = field(default=MarkerConditionType.API_CHECK, init=False)
    location: Optional[SourceLocation] = None


@dataclass
class CompoundCondition:
    """Marker condition: AND/OR of other conditions.

    Example: when eod_1 and risk_calculations_complete and margin_calls_sent
    """
    operator: str  # 'and', 'or'
    conditions: List['AnyMarkerCondition'] = field(default_factory=list)
    condition_type: MarkerConditionType = field(default=MarkerConditionType.COMPOUND, init=False)
    location: Optional[SourceLocation] = None


# Type alias for any marker condition
AnyMarkerCondition = Union[
    SignalCondition,
    MarkerRefCondition,
    StreamDrainedCondition,
    CountThresholdCondition,
    TimeBasedCondition,
    ApiCheckCondition,
    CompoundCondition,
]


@dataclass
class MarkerDef:
    """Definition of an EOD marker.

    Example:
        eod_1: when trades_reconciled
        eod_2: when eod_1 and risk_calculations_complete
    """
    name: str
    condition: AnyMarkerCondition
    location: Optional[SourceLocation] = None


@dataclass
class MarkersBlock:
    """Block containing marker definitions.

    Example:
        markers
            eod_1: when trades_reconciled
            eod_2: when eod_1 and risk_complete
            eod_3: when eod_2 and reports_filed
        end
    """
    markers: List[MarkerDef] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    def get_marker(self, name: str) -> Optional[MarkerDef]:
        """Get marker by name."""
        for marker in self.markers:
            if marker.name == name:
                return marker
        return None

    def marker_names(self) -> List[str]:
        """Get all marker names."""
        return [m.name for m in self.markers]


@dataclass
class OnCompleteClause:
    """Signal emission on phase completion.

    Example:
        on complete signal trades_reconciled
        on complete when error_count = 0 signal trades_reconciled
        signal rollover to trading_calendar
    """
    signal_name: str
    target: Optional[str] = None  # e.g., "trading_calendar" for rollover
    condition: Optional[str] = None  # Optional when condition expression
    location: Optional[SourceLocation] = None


@dataclass
class PhaseSpec:
    """Phase specification defining when a phase runs.

    Examples:
        phase before eod_1
        phase between eod_1 and eod_2
        phase after eod_3
        phase anytime
    """
    phase_type: PhaseType
    start_marker: Optional[str] = None  # For BETWEEN and AFTER
    end_marker: Optional[str] = None    # For BETWEEN and BEFORE
    location: Optional[SourceLocation] = None

    @classmethod
    def before(cls, marker: str, location: Optional[SourceLocation] = None) -> 'PhaseSpec':
        """Create a 'before marker' phase spec."""
        return cls(phase_type=PhaseType.BEFORE, end_marker=marker, location=location)

    @classmethod
    def between(cls, start: str, end: str, location: Optional[SourceLocation] = None) -> 'PhaseSpec':
        """Create a 'between markers' phase spec."""
        return cls(phase_type=PhaseType.BETWEEN, start_marker=start, end_marker=end, location=location)

    @classmethod
    def after(cls, marker: str, location: Optional[SourceLocation] = None) -> 'PhaseSpec':
        """Create an 'after marker' phase spec."""
        return cls(phase_type=PhaseType.AFTER, start_marker=marker, location=location)

    @classmethod
    def anytime(cls, location: Optional[SourceLocation] = None) -> 'PhaseSpec':
        """Create an 'anytime' phase spec."""
        return cls(phase_type=PhaseType.ANYTIME, location=location)


@dataclass
class PhaseBlock:
    """A phase block containing statements that execute within a phase.

    Example:
        phase before eod_1
            receive trades from trade_stream
                schema Trade
            transform using validate_trade
            emit validated_trades to validated_trade_stream
            on complete signal trades_reconciled
        end
    """
    spec: PhaseSpec
    # Statements within the phase (same types as process body)
    statements: List = field(default_factory=list)  # List of ReceiveDecl, TransformDecl, EmitDecl, etc.
    on_complete: List[OnCompleteClause] = field(default_factory=list)
    location: Optional[SourceLocation] = None


@dataclass
class BusinessDateDecl:
    """Business date calendar reference.

    Example: business_date from trading_calendar
    """
    calendar_name: str
    location: Optional[SourceLocation] = None


@dataclass
class ProcessingDateDecl:
    """Processing date declaration - system time when record is processed.

    Example: processing_date auto

    The processing date is automatically set to the system clock time
    when each record is processed by the streaming pipeline.
    """
    mode: str = "auto"  # Currently only 'auto' is supported
    location: Optional[SourceLocation] = None
