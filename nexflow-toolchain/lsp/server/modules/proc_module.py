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
from backend.parser.flow_parser import FlowParser
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
        "structure": ["process", "end"],

        # Execution
        "execution": [
            "parallelism", "hint", "partition", "by",
            "time", "watermark", "delay", "late", "data", "allowed", "lateness",
            "mode", "stream", "batch", "micro_batch"
        ],

        # Input
        "input": [
            "receive", "from", "schema", "project", "except",
            "store", "in", "match", "on"
        ],

        # Processing
        "processing": [
            "transform", "using", "enrich", "select",
            "route", "aggregate", "merge", "into"
        ],

        # Window
        "window": [
            "window", "tumbling", "sliding", "session", "gap", "every"
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
            "emit", "to", "fanout", "broadcast", "round_robin"
        ],

        # Completion
        "completion": [
            "commit", "failure", "completion", "correlation", "include"
        ],

        # State
        "state": [
            "state", "uses", "local", "counter", "gauge", "map", "list",
            "ttl", "sliding", "absolute", "cleanup",
            "on_checkpoint", "on_access", "background",
            "buffer", "fifo", "lifo", "priority"
        ],

        # Resilience
        "resilience": [
            "error", "transform", "lookup", "rule",
            "dead_letter", "skip", "retry",
            "checkpoint", "strategy", "block", "drop", "sample", "alert", "after"
        ],

        # Time units
        "time_units": [
            "seconds", "second", "minutes", "minute",
            "hours", "hour", "days", "day"
        ],
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
    }

    def __init__(self):
        """Initialize the ProcDSL module."""
        self._parser = FlowParser()
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
