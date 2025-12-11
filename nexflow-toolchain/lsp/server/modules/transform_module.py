"""
L3 TransformDSL Language Module

Provides Language Server Protocol support for TransformDSL (Transform Catalog DSL).
Handles .xform and .transform files with syntax validation, completions, symbols, and hover.
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
from backend.parser.transform_parser import TransformParser
from backend.parser.base import ParseResult


class TransformModule(LanguageModule):
    """
    Language module for L3 TransformDSL (Transform Catalog DSL).

    Supports:
    - Real-time diagnostics (parse errors)
    - Keyword completion
    - Document symbols (transform definitions)
    - Hover documentation for keywords

    File extensions: .xform, .transform
    """

    # TransformDSL keywords organized by category
    KEYWORDS = {
        # Structure
        "structure": ["transform", "transform_block", "end"],

        # Metadata
        "metadata": [
            "version", "description", "previous_version", "compatibility",
            "backward", "forward", "full", "none"
        ],

        # Purity & Caching
        "purity": ["pure", "cache", "ttl", "key"],

        # Input/Output
        "io": ["input", "output", "nullable", "required", "default"],

        # Types
        "types": [
            "string", "integer", "decimal", "boolean", "date", "timestamp",
            "uuid", "bytes", "list", "set", "map"
        ],

        # Constraints
        "constraints": ["range", "length", "pattern", "values", "precision", "scale"],

        # Apply & Mappings
        "apply": ["apply", "mappings", "use"],

        # Composition
        "compose": ["compose", "sequential", "parallel", "conditional", "then"],

        # Validation
        "validation": [
            "validate_input", "validate_output", "invariant", "on_invalid",
            "message", "code", "severity"
        ],

        # Error handling
        "error": [
            "on_error", "action", "reject", "skip", "use_default", "raise",
            "emit_to", "emit_all_errors", "error_code", "error_message", "log_level"
        ],

        # Severity levels
        "severity": ["error", "warning", "info", "debug"],

        # Recalculation
        "recalc": ["on_change", "recalculate"],

        # Expression keywords
        "expressions": [
            "when", "otherwise", "between", "in", "is", "not", "and", "or", "null"
        ],

        # Time units
        "time_units": ["seconds", "second", "minutes", "minute", "hours", "hour", "days", "day"],

        # Boolean
        "boolean": ["true", "false", "yes", "no"],
    }

    # Hover documentation for keywords
    KEYWORD_DOCS: Dict[str, str] = {
        # Structure
        "transform": "**transform**: Field-level or expression-level transformation\n\nDefines a single-purpose data transformation.\n\n```\ntransform normalize_amount\n    input: decimal, required\n    output: decimal, required\n    apply\n        output = input * rate\n    end\nend\n```",
        "transform_block": "**transform_block**: Block-level multi-field transformation\n\nMaps multiple input fields to output fields, can compose other transforms.\n\n```\ntransform_block enrich_data\n    use normalize_amount end\n    input ... end\n    output ... end\n    mappings ... end\nend\n```",
        "end": "**end**: Closes a block or transform definition",

        # Metadata
        "version": "**version**: `\"X.Y.Z\"`\n\nSemantic version number for the transform.",
        "description": "**description**: `\"text\"`\n\nHuman-readable description of what the transform does.",
        "previous_version": "**previous_version**: `\"X.Y.Z\"`\n\nPrevious version for evolution tracking.",
        "compatibility": "**compatibility**: `backward | forward | full | none`\n\nSchema compatibility mode.",

        # Purity & Caching
        "pure": "**pure**: `true | false`\n\nMarks transform as having no side effects. Pure transforms are cacheable and parallelizable.",
        "cache": "**cache**: Caching configuration\n\n```\ncache\n    ttl: 1 hour\n    key: [field1, field2]\nend\n```",
        "ttl": "**ttl**: Cache time-to-live duration (e.g., `1 hour`, `30 minutes`).",
        "key": "**key**: `[field_list]`\n\nFields used as cache key.",

        # Input/Output
        "input": "**input**: Input specification\n\nSingle: `input: type, qualifiers`\nMultiple:\n```\ninput\n    field1: type1, required\n    field2: type2, nullable\nend\n```",
        "output": "**output**: Output specification\n\nSingle: `output: type, qualifiers`\nMultiple:\n```\noutput\n    field1: type1, required\n    field2: type2\nend\n```",
        "nullable": "**nullable**: Field can be null.",
        "required": "**required**: Field must have a value.",
        "default": "**default**: `expression`\n\nDefault value if input is null.",

        # Types
        "string": "**string**: Text/string type. Supports `[length: N]`, `[pattern: \"regex\"]`.",
        "integer": "**integer**: Whole number type. Supports `[range: min..max]`.",
        "decimal": "**decimal**: Decimal number type. Supports `[precision: N, scale: M]`.",
        "boolean": "**boolean**: True/false type.",
        "date": "**date**: Date without time.",
        "timestamp": "**timestamp**: Date with time.",
        "uuid": "**uuid**: Universally unique identifier.",
        "bytes": "**bytes**: Binary data.",
        "list": "**list**<T>: Ordered collection of T.",
        "set": "**set**<T>: Unordered unique collection of T.",
        "map": "**map**<K,V>: Key-value mapping.",

        # Apply & Mappings
        "apply": "**apply**: Transformation logic block\n\n```\napply\n    result = input * 2\n    output = result + offset\nend\n```",
        "mappings": "**mappings**: Field mappings for transform_block\n\n```\nmappings\n    output.field1 = input.field1\n    output.field2 = transform(input.field2)\nend\n```",
        "use": "**use**: Import other transforms for composition\n\n```\nuse transform1 transform2 end\n```",

        # Composition
        "compose": "**compose**: Transform composition\n\n```\ncompose sequential\n    transform1\n    transform2\nend\n```",
        "sequential": "**sequential**: Execute transforms in order.",
        "parallel": "**parallel**: Execute transforms concurrently.",
        "conditional": "**conditional**: Choose transform based on condition.",
        "then": "**then**: Continuation after compose block.",

        # Validation
        "validate_input": "**validate_input**: Input validation rules\n\n```\nvalidate_input\n    amount > 0: \"Amount must be positive\"\n    currency in [\"USD\", \"EUR\"]: \"Unsupported currency\"\nend\n```",
        "validate_output": "**validate_output**: Output validation rules\n\n```\nvalidate_output\n    result >= 0: message: \"Invalid\" code: \"ERR001\"\nend\n```",
        "invariant": "**invariant**: Rules that must always hold true.",
        "message": "**message**: Validation error message.",
        "code": "**code**: Validation error code.",
        "severity": "**severity**: `error | warning | info`\n\nValidation message severity.",

        # Error handling
        "on_error": "**on_error**: Error handling configuration\n\n```\non_error\n    action: reject\n    log_level: error\n    emit_to: error_stream\nend\n```",
        "action": "**action**: `reject | skip | use_default | raise`\n\nWhat to do on error.",
        "reject": "**reject**: Reject the record on error.",
        "skip": "**skip**: Skip the record on error.",
        "use_default": "**use_default**: Use default value on error.",
        "raise": "**raise**: Re-raise the error.",
        "emit_to": "**emit_to**: Send error records to specified stream.",
        "log_level": "**log_level**: `error | warning | info | debug`\n\nLogging level for errors.",

        # Recalculation
        "on_change": "**on_change**: Trigger recalculation when fields change\n\n```\non_change [field1, field2]\n    recalculate\n        output = compute(field1, field2)\n    end\nend\n```",
        "recalculate": "**recalculate**: Fields to recompute on change.",

        # Expression keywords
        "when": "**when**: Conditional expression\n\n```\nwhen condition: value\nwhen other_condition: other_value\notherwise: default_value\n```",
        "otherwise": "**otherwise**: Default case in conditional.",
        "between": "**between**: Range check (`x between a and b`).",
        "in": "**in**: Set membership (`x in [a, b, c]`).",
        "is": "**is**: Null check (`x is null`, `x is not null`).",
        "not": "**not**: Logical negation.",
        "and": "**and**: Logical AND.",
        "or": "**or**: Logical OR.",
        "null": "**null**: Null/missing value.",
    }

    def __init__(self):
        super().__init__()
        self._parser = TransformParser()
        self._all_keywords = self._flatten_keywords()

    def _flatten_keywords(self) -> List[str]:
        """Flatten all keyword categories into a single list."""
        all_kw = []
        for keywords in self.KEYWORDS.values():
            all_kw.extend(keywords)
        return list(set(all_kw))

    @property
    def language_id(self) -> str:
        return "transformdsl"

    @property
    def display_name(self) -> str:
        return "TransformDSL (L3 Transform Catalog)"

    @property
    def file_extensions(self) -> List[str]:
        return [".xform", ".transform"]

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
            rename=False,
            code_actions=False
        )

    @property
    def trigger_characters(self) -> List[str]:
        return [" ", "\n", ":", "[", "."]

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
                        severity=types.DiagnosticSeverity.Error
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
                detail="TransformDSL keyword",
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
            return ["transform", "transform_block", "end"] + self._all_keywords

        # After 'transform', suggest name then blocks
        if current_line.startswith("transform") and not current_line.startswith("transform_block"):
            return ["version", "description", "pure", "cache", "input", "output", "apply", "end"]

        # After 'transform_block', suggest blocks
        if current_line.startswith("transform_block"):
            return ["version", "description", "use", "input", "output", "mappings", "compose", "end"]

        # After 'input' or 'output', suggest types
        if "input" in current_line or "output" in current_line:
            return list(self.KEYWORDS["types"]) + list(self.KEYWORDS["io"])

        # After type declaration, suggest qualifiers and constraints
        if any(t in current_line for t in ["string", "integer", "decimal", "boolean", "timestamp"]):
            return list(self.KEYWORDS["io"]) + list(self.KEYWORDS["constraints"])

        # After 'apply' or 'mappings', suggest expression keywords
        if "apply" in content[:content.find(current_line) if current_line else 0] or \
           "mappings" in content[:content.find(current_line) if current_line else 0]:
            return list(self.KEYWORDS["expressions"])

        # After 'on_error', suggest error handling keywords
        if "on_error" in content[:content.find(current_line) if current_line else 0]:
            return list(self.KEYWORDS["error"]) + list(self.KEYWORDS["severity"])

        # After 'validate_', suggest validation keywords
        if "validate_" in content[:content.find(current_line) if current_line else 0]:
            return list(self.KEYWORDS["validation"]) + list(self.KEYWORDS["expressions"])

        # After 'compose', suggest composition keywords
        if "compose" in current_line:
            return list(self.KEYWORDS["compose"])

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
        """Extract transform definitions as document symbols."""
        symbols: List[types.DocumentSymbol] = []

        try:
            result = self._parser.parse(content)

            if result.ast:
                # Process regular transforms
                if hasattr(result.ast, 'transforms'):
                    for transform in result.ast.transforms:
                        symbol = self._create_transform_symbol(transform, content, is_block=False)
                        if symbol:
                            symbols.append(symbol)

                # Process transform blocks
                if hasattr(result.ast, 'transform_blocks'):
                    for block in result.ast.transform_blocks:
                        symbol = self._create_transform_symbol(block, content, is_block=True)
                        if symbol:
                            symbols.append(symbol)

        except Exception:
            pass

        return symbols

    def _create_transform_symbol(
        self,
        transform,
        content: str,
        is_block: bool
    ) -> Optional[types.DocumentSymbol]:
        """Create a document symbol for a transform definition."""
        try:
            name = getattr(transform, 'name', 'unknown')
            location = getattr(transform, 'location', None)

            start_line = location.line - 1 if location else 0
            end_line = start_line + 10

            # Find actual end
            lines = content.split("\n")
            depth = 0
            for i in range(start_line, min(len(lines), start_line + 200)):
                line = lines[i].strip()
                if line.startswith("transform"):
                    depth += 1
                if line == "end":
                    depth -= 1
                    if depth <= 0:
                        end_line = i
                        break

            transform_range = self.create_range(start_line, 0, end_line, 3)
            children = []

            # Add input/output as children
            if hasattr(transform, 'input_spec') and transform.input_spec:
                input_symbol = types.DocumentSymbol(
                    name="input",
                    kind=types.SymbolKind.Interface,
                    range=transform_range,
                    selection_range=transform_range,
                )
                children.append(input_symbol)

            if hasattr(transform, 'output_spec') and transform.output_spec:
                output_symbol = types.DocumentSymbol(
                    name="output",
                    kind=types.SymbolKind.Interface,
                    range=transform_range,
                    selection_range=transform_range,
                )
                children.append(output_symbol)

            symbol_kind = types.SymbolKind.Class if is_block else types.SymbolKind.Function
            detail = "transform_block" if is_block else "transform"

            return types.DocumentSymbol(
                name=name,
                kind=symbol_kind,
                range=transform_range,
                selection_range=self.create_range(start_line, 0, start_line, len(name) + 15),
                detail=detail,
                children=children if children else None
            )
        except Exception:
            return None
