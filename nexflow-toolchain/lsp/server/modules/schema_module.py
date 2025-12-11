"""
L2 SchemaDSL Language Module

Provides Language Server Protocol support for SchemaDSL (Schema Registry DSL).
Handles .schema files with syntax validation, completions, symbols, and hover.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict
from lsprotocol import types

# Add project root to path for imports (NOT backend, to avoid ast module conflict)
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from .base import LanguageModule, ModuleCapabilities

# Import existing parser infrastructure from backend
from backend.parser.schema_parser import SchemaParser
from backend.parser.base import ParseResult


class SchemaModule(LanguageModule):
    """
    Language module for L2 SchemaDSL (Schema Registry DSL).

    Supports:
    - Real-time diagnostics (parse errors)
    - Keyword completion
    - Document symbols (schema definitions)
    - Hover documentation for keywords

    File extensions: .schema
    """

    # SchemaDSL keywords organized by category
    KEYWORDS = {
        # Structure
        "structure": ["schema", "end", "types"],

        # Patterns (9 mutation patterns)
        "patterns": [
            "pattern", "master_data", "immutable_ledger", "versioned_configuration",
            "operational_parameters", "event_log", "state_machine", "temporal_data",
            "reference_data", "business_logic"
        ],

        # Version/Evolution
        "version": [
            "version", "compatibility", "backward", "forward", "full", "none",
            "previous_version", "deprecated", "deprecated_since", "removal_version",
            "migration_guide"
        ],

        # Blocks
        "blocks": [
            "identity", "streaming", "fields", "parameters", "entries", "rule",
            "migration", "transitions", "on_transition", "given", "calculate", "return"
        ],

        # Types
        "types": [
            "string", "integer", "decimal", "boolean", "date", "timestamp",
            "uuid", "bytes", "list", "set", "map", "object"
        ],

        # Streaming
        "streaming": [
            "key_fields", "time_field", "time_semantics", "event_time",
            "processing_time", "ingestion_time", "watermark_delay",
            "watermark_strategy", "watermark_field", "max_out_of_orderness",
            "watermark_interval", "bounded_out_of_orderness", "periodic",
            "punctuated", "late_data_handling", "late_data_stream",
            "side_output", "drop", "update", "allowed_lateness",
            "idle_timeout", "idle_behavior", "mark_idle", "advance_to_infinity",
            "keep_waiting", "sparsity", "dense", "moderate", "sparse",
            "retention", "time", "size", "policy", "delete_oldest", "archive", "compact"
        ],

        # Field qualifiers
        "qualifiers": [
            "required", "optional", "unique", "cannot_change", "encrypted",
            "default", "pii"
        ],

        # Constraints
        "constraints": [
            "range", "length", "pattern", "values", "precision", "scale"
        ],

        # State machine
        "state_machine": [
            "for_entity", "states", "initial_state", "from", "to"
        ],

        # Expressions
        "expressions": [
            "when", "otherwise", "and", "or", "null"
        ],

        # Time units
        "time_units": [
            "seconds", "second", "minutes", "minute", "hours", "hour",
            "days", "day", "weeks", "week", "months", "month", "years", "year",
            "milliseconds", "millisecond"
        ],

        # Size units
        "size_units": ["bytes", "KB", "MB", "GB", "TB"],
    }

    # Keyword documentation
    KEYWORD_DOCS = {
        # Structure
        "schema": "**schema** `name`\n\nDefines a schema for data structures with optional mutation patterns.",
        "end": "**end**\n\nCloses a block (schema, identity, fields, streaming, etc.).",
        "types": "**types**\n\nDefines reusable type aliases that can be referenced in schemas.",

        # Patterns
        "pattern": "**pattern** `mutation_pattern`\n\nDeclares which of the 9 mutation patterns this schema follows.",
        "master_data": "**master_data**\n\nSCD Type 2 pattern - tracks full history with effective dates.",
        "immutable_ledger": "**immutable_ledger**\n\nAppend-only financial records that cannot be modified.",
        "event_log": "**event_log**\n\nAppend-only event stream for event sourcing patterns.",
        "state_machine": "**state_machine**\n\nWorkflow state tracking with defined states and transitions.",
        "reference_data": "**reference_data**\n\nLookup tables with predefined entries.",
        "temporal_data": "**temporal_data**\n\nEffective-dated values with time-based validity.",

        # Blocks
        "identity": "**identity**\n\nDefines the identity/key fields that uniquely identify records.",
        "streaming": "**streaming**\n\nConfigures streaming semantics: keys, time fields, watermarks.",
        "fields": "**fields**\n\nDefines the data fields with types and constraints.",
        "parameters": "**parameters**\n\nDefines configurable parameters for operational_parameters pattern.",

        # Types
        "string": "**string**\n\nText type. Can have `length` and `pattern` constraints.",
        "integer": "**integer**\n\nWhole number type. Can have `range` constraint.",
        "decimal": "**decimal**\n\nDecimal number type. Can have `precision` and `scale`.",
        "boolean": "**boolean**\n\nTrue/false type.",
        "timestamp": "**timestamp**\n\nDate and time with timezone.",
        "uuid": "**uuid**\n\nUniversally unique identifier.",
        "list": "**list**`<type>`\n\nOrdered collection of elements.",
        "map": "**map**`<key, value>`\n\nKey-value mapping.",

        # Streaming
        "key_fields": "**key_fields**: `[field1, field2]`\n\nPartition key fields for streaming.",
        "time_field": "**time_field**: `field_name`\n\nEvent time field for time-based operations.",
        "watermark_delay": "**watermark_delay**: `duration`\n\nAllowed out-of-orderness for watermarks.",
        "event_time": "**event_time**\n\nUse event timestamp for time-based operations.",
        "processing_time": "**processing_time**\n\nUse processing timestamp for time-based operations.",

        # Qualifiers
        "required": "**required**\n\nField must have a value (not null).",
        "optional": "**optional**\n\nField may be null.",
        "unique": "**unique**\n\nField value must be unique across records.",
        "cannot_change": "**cannot_change**\n\nField value cannot be modified after creation.",
        "encrypted": "**encrypted**\n\nField value is encrypted at rest.",
        "pii": "**pii**`.profile`\n\nPersonally identifiable information with encryption profile.\n\nProfiles: `ssn`, `pan`, `email`, or custom.",

        # Constraints
        "range": "**range**: `min..max`\n\nNumeric value must be within range.",
        "length": "**length**: `min..max`\n\nString length must be within range.",
        "pattern": "**pattern**: `\"regex\"`\n\nString must match regex pattern.",
        "values": "**values**: `[a, b, c]`\n\nValue must be one of the listed values.",

        # Version
        "version": "**version** `x.y.z`\n\nSchema version number for evolution tracking.",
        "compatibility": "**compatibility** `mode`\n\nEvolution compatibility: backward, forward, full, none.",
        "backward": "**backward**\n\nNew schema can read data written by old schema.",
        "forward": "**forward**\n\nOld schema can read data written by new schema.",
    }

    def __init__(self):
        """Initialize the SchemaDSL module."""
        self._parser = SchemaParser()
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
        return "schemadsl"

    @property
    def file_extensions(self) -> List[str]:
        return [".schema"]

    @property
    def display_name(self) -> str:
        return "SchemaDSL (L2 Schema Registry)"

    @property
    def capabilities(self) -> ModuleCapabilities:
        return ModuleCapabilities(
            diagnostics=True,
            completion=True,
            hover=True,
            symbols=True,
            definition=False,
            references=False,
            formatting=False,
        )

    @property
    def trigger_characters(self) -> List[str]:
        return [" ", "\n", ":"]

    @property
    def version(self) -> str:
        return "0.1.0"

    # =========================================================================
    # Core Methods
    # =========================================================================

    def get_diagnostics(self, uri: str, content: str) -> List[types.Diagnostic]:
        """Parse content and return diagnostics."""
        diagnostics: List[types.Diagnostic] = []

        try:
            result = self._parser.parse(content)

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
                    diagnostics.append(types.Diagnostic(
                        range=self.create_range(0, 0, 0, 1),
                        message=error.message,
                        severity=types.DiagnosticSeverity.Error,
                        source=f"nexflow-{self.language_id}"
                    ))

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
        """Return keyword completions."""
        items: List[types.CompletionItem] = []

        lines = content.split("\n")
        current_line = ""
        if 0 <= position.line < len(lines):
            current_line = lines[position.line][:position.character].strip().lower()

        relevant_keywords = self._get_contextual_keywords(current_line, content, position)

        for keyword in relevant_keywords:
            doc = self.KEYWORD_DOCS.get(keyword)
            items.append(types.CompletionItem(
                label=keyword,
                kind=types.CompletionItemKind.Keyword,
                detail="SchemaDSL keyword",
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
        """Get keywords relevant to the current context."""
        # At start of line, suggest top-level keywords
        if not current_line:
            return ["schema", "types", "end"] + self._all_keywords

        # After 'schema', suggest name then blocks
        if current_line.startswith("schema"):
            return ["pattern", "version", "retention", "identity", "streaming", "fields", "end"]

        # After 'pattern', suggest mutation patterns
        if current_line.startswith("pattern"):
            return list(self.KEYWORDS["patterns"])[1:]  # Skip 'pattern' itself

        # After 'fields', suggest types and qualifiers
        if "fields" in content[:content.find(current_line)] and ":" in current_line:
            return list(self.KEYWORDS["types"]) + list(self.KEYWORDS["qualifiers"])

        # After 'streaming', suggest streaming keywords
        if "streaming" in content[:content.find(current_line)]:
            return list(self.KEYWORDS["streaming"])

        # After type declaration, suggest qualifiers and constraints
        if any(t in current_line for t in ["string", "integer", "decimal", "boolean", "timestamp"]):
            return list(self.KEYWORDS["qualifiers"]) + list(self.KEYWORDS["constraints"])

        # Default: return all keywords
        return self._all_keywords

    def get_hover(
        self,
        uri: str,
        content: str,
        position: types.Position
    ) -> Optional[types.Hover]:
        """Return hover documentation for keyword at position."""
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

        start = position.character
        end = position.character

        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        if start == end:
            return None

        return line[start:end]

    def get_symbols(self, uri: str, content: str) -> List[types.DocumentSymbol]:
        """Extract schema definitions as document symbols."""
        symbols: List[types.DocumentSymbol] = []

        try:
            result = self._parser.parse(content)

            if result.ast and hasattr(result.ast, 'schemas'):
                for schema in result.ast.schemas:
                    # Create range from schema position
                    start_line = getattr(schema, 'line', 1) - 1
                    end_line = start_line + 10  # Approximate

                    # Find actual end by searching for 'end'
                    lines = content.split("\n")
                    for i in range(start_line, min(len(lines), start_line + 100)):
                        if lines[i].strip() == "end":
                            end_line = i
                            break

                    schema_range = self.create_range(start_line, 0, end_line, 3)

                    children = []

                    # Add pattern as child if present
                    if hasattr(schema, 'patterns') and schema.patterns:
                        pattern_symbol = types.DocumentSymbol(
                            name=f"pattern: {', '.join(schema.patterns)}",
                            kind=types.SymbolKind.Property,
                            range=schema_range,
                            selection_range=schema_range,
                        )
                        children.append(pattern_symbol)

                    # Add identity block if present
                    if hasattr(schema, 'identity') and schema.identity:
                        identity_symbol = types.DocumentSymbol(
                            name="identity",
                            kind=types.SymbolKind.Struct,
                            range=schema_range,
                            selection_range=schema_range,
                        )
                        children.append(identity_symbol)

                    # Add fields block if present
                    if hasattr(schema, 'fields') and schema.fields:
                        fields_symbol = types.DocumentSymbol(
                            name=f"fields ({len(schema.fields)})",
                            kind=types.SymbolKind.Struct,
                            range=schema_range,
                            selection_range=schema_range,
                        )
                        children.append(fields_symbol)

                    symbol = types.DocumentSymbol(
                        name=schema.name,
                        kind=types.SymbolKind.Class,
                        range=schema_range,
                        selection_range=self.create_range(start_line, 0, start_line, len(schema.name) + 7),
                        detail=f"schema",
                        children=children if children else None
                    )
                    symbols.append(symbol)

            # Also look for type aliases
            if result.ast and hasattr(result.ast, 'type_aliases'):
                for alias in result.ast.type_aliases:
                    alias_line = getattr(alias, 'line', 1) - 1
                    alias_range = self.create_range(alias_line, 0, alias_line, 50)

                    symbol = types.DocumentSymbol(
                        name=alias.name,
                        kind=types.SymbolKind.TypeParameter,
                        range=alias_range,
                        selection_range=alias_range,
                        detail="type alias"
                    )
                    symbols.append(symbol)

        except Exception:
            # If AST extraction fails, fall back to regex-based extraction
            import re
            schema_pattern = re.compile(r'^schema\s+(\w+)', re.MULTILINE)
            lines = content.split("\n")

            for match in schema_pattern.finditer(content):
                name = match.group(1)
                line_num = content[:match.start()].count("\n")

                symbol = types.DocumentSymbol(
                    name=name,
                    kind=types.SymbolKind.Class,
                    range=self.create_range(line_num, 0, line_num + 1, 0),
                    selection_range=self.create_range(line_num, 7, line_num, 7 + len(name)),
                    detail="schema"
                )
                symbols.append(symbol)

        return symbols
