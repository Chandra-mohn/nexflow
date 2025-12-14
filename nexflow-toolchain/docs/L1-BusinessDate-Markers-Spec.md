# L1 Enhancement: Business Date & EOD Markers

## Overview

This specification defines two interconnected L1 Flow enhancements:

1. **Business Date Context** - Calendar-aware processing with API-backed date resolution
2. **EOD Markers & Phases** - Processing gates that control execution order within a business day

## Motivation

Enterprise batch and streaming processes operate on **business calendars**, not system time:

- Business date may differ from system date (e.g., Saturday 2am is still Friday's business day)
- Certain processes can only run after specific conditions are met (EOD markers)
- Processing schedules respect holidays and non-processing days
- Calendar logic should be centralized, not embedded in each flow

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RUNTIME ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐                      ┌─────────────────────────┐  │
│  │   Nexflow DSL   │                      │   Calendar Service      │  │
│  │                 │                      │   (External API)        │  │
│  │  process foo    │                      │                         │  │
│  │    business_date│───── references ────►│  - Current biz date     │  │
│  │      from cal   │                      │  - Holiday lookups      │  │
│  │    markers ...  │                      │  - Date arithmetic      │  │
│  │    phase ...    │                      │  - Rollover signals     │  │
│  └────────┬────────┘                      └────────────▲────────────┘  │
│           │                                            │               │
│           │ generates                                  │ API calls     │
│           ▼                                            │               │
│  ┌─────────────────┐                      ┌────────────┴────────────┐  │
│  │  Flink Job      │                      │   CalendarClient        │  │
│  │                 │──── uses ───────────►│   (Generated)           │  │
│  │  - MarkerState  │                      │                         │  │
│  │  - PhaseGating  │                      │   - Caching             │  │
│  │  - BizDateScope │                      │   - Circuit breaker     │  │
│  └─────────────────┘                      └─────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Part 1: Business Date Context

### Concept

Business date is the **logical processing day**, which may differ from the calendar date:

| System Time | Business Date | Reason |
|-------------|---------------|--------|
| Sat Dec 14, 02:30 | Fri Dec 13 | EOD not yet complete |
| Sun Dec 15, 06:00 | Sun Dec 15 | New business day started |
| Mon Dec 16, 00:01 | Sun Dec 15 | EOD not yet complete |
| Dec 25, 10:00 | Dec 24 | Holiday - no processing |

### L5 Infrastructure: API Reference

Business date is resolved via external API, not embedded in L5:

```yaml
# production.infra
version: "1.0"
environment: production

calendar:
  # Service discovery name (for K8s/service mesh)
  service: calendar-service

  # Direct endpoint (fallback or for local dev)
  endpoint: ${CALENDAR_API_URL:http://calendar-api:8080}

  # Which calendar this environment uses
  name: trading_calendar

  # Local cache settings (reduce API calls)
  cache:
    ttl: 300s                    # Cache business date for 5 minutes
    refresh_on_phase: true       # Refresh after each phase transition

  # Circuit breaker for API failures
  fallback:
    strategy: last_known         # Use last cached value
    max_stale: 1h                # Maximum staleness allowed
    alert_channel: ops-critical  # Alert on fallback activation
```

### L1 Syntax: Business Date Declaration

```
process daily_settlement
    # Declare which calendar this process uses
    business_date from trading_calendar

    # All date references in this process are calendar-aware
    receive trades from trade_stream
        where trade.effective_date = current_business_date

    transform using calculate_settlement

    emit to settlement_instructions
end
```

### Built-in Functions (API-Backed)

| Function | Description | Example |
|----------|-------------|---------|
| `current_business_date` | Current business date from calendar | `where date = current_business_date` |
| `previous_business_date` | T-1 business date | `lookup prior_close at previous_business_date` |
| `next_business_date` | T+1 business date | `settlement_date = next_business_date` |
| `add_business_days(date, n)` | Add/subtract business days | `add_business_days(trade_date, 2)` |
| `is_business_day(date)` | Check if date is processing day | `when is_business_day(event_date)` |
| `is_holiday(date)` | Check if date is a holiday | `when not is_holiday(settlement_date)` |

### L2 Schema: Business Date Type

```
pattern Trade version 1.0.0
    identity by trade_id

    fields
        trade_id: string required
        symbol: string required
        quantity: decimal required
        price: decimal required

        # Business date type - validated against calendar
        trade_date: bizdate required
        settlement_date: bizdate

        # Regular timestamp for audit
        execution_timestamp: timestamp required
    end
end
```

The `bizdate` type:
- Stored as `LocalDate` in Java
- Validated against calendar (must be a valid business day, unless explicitly allowed)
- Supports business day arithmetic

### L3 Transform: Calendar-Aware Operations

```
transform calculate_settlement
    input: Trade
    output: SettlementInstruction

    map
        trade_id = input.trade_id
        trade_date = input.trade_date

        # T+2 settlement using calendar
        settlement_date = add_business_days(input.trade_date, 2)

        # Lookup previous day's closing price
        prior_close = lookup closing_prices
            at previous_business_date
            key input.symbol

        # Mark if settling on a different month
        cross_month = settlement_date.month != trade_date.month
    end
end
```

---

## Part 2: EOD Markers & Phases

### Concept

EOD (End of Day) Markers are **named checkpoints** that represent business conditions being satisfied. Phases are **execution windows** bounded by markers.

```
Business Day Timeline:

  START ─────┬───────────┬───────────┬─────────► ROLLOVER
             │           │           │
           EOD_1       EOD_2       EOD_3
             │           │           │
    ┌────────┴──┐   ┌────┴────┐   ┌──┴────────┐
    │ Phase 1   │   │ Phase 2 │   │ Phase 3   │
    │           │   │         │   │           │
    │ - Trade   │   │ - Risk  │   │ - Reports │
    │   capture │   │   calc  │   │ - Filing  │
    │ - Recon   │   │ - Margin│   │ - Archive │
    └───────────┘   └─────────┘   └───────────┘

    ──────────────── Anytime Processes ────────────────
    │ - Audit logging                                 │
    │ - Monitoring                                    │
    │ - Alerting                                      │
    ──────────────────────────────────────────────────
```

### L1 Syntax: Markers Definition

```
process daily_settlement
    business_date from trading_calendar

    # Define markers with their completion conditions
    markers
        # Simple condition
        eod_1: when trades_reconciled

        # Compound condition with dependency
        eod_2: when eod_1
                and risk_calculations_complete
                and margin_calls_sent

        # Final marker triggers rollover
        eod_3: when eod_2
                and regulatory_reports_filed
                and archives_complete
    end

    # ... phases defined below
end
```

### Marker Conditions

Markers can depend on:

| Condition Type | Syntax | Description |
|----------------|--------|-------------|
| Signal received | `signal_name` | External signal received |
| Prior marker | `eod_1` | Another marker completed |
| Stream drained | `stream_name.drained` | No pending messages |
| Count threshold | `trades.count >= 1000` | Message count condition |
| Time-based | `after 18:00` | Time threshold (use sparingly) |
| API check | `api.risk_service.ready` | External service ready |

### L1 Syntax: Phase Definition

```
process daily_settlement
    business_date from trading_calendar

    markers
        eod_1: when trades_reconciled
        eod_2: when eod_1 and risk_complete
        eod_3: when eod_2 and reports_filed
    end

    # Processes that must complete BEFORE eod_1
    phase before eod_1
        receive trades from trade_stream
            schema Trade
            where trade.business_date = current_business_date

        transform using validate_trade
        transform using enrich_trade

        emit validated_trades to validated_trade_stream

        # Signal completion (contributes to eod_1 condition)
        on complete signal trades_reconciled
    end

    # Processes that run BETWEEN eod_1 and eod_2
    phase between eod_1 and eod_2
        receive validated from validated_trade_stream
            schema ValidatedTrade

        transform using calculate_risk
        transform using compute_margin

        emit to risk_results

        on complete signal risk_calculations_complete
    end

    # Processes that run BETWEEN eod_2 and eod_3
    phase between eod_2 and eod_3
        receive results from risk_results
            schema RiskResult

        transform using generate_reports

        persist to regulatory_archive
        emit to report_distribution

        on complete signal regulatory_reports_filed
    end

    # Processes that run AFTER all markers (cleanup, rollover)
    phase after eod_3
        # Signal calendar service to roll to next business date
        signal rollover to trading_calendar

        # Archive and cleanup
        emit day_complete to audit_stream
    end

    # Processes that run continuously, independent of markers
    phase anytime
        receive events from audit_event_stream
            schema AuditEvent

        transform using enrich_audit
        persist to audit_database
    end
end
```

### Phase Types

| Phase | Syntax | Behavior |
|-------|--------|----------|
| Before marker | `phase before eod_1` | Runs until marker fires |
| Between markers | `phase between eod_1 and eod_2` | Waits for first, stops at second |
| After marker | `phase after eod_3` | Starts after marker, runs once |
| Anytime | `phase anytime` | Runs continuously, ignores markers |

### Signals

Signals are the mechanism for communicating marker conditions:

```
# Emit a signal when phase completes
on complete signal trades_reconciled

# Emit a signal conditionally
on complete when error_count = 0 signal trades_reconciled

# Emit signal to external system (calendar rollover)
signal rollover to trading_calendar
```

---

## Part 3: Generated Code Architecture

### Marker State Management

```java
// Generated: MarkerStateManager.java
public class MarkerStateManager {

    // Flink state for marker completion
    private final ValueState<MarkerState> markerState;

    // Marker definitions from DSL
    private final Map<String, MarkerCondition> markerConditions = Map.of(
        "eod_1", new SignalCondition("trades_reconciled"),
        "eod_2", new CompoundCondition(
            new MarkerCondition("eod_1"),
            new SignalCondition("risk_calculations_complete")
        ),
        "eod_3", new CompoundCondition(
            new MarkerCondition("eod_2"),
            new SignalCondition("regulatory_reports_filed")
        )
    );

    public boolean isMarkerComplete(String markerName) {
        return markerState.value().isComplete(markerName);
    }

    public void onSignalReceived(String signalName) {
        MarkerState state = markerState.value();
        state.recordSignal(signalName);

        // Check if any markers are now satisfied
        for (var entry : markerConditions.entrySet()) {
            if (!state.isComplete(entry.getKey())
                && entry.getValue().isSatisfied(state)) {
                state.markComplete(entry.getKey());
                emitMarkerEvent(entry.getKey());
            }
        }

        markerState.update(state);
    }
}
```

### Phase Gating Operator

```java
// Generated: PhaseGatingOperator.java
public class PhaseGatingOperator<T> extends KeyedProcessFunction<String, T, T> {

    private final String phaseName;
    private final String startMarker;  // null for "before" phases
    private final String endMarker;    // null for "after" phases
    private final MarkerStateManager markerManager;

    // Buffer for messages received before phase is active
    private final ListState<T> pendingMessages;

    @Override
    public void processElement(T value, Context ctx, Collector<T> out) {
        if (isPhaseActive()) {
            out.collect(value);
        } else if (isPhaseUpcoming()) {
            // Buffer until phase starts
            pendingMessages.add(value);
        }
        // else: phase already ended, drop or route to dead letter
    }

    private boolean isPhaseActive() {
        boolean afterStart = startMarker == null
            || markerManager.isMarkerComplete(startMarker);
        boolean beforeEnd = endMarker == null
            || !markerManager.isMarkerComplete(endMarker);
        return afterStart && beforeEnd;
    }

    // Called when marker state changes
    public void onMarkerComplete(String markerName) {
        if (markerName.equals(startMarker)) {
            // Phase just became active, flush pending messages
            for (T msg : pendingMessages.get()) {
                output.collect(msg);
            }
            pendingMessages.clear();
        }
    }
}
```

### Calendar Client (API Integration)

```java
// Generated: CalendarClient.java
public class CalendarClient implements Serializable {

    private final String calendarName;
    private final String endpoint;
    private final Duration cacheTtl;

    // Thread-safe cache
    private transient LoadingCache<String, BusinessDateInfo> cache;

    @PostConstruct
    public void init() {
        this.cache = Caffeine.newBuilder()
            .expireAfterWrite(cacheTtl)
            .build(this::fetchFromApi);
    }

    public LocalDate getCurrentBusinessDate() {
        return cache.get("current").getBusinessDate();
    }

    public LocalDate addBusinessDays(LocalDate from, int days) {
        String cacheKey = "add:" + from + ":" + days;
        return cache.get(cacheKey, k -> {
            return webClient.get()
                .uri(endpoint + "/calendars/{name}/add-business-days", calendarName)
                .queryParam("from_date", from)
                .queryParam("days", days)
                .retrieve()
                .bodyToMono(DateResult.class)
                .block()
                .getResultDate();
        });
    }

    public void signalRollover(String trigger) {
        webClient.post()
            .uri(endpoint + "/calendars/{name}/rollover", calendarName)
            .bodyValue(Map.of(
                "current_business_date", getCurrentBusinessDate(),
                "triggered_by", trigger
            ))
            .retrieve()
            .toBodilessEntity()
            .block();
    }

    // Circuit breaker fallback
    @CircuitBreaker(name = "calendar", fallbackMethod = "fallbackCurrentDate")
    private BusinessDateInfo fetchFromApi(String key) {
        // API call implementation
    }

    private BusinessDateInfo fallbackCurrentDate(String key, Exception ex) {
        log.warn("Calendar API unavailable, using fallback");
        // Return last known value or conservative default
    }
}
```

---

## Part 4: Grammar Changes

### L1 Flow Grammar Additions

```antlr
// proc.g4 additions

processDecl
    : PROCESS IDENTIFIER processConfig* processBody END
    ;

processConfig
    : parallelismClause
    | partitionClause
    | timeClause
    | modeClause
    | businessDateClause    // NEW
    | markersBlock          // NEW
    ;

// Business date reference
businessDateClause
    : BUSINESS_DATE FROM IDENTIFIER
    ;

// Markers block
markersBlock
    : MARKERS markerDef+ END
    ;

markerDef
    : IDENTIFIER COLON WHEN markerCondition
    ;

markerCondition
    : markerCondition AND markerCondition
    | markerCondition OR markerCondition
    | IDENTIFIER                           // signal name or marker reference
    | IDENTIFIER DOT DRAINED              // stream drained
    | AFTER timeSpec                       // time-based
    | LPAREN markerCondition RPAREN
    ;

// Phase blocks replace simple receive/transform/emit
processBody
    : phaseBlock+
    | statement+           // backward compatible: no phases = anytime
    ;

phaseBlock
    : PHASE phaseSpec statement+ (onCompleteClause)? END
    ;

phaseSpec
    : BEFORE IDENTIFIER                    // before eod_1
    | BETWEEN IDENTIFIER AND IDENTIFIER    // between eod_1 and eod_2
    | AFTER IDENTIFIER                     // after eod_3
    | ANYTIME                              // always running
    ;

onCompleteClause
    : ON COMPLETE (WHEN expression)? SIGNAL IDENTIFIER (TO IDENTIFIER)?
    ;

// New keywords
BUSINESS_DATE : 'business_date' ;
MARKERS : 'markers' ;
PHASE : 'phase' ;
BEFORE : 'before' ;
BETWEEN : 'between' ;
AFTER : 'after' ;
ANYTIME : 'anytime' ;
SIGNAL : 'signal' ;
DRAINED : 'drained' ;
ON : 'on' ;
COMPLETE : 'complete' ;
```

---

## Part 5: Implementation Plan

### Phase 1: Calendar API Integration (L5 + Runtime)

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Add calendar config to L5 AST | Small |
| 1.2 | Extend infra parser for calendar block | Small |
| 1.3 | Create CalendarClient base class | Medium |
| 1.4 | Add caching and circuit breaker | Medium |
| 1.5 | Generate CalendarClient in flow generator | Medium |
| 1.6 | Unit tests with mock calendar API | Medium |

**Deliverable**: Flows can reference calendar and call `current_business_date`

### Phase 2: Business Date Type (L2)

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Add `bizdate` to schema type system | Small |
| 2.2 | Generate `LocalDate` fields for bizdate | Small |
| 2.3 | Add calendar validation annotations | Small |
| 2.4 | Unit tests | Small |

**Deliverable**: Schemas can declare `bizdate` fields

### Phase 3: Calendar Functions (L3)

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Add calendar functions to L3 expression language | Medium |
| 3.2 | Generate CalendarClient calls in transforms | Medium |
| 3.3 | Handle caching in streaming context | Medium |
| 3.4 | Unit tests | Medium |

**Deliverable**: Transforms can use `add_business_days()`, etc.

### Phase 4: Markers & Phases (L1)

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Extend L1 grammar for markers/phases | Medium |
| 4.2 | Add AST models for markers/phases | Medium |
| 4.3 | Create MarkerStateManager | Large |
| 4.4 | Create PhaseGatingOperator | Large |
| 4.5 | Generate marker/phase Flink code | Large |
| 4.6 | Signal emission to calendar API | Medium |
| 4.7 | Integration tests | Large |

**Deliverable**: Full markers and phases functionality

### Phase 5: L4 Rules Integration

| Task | Description | Effort |
|------|-------------|--------|
| 5.1 | Add business date functions to L4 | Small |
| 5.2 | Add marker state checks to L4 | Small |
| 5.3 | Unit tests | Small |

**Deliverable**: Rules can check `is_business_day()` and marker states

---

## Example: Complete Daily Settlement Process

```
process daily_settlement
    parallelism hint 4
    partition by account_id
    business_date from trading_calendar
    mode stream

    markers
        eod_1: when trades_validated and positions_reconciled
        eod_2: when eod_1 and risk_aggregated and margin_calculated
        eod_3: when eod_2 and reports_generated and files_archived
    end

    phase before eod_1
        receive trades from raw_trade_stream
            schema Trade
            where trade.trade_date = current_business_date

        apply rules trade_validation_rules

        transform using enrich_trade
            with
                prior_close = lookup closing_prices
                    at previous_business_date
                    key trade.symbol

        emit to validated_trade_stream
            schema ValidatedTrade

        on complete signal trades_validated
    end

    phase before eod_1
        receive positions from position_stream
            schema Position
            where position.as_of_date = current_business_date

        transform using reconcile_positions

        emit to reconciled_positions
            schema ReconciledPosition

        on complete signal positions_reconciled
    end

    phase between eod_1 and eod_2
        receive validated from validated_trade_stream
            schema ValidatedTrade

        transform using aggregate_risk
        transform using calculate_margin

        emit to risk_stream
            schema RiskMetrics

        on complete signal risk_aggregated
        on complete signal margin_calculated
    end

    phase between eod_2 and eod_3
        receive risk from risk_stream
            schema RiskMetrics

        transform using generate_regulatory_report

        persist to report_archive
            collection regulatory_reports

        emit to distribution_stream

        on complete signal reports_generated
        on complete signal files_archived
    end

    phase after eod_3
        signal rollover to trading_calendar

        emit to audit_stream
            value {
                business_date: current_business_date,
                completed_at: now(),
                status: "success"
            }
    end

    phase anytime
        receive audit_events from internal_audit_stream
            schema AuditEvent

        transform using enrich_audit

        persist to audit_database
            collection audit_log
    end
end
```

---

## Calendar Service API Specification

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/calendars/{name}/current` | Get current business date |
| GET | `/calendars/{name}/is-business-day` | Check if date is business day |
| GET | `/calendars/{name}/add-days` | Business day arithmetic |
| GET | `/calendars/{name}/range` | Get business days in range |
| POST | `/calendars/{name}/rollover` | Signal EOD rollover |
| GET | `/calendars/{name}/markers/{date}` | Get marker states for date |
| POST | `/calendars/{name}/markers/{date}/{marker}` | Update marker state |

### Response Examples

```json
// GET /calendars/trading/current
{
  "calendar_name": "trading",
  "business_date": "2025-12-13",
  "system_date": "2025-12-14",
  "is_processing_day": true,
  "market_status": "closed",
  "next_business_date": "2025-12-15",
  "previous_business_date": "2025-12-12",
  "eod_markers": {
    "eod_1": { "complete": true, "completed_at": "2025-12-13T18:30:00Z" },
    "eod_2": { "complete": true, "completed_at": "2025-12-13T20:15:00Z" },
    "eod_3": { "complete": false }
  }
}

// GET /calendars/trading/is-business-day?date=2025-12-25
{
  "date": "2025-12-25",
  "is_business_day": false,
  "reason": "holiday",
  "holiday_name": "Christmas Day"
}

// GET /calendars/trading/add-days?from=2025-12-13&days=2
{
  "from_date": "2025-12-13",
  "days_requested": 2,
  "result_date": "2025-12-17",
  "skipped_dates": ["2025-12-14", "2025-12-15", "2025-12-16"],
  "skip_reasons": {
    "2025-12-14": "non_processing_day",
    "2025-12-15": "non_processing_day",
    "2025-12-16": "holiday"
  }
}
```

---

## Summary

| Component | Change | Complexity |
|-----------|--------|------------|
| L5 Infra | Calendar API config only (no calendar definition) | Low |
| L1 Flow | `business_date from`, `markers`, `phase` blocks | High |
| L2 Schema | `bizdate` type | Low |
| L3 Transform | Calendar functions | Medium |
| L4 Rules | Date/marker conditions | Low |
| Code Gen | CalendarClient, MarkerStateManager, PhaseGating | High |
| External | Calendar Service API (separate service) | Separate project |

**Key Design Decision**: Calendar logic lives in external API, not L5. L5 only stores the API endpoint and cache configuration. This enables:
- Centralized calendar management
- Dynamic holiday updates without redeployment
- Multi-calendar support (trading, settlement, reporting)
- Operational visibility into marker states
