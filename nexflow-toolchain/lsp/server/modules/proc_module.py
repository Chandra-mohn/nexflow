"""
L1 ProcDSL Language Module

Provides Language Server Protocol support for ProcDSL (Process Orchestration DSL).
Handles .proc files with syntax validation, completions, symbols, and hover.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from lsprotocol import types

# Add project root to path for imports (NOT backend, to avoid ast module conflict)
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from .base import LanguageModule, ModuleCapabilities, SymbolInfo

# Import existing parser infrastructure from backend
from backend.parser.proc_parser import ProcParser
from backend.parser.base import ParseResult, ParseError


class ProcModule(LanguageModule):
    """
    Language module for L1 ProcDSL (Process Orchestration DSL).

    Supports:
    - Real-time diagnostics (parse errors)
    - Keyword completion
    - Document symbols (process definitions)
    - Hover documentation for keywords

    File extensions: .proc
    """

    # ProcDSL keywords organized by category
    KEYWORDS = {
        # Structure
        "structure": ["process", "end", "import"],

        # Execution
        "execution": [
            "parallelism", "hint", "partition", "by",
            "time", "watermark", "delay", "late", "data", "allowed", "lateness",
            "mode", "stream", "batch", "micro_batch"
        ],

        # Business Date & EOD Markers (v0.6.0+)
        "eod_markers": [
            "business_date", "processing_date", "auto",
            "markers", "phase", "before", "after", "between", "anytime",
            "signal", "drained", "fired", "pending",
            "on_complete", "end_of_day"
        ],

        # Input
        "input": [
            "receive", "from", "schema", "project", "except",
            "store", "in", "match", "on", "filter"
        ],

        # Connectors
        "connectors": [
            "kafka", "mongodb", "redis", "scheduler", "state_store",
            "group", "offset", "latest", "earliest",
            "isolation", "read_committed", "read_uncommitted",
            "compaction", "retention", "infinite", "upsert",
            "headers", "index", "template", "channel", "payload"
        ],

        # Processing
        "processing": [
            "transform", "using", "enrich", "select",
            "route", "aggregate", "merge", "into",
            "evaluate", "params", "input", "output", "lookups"
        ],

        # Control Flow
        "control_flow": [
            "if", "then", "else", "elseif", "endif",
            "foreach", "continue", "terminate",
            "branch", "parallel", "require_all", "min_required"
        ],

        # Window
        "window": [
            "window", "tumbling", "sliding", "session", "gap", "every",
            "key", "count", "sum", "avg", "min", "max", "collect", "first", "last", "as"
        ],

        # Join
        "join": [
            "join", "with", "within", "type",
            "inner", "left", "right", "outer"
        ],

        # Correlation
        "correlation": [
            "await", "until", "arrives", "matching", "timeout",
            "hold", "keyed", "complete", "when", "count", "marker", "received"
        ],

        # Output
        "output": [
            "emit", "to", "fanout", "broadcast", "round_robin",
            "persist", "async", "sync", "flush", "interval", "fail"
        ],

        # Completion
        "completion": [
            "commit", "failure", "completion", "correlation", "include"
        ],

        # State Machine
        "state_machine": [
            "state_machine", "persistence", "transition", "events"
        ],

        # State
        "state": [
            "state", "uses", "local", "counter", "gauge", "map", "list",
            "ttl", "sliding", "absolute", "cleanup",
            "on_checkpoint", "on_access", "background",
            "buffer", "fifo", "lifo", "priority"
        ],

        # External Calls
        "external": [
            "call", "external", "ml_service", "endpoint", "features",
            "circuit_breaker", "failure_threshold", "reset_timeout"
        ],

        # Scheduling
        "scheduling": [
            "schedule", "action", "repeat"
        ],

        # Validation & Deduplication
        "validation": [
            "validate_input", "require", "deduplicate"
        ],

        # Variables
        "variables": [
            "let", "set"
        ],

        # Audit
        "audit": [
            "emit_audit_event", "actor", "system", "user"
        ],

        # Conditional Actions
        "conditional": [
            "add_flag", "add_metadata", "adjust_score",
            "on_critical_fraud", "on_duplicate",
            "on_success", "on_failure", "on_partial_timeout"
        ],

        # Resilience
        "resilience": [
            "error", "transform_error", "lookup_error", "rule_error", "correlation_error",
            "dead_letter", "skip", "retry", "times", "indefinitely",
            "backoff", "exponential", "linear", "max_delay",
            "checkpoint", "strategy", "block", "drop", "sample", "alert", "after",
            "backpressure", "slow", "preserve_state", "include_error_context",
            "log_error", "log_warning", "log_info"
        ],

        # Metrics
        "metrics": [
            "metrics", "histogram", "rate"
        ],

        # Time units
        "time_units": [
            "seconds", "second", "minutes", "minute",
            "hours", "hour", "days", "day", "weeks", "week"
        ],

        # Boolean/Logic
        "logic": [
            "and", "or", "not", "true", "false", "null", "is", "contains", "none", "filter"
        ],

        # Lookup & Cache
        "lookup": ["lookup", "cache"],

        # Sizing
        "sizing": ["size"],

        # Rule reference
        "rule": ["rule"],
    }

    # Keyword documentation for hover
    KEYWORD_DOCS: Dict[str, str] = {
        "process": "**process** `name`\n\nDefines a streaming or batch process. Contains execution config, input, processing, and output blocks.\n\n```\nprocess my_processor\n    receive orders from kafka\n    transform using enrich_order\n    emit to processed_orders\nend\n```",
        "end": "**end**\n\nCloses a process definition block.",
        "receive": "**receive** `alias` **from** `source`\n\nDeclares an input source for the process.\n\n```\nreceive orders\n    schema order_schema\n    from kafka \"orders-topic\"\n```",
        "emit": "**emit to** `target`\n\nDeclares an output destination.\n\n```\nemit to processed_orders\n    schema enriched_order\n    fanout broadcast\n```",
        "transform": "**transform using** `transform_name`\n\nApplies a transformation (defined in L3 TransformDSL).\n\n```\ntransform using calculate_totals\n```",
        "enrich": "**enrich using** `enricher` **on** `fields`\n\nJoins with external data source on specified keys.\n\n```\nenrich using customer_lookup\n    on customer_id\n    select name, tier\n```",
        "window": "**window** `type` `duration`\n\nDefines a windowing strategy for aggregation.\n\n```\nwindow tumbling 1 hour\nwindow sliding 30 minutes every 5 minutes\nwindow session gap 10 minutes\n```",
        "join": "**join** `stream1` **with** `stream2` **on** `keys` **within** `duration`\n\nJoins two streams within a time window.\n\n```\njoin orders with payments\n    on order_id\n    within 1 hour\n    type left\n```",
        "await": "**await** `source` **until** `trigger` **arrives**\n\nEvent-driven correlation - waits for a triggering event.\n\n```\nawait orders\n    until payment arrives\n    matching on order_id\n    timeout 24 hours emit to stale_orders\n```",
        "hold": "**hold** `source` **keyed by** `fields`\n\nBuffer-based correlation - holds records until condition met.\n\n```\nhold line_items\n    keyed by order_id\n    complete when count >= 3\n    timeout 1 hour emit to incomplete_orders\n```",
        "route": "**route using** `router`\n\nRoutes records to different outputs based on rules (L4).\n\n```\nroute using fraud_classifier\n```",
        "parallelism": "**parallelism** [`hint`] `n`\n\nSets the parallelism level for the process.\n\n```\nparallelism hint 8\n```",
        "partition": "**partition by** `fields`\n\nPartitions the stream by specified key fields.\n\n```\npartition by customer_id, region\n```",
        "watermark": "**watermark delay** `duration`\n\nSets the watermark delay for event time processing.\n\n```\ntime by event_timestamp\n    watermark delay 10 seconds\n```",
        "state": "**state**\n\nDeclares state stores used by the process.\n\n```\nstate\n    uses order_cache\n    local counters keyed by customer_id type counter ttl 1 hour\n```",
        "checkpoint": "**checkpoint every** `duration` **to** `backend`\n\nConfigures checkpointing for fault tolerance.\n\n```\ncheckpoint every 5 minutes\n    to rocksdb\n```",
        "schema": "**schema** `schema_name`\n\nSpecifies the schema (from L2 SchemaDSL) for input or output.\n\n```\nreceive orders\n    schema order_event\n```",

        # Import (v0.7.0+)
        "import": "**import** `path`\n\nImports definitions from another DSL file.\n\n```\nimport ../schemas/order.schema\nimport ./transforms/enrichment.xform\n```",

        # Business Date & EOD Markers (v0.6.0+)
        "business_date": "**business_date from** `calendar`\n\nDeclares the business date calendar for the process. Essential for financial workflows.\n\n```\nprocess DailySettlement\n    business_date from trading_calendar\n    processing_date auto\n```",
        "processing_date": "**processing_date auto**\n\nDeclares that processing date uses system clock. Part of the three-date model.\n\n```\nprocessing_date auto\n```",
        "markers": "**markers**\n\nDefines EOD (End-of-Day) marker conditions that trigger phase transitions.\n\n```\nmarkers\n    market_close: when after \"16:00\"\n    trades_drained: when trades.drained\n    eod_ready: when market_close and trades_drained\nend\n```",
        "phase": "**phase** `before|after|between` `marker`\n\nDefines a processing phase relative to EOD markers.\n\n```\nphase before eod_ready\n    receive trades from kafka\n    transform using accumulate\nend\n\nphase after eod_ready\n    receive from state_store\n    transform using settle\nend\n```",
        "before": "**before** `marker`\n\nPhase executes before the marker fires.\n\n```\nphase before eod_ready\n```",
        "after": "**after** `marker` | `time`\n\nPhase executes after marker fires, or time-based marker condition.\n\n```\nphase after eod_ready\n// or in markers block:\nmarket_close: when after \"16:00\"\n```",
        "between": "**between** `marker1` **and** `marker2`\n\nPhase executes between two markers.\n\n```\nphase between eod_1 and eod_2\n```",
        "anytime": "**anytime**\n\nPhase executes regardless of marker state.\n\n```\nphase anytime\n    // Always-on processing\nend\n```",
        "signal": "**signal** `name` **to** `target`\n\nEmits a signal for marker coordination or cross-process communication.\n\n```\non_complete signal settlement_done to downstream\n```",
        "drained": "**stream.drained**\n\nMarker condition that fires when a stream has no more pending records.\n\n```\ntrades_drained: when trades.drained\n```",
        "end_of_day": "**end_of_day**\n\nKeyword for time-based marker conditions.\n\n```\neod_marker: when end_of_day\n```",

        # Connectors
        "kafka": "**kafka** `\"topic\"`\n\nKafka connector for streaming input/output.\n\n```\nreceive orders\n    from kafka \"orders-topic\"\n    group \"consumer-group\"\n    offset latest\n```",
        "mongodb": "**mongodb** `\"collection\"`\n\nMongoDB connector for persistence.\n\n```\npersist to mongodb \"orders_collection\"\n```",
        "state_store": "**state_store** `\"name\"`\n\nFlink state store for buffered data.\n\n```\nreceive buffered from state_store \"trade_buffer\"\n```",

        # State Machine
        "state_machine": "**state_machine** `name`\n\nDeclares a state machine for entity lifecycle tracking.\n\n```\nstate_machine order_lifecycle\n    schema OrderState\n    persistence order_db\n    checkpoint every 100 events\n```",
        "transition": "**transition to** `\"state\"`\n\nTransitions entity to a new state.\n\n```\ntransition to \"completed\"\n```",
        "persistence": "**persistence** `target`\n\nDeclares persistence target for state machine.\n\n```\npersistence order_db\n```",

        # External Calls
        "call": "**call** `external|ml_service` `name`\n\nCalls an external service or ML model.\n\n```\ncall external fraud_service\n    endpoint \"https://api.example.com/check\"\n    timeout 5 seconds\n    retry 3 times\n```",
        "evaluate": "**evaluate using** `rule_name`\n\nEvaluates an L4 business rule.\n\n```\nevaluate using fraud_detection\n    params: { amount: transaction.amount }\n    output decision\n```",

        # Control Flow
        "foreach": "**foreach** `item` **in** `collection`\n\nIterates over a collection.\n\n```\nforeach line_item in order.items\n    transform using process_item\nend\n```",
        "branch": "**branch** `name`\n\nConditional sub-pipeline branch.\n\n```\nbranch high_value\n    transform using premium_handling\n    emit to vip_queue\nend\n```",

        # Validation
        "validate_input": "**validate_input**\n\nValidates input records with rules.\n\n```\nvalidate_input\n    require amount > 0 else \"Amount must be positive\"\n    require customer_id is not null else \"Customer required\"\n```",
        "deduplicate": "**deduplicate by** `field` **window** `duration`\n\nRemoves duplicate records within a time window.\n\n```\ndeduplicate by transaction_id\n    window 1 hour\n```",

        # Persist
        "persist": "**persist to** `target`\n\nPersists records to external storage (L5 integration).\n\n```\nemit to output\n    persist to order_db async\n```",

        # Metrics
        "metrics": "**metrics**\n\nDefines observability metrics for the process.\n\n```\nmetrics\n    counter processed_count\n    histogram latency\n    gauge queue_depth\nend\n```",

        # Lookup
        "lookup": "**lookup** `name` **from** `source`\n\nLooks up data from external source with optional caching.\n\n```\nlookup customer_data\n    key customer_id\n    from mongodb \"customers\"\n    cache ttl 1 hour\n```",
        "cache": "**cache ttl** `duration`\n\nEnables caching for lookup with specified time-to-live.\n\n```\ncache ttl 30 minutes\n```",

        # Filter
        "filter": "**filter** `condition`\n\nFilters records based on a condition.\n\n```\nreceive orders\n    filter amount > 100\n```",

        # Control Flow additional
        "when": "**when** `condition`\n\nConditional clause used in various contexts.\n\n```\nroute using decision\n    when result == \"approved\" to approved_sink\n    otherwise to review_queue\n```",
        "otherwise": "**otherwise**\n\nDefault case in route or conditional expressions.\n\n```\notherwise to default_sink\notherwise continue\n```",

        # Window additional
        "tumbling": "**tumbling** `duration`\n\nFixed-size non-overlapping window.\n\n```\nwindow tumbling 1 hour\n```",
        "sliding": "**sliding** `duration` **every** `step`\n\nOverlapping window with step size.\n\n```\nwindow sliding 1 hour every 15 minutes\n```",
        "session": "**session gap** `duration`\n\nSession window that closes after inactivity gap.\n\n```\nwindow session gap 30 minutes\n```",

        # Resilience additional
        "retry": "**retry** `n` **times**\n\nRetry failed operations with optional backoff.\n\n```\nretry 3 times\n    delay 1 second\n    backoff exponential\n    max_delay 30 seconds\n```",
        "dead_letter": "**dead_letter** `target`\n\nSend failed records to dead letter queue.\n\n```\non error\n    transform_error dead_letter failed_transforms\nend\n```",

        # Aggregation functions
        "count": "**count()**\n\nCounts records in window.\n\n```\naggregate\n    count() as total_count\nend\n```",
        "sum": "**sum**(`field`)\n\nSums a numeric field in window.\n\n```\naggregate\n    sum(amount) as total_amount\nend\n```",
        "avg": "**avg**(`field`)\n\nCalculates average of a numeric field.\n\n```\naggregate\n    avg(amount) as avg_amount\nend\n```",
        "min": "**min**(`field`)\n\nFinds minimum value in window.\n\n```\naggregate\n    min(amount) as min_amount\nend\n```",
        "max": "**max**(`field`)\n\nFinds maximum value in window.\n\n```\naggregate\n    max(amount) as max_amount\nend\n```",
        "collect": "**collect**(`field`)\n\nCollects field values into a list.\n\n```\naggregate\n    collect(transaction_id) as transaction_ids\nend\n```",
        "first": "**first**(`field`)\n\nGets first value in window.\n\n```\naggregate\n    first(timestamp) as window_start\nend\n```",
        "last": "**last**(`field`)\n\nGets last value in window.\n\n```\naggregate\n    last(timestamp) as window_end\nend\n```",

        # On clauses
        "on": "**on** `event`\n\nTriggered action clause.\n\n```\non error\n    log_error \"Processing failed\"\nend\n\non commit\n    emit completion to notifications\n```",

        # Variables
        "let": "**let** `name` **=** `expression`\n\nDeclares a local variable.\n\n```\nlet threshold = config.fraud_threshold\nlet rate = lookup(\"rates\", currency)\n```",
        "set": "**set** `field` **=** `expression`\n\nSets a field value.\n\n```\nset enriched.risk_score = ml_result.score\n```",

        # Sizes and intervals
        "size": "**size** `n`\n\nBatch size configuration.\n\n```\npersist to mongodb async\n    batch size 100\n```",

        # Rule
        "rule": "**rule**\n\nRule reference in error handling.\n\n```\non error\n    rule_error dead_letter failed_rules\nend\n```",
    }

    def __init__(self):
        """Initialize the ProcDSL module."""
        self._parser = ProcParser()
        self._all_keywords = self._flatten_keywords()

    def _flatten_keywords(self) -> List[str]:
        """Flatten all keyword categories into a single list."""
        keywords = []
        for category_keywords in self.KEYWORDS.values():
            keywords.extend(category_keywords)
        return sorted(set(keywords))

    # =========================================================================
    # Required Properties
    # =========================================================================

    @property
    def language_id(self) -> str:
        return "procdsl"

    @property
    def file_extensions(self) -> List[str]:
        return [".proc"]

    @property
    def display_name(self) -> str:
        return "ProcDSL (L1 Process Orchestration)"

    @property
    def capabilities(self) -> ModuleCapabilities:
        return ModuleCapabilities(
            diagnostics=True,
            completion=True,
            hover=True,
            symbols=True,
            definition=False,  # Phase 2
            references=False,  # Phase 2
            formatting=False,  # Phase 2
        )

    @property
    def trigger_characters(self) -> List[str]:
        return [" ", "\n"]

    @property
    def version(self) -> str:
        return "0.1.0"

    # =========================================================================
    # Core Methods
    # =========================================================================

    def get_diagnostics(self, uri: str, content: str) -> List[types.Diagnostic]:
        """
        Parse content and return diagnostics.

        Uses the existing ANTLR parser infrastructure from backend.parser.
        """
        diagnostics: List[types.Diagnostic] = []

        try:
            result = self._parser.parse(content)

            # Convert parse errors to LSP diagnostics
            for error in result.errors:
                loc = error.location
                if loc:
                    diagnostics.append(self.create_diagnostic(
                        message=error.message,
                        line=loc.line,
                        column=loc.column,
                        end_column=loc.column + len(error.token or "") + 1 if error.token else loc.column + 10,
                        severity=types.DiagnosticSeverity.Error
                    ))
                else:
                    # Error without location - put at start of file
                    diagnostics.append(types.Diagnostic(
                        range=self.create_range(0, 0, 0, 1),
                        message=error.message,
                        severity=types.DiagnosticSeverity.Error,
                        source=f"nexflow-{self.language_id}"
                    ))

            # Convert warnings
            for warning in result.warnings:
                loc = warning.location
                if loc:
                    diagnostics.append(self.create_diagnostic(
                        message=warning.message,
                        line=loc.line,
                        column=loc.column,
                        severity=types.DiagnosticSeverity.Warning
                    ))

        except Exception as e:
            # Parser crashed - report as diagnostic
            diagnostics.append(types.Diagnostic(
                range=self.create_range(0, 0, 0, 1),
                message=f"Parser error: {str(e)}",
                severity=types.DiagnosticSeverity.Error,
                source=f"nexflow-{self.language_id}"
            ))

        return diagnostics

    def get_completions(
        self,
        uri: str,
        content: str,
        position: types.Position,
        trigger_character: Optional[str] = None
    ) -> List[types.CompletionItem]:
        """
        Return keyword completions.

        Currently provides all keywords. Future: context-aware completion.
        """
        items: List[types.CompletionItem] = []

        # Get the current line to provide context-aware completions
        lines = content.split("\n")
        current_line = ""
        if 0 <= position.line < len(lines):
            current_line = lines[position.line][:position.character].strip().lower()

        # Determine which keywords are relevant based on context
        relevant_keywords = self._get_contextual_keywords(current_line, content, position)

        for keyword in relevant_keywords:
            doc = self.KEYWORD_DOCS.get(keyword)
            items.append(types.CompletionItem(
                label=keyword,
                kind=types.CompletionItemKind.Keyword,
                detail="ProcDSL keyword",
                documentation=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=doc
                ) if doc else None,
                insert_text=keyword
            ))

        return items

    def _get_contextual_keywords(
        self,
        current_line: str,
        content: str,
        position: types.Position
    ) -> List[str]:
        """
        Get keywords relevant to the current context.

        Simple heuristic-based approach for MVP.
        """
        # At start of line or after specific keywords, suggest structure/blocks
        if not current_line or current_line in ["process", "end"]:
            return self._all_keywords

        # After 'receive' suggest input-related keywords
        if current_line.startswith("receive"):
            return ["from", "schema", "project", "except", "store", "match"]

        # After 'emit' suggest output-related keywords
        if current_line.startswith("emit"):
            return ["to", "schema", "fanout"]

        # After 'window' suggest window types
        if current_line.startswith("window"):
            return ["tumbling", "sliding", "session"]

        # After 'join' suggest join-related keywords
        if current_line.startswith("join"):
            return ["with", "on", "within", "type"]

        # After 'type' in join context, suggest join types
        if "type" in current_line:
            return ["inner", "left", "right", "outer"]

        # After 'on' suggest 'error' for error handling
        if current_line == "on":
            return ["error", "commit"]

        # Default: return all keywords
        return self._all_keywords

    def get_hover(
        self,
        uri: str,
        content: str,
        position: types.Position
    ) -> Optional[types.Hover]:
        """
        Return hover documentation for keyword at position.
        """
        # Get the word at the current position
        word = self._get_word_at_position(content, position)

        if word and word.lower() in self.KEYWORD_DOCS:
            doc = self.KEYWORD_DOCS[word.lower()]
            return types.Hover(
                contents=types.MarkupContent(
                    kind=types.MarkupKind.Markdown,
                    value=doc
                )
            )

        return None

    def _get_word_at_position(self, content: str, position: types.Position) -> Optional[str]:
        """Extract the word at the given position."""
        lines = content.split("\n")
        if position.line >= len(lines):
            return None

        line = lines[position.line]
        if position.character >= len(line):
            return None

        # Find word boundaries
        start = position.character
        end = position.character

        # Scan backwards for start of word
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        # Scan forwards for end of word
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        if start == end:
            return None

        return line[start:end]

    def get_symbols(self, uri: str, content: str) -> List[types.DocumentSymbol]:
        """
        Extract process definitions as document symbols.

        Returns hierarchical symbols showing:
        - Process definitions (top-level)
        - Blocks within processes (children)
        """
        symbols: List[types.DocumentSymbol] = []

        try:
            result = self._parser.parse(content)

            if result.ast and hasattr(result.ast, "processes"):
                for proc in result.ast.processes:
                    proc_symbol = self._create_process_symbol(proc, content)
                    if proc_symbol:
                        symbols.append(proc_symbol)

        except Exception:
            # If parsing fails, try simple regex-based extraction
            symbols = self._extract_symbols_regex(content)

        return symbols

    def _create_process_symbol(
        self,
        proc: Any,
        content: str
    ) -> Optional[types.DocumentSymbol]:
        """Create a DocumentSymbol from a ProcessDefinition AST node."""
        if not proc.name:
            return None

        # Get location info
        loc = proc.location
        if loc:
            start_line = loc.line - 1
            start_char = loc.column
        else:
            # Find process in content
            start_line, start_char = self._find_process_location(content, proc.name)

        # Find the 'end' keyword to get the full range
        end_line, end_char = self._find_process_end(content, start_line)

        proc_range = self.create_range(start_line, start_char, end_line, end_char)

        # Create child symbols for blocks
        children: List[types.DocumentSymbol] = []

        # Add receive blocks as children
        if proc.input and proc.input.receives:
            for recv in proc.input.receives:
                recv_name = recv.alias or recv.source
                if recv_name:
                    children.append(types.DocumentSymbol(
                        name=f"receive {recv_name}",
                        kind=types.SymbolKind.Event,
                        range=proc_range,  # Simplified - use proc range
                        selection_range=proc_range,
                    ))

        # Add emit blocks as children
        if proc.output and proc.output.emits:
            for emit in proc.output.emits:
                if emit.target:
                    children.append(types.DocumentSymbol(
                        name=f"emit to {emit.target}",
                        kind=types.SymbolKind.Event,
                        range=proc_range,
                        selection_range=proc_range,
                    ))

        return types.DocumentSymbol(
            name=proc.name,
            kind=types.SymbolKind.Function,
            range=proc_range,
            selection_range=self.create_range(start_line, start_char, start_line, start_char + len(proc.name) + 8),
            detail="process",
            children=children if children else None
        )

    def _find_process_location(self, content: str, name: str) -> tuple:
        """Find the line and column of a process definition."""
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if f"process {name}" in line:
                col = line.index(f"process {name}")
                return (i, col)
        return (0, 0)

    def _find_process_end(self, content: str, start_line: int) -> tuple:
        """Find the 'end' keyword that closes a process."""
        lines = content.split("\n")
        depth = 0
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            if line.startswith("process "):
                depth += 1
            elif line == "end":
                if depth <= 1:
                    return (i, len(lines[i]))
                depth -= 1
        return (len(lines) - 1, 0)

    def _extract_symbols_regex(self, content: str) -> List[types.DocumentSymbol]:
        """
        Fallback symbol extraction using regex.

        Used when AST parsing fails.
        """
        import re
        symbols: List[types.DocumentSymbol] = []

        # Find all process definitions
        pattern = r"^\s*process\s+(\w+)"
        for match in re.finditer(pattern, content, re.MULTILINE):
            name = match.group(1)
            line = content[:match.start()].count("\n")
            col = match.start() - content.rfind("\n", 0, match.start()) - 1

            symbols.append(types.DocumentSymbol(
                name=name,
                kind=types.SymbolKind.Function,
                range=self.create_range(line, col, line, col + len(match.group(0))),
                selection_range=self.create_range(line, col, line, col + len(match.group(0))),
                detail="process"
            ))

        return symbols
