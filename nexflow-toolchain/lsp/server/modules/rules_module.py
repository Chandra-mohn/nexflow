"""
L4 RulesDSL Language Module

Provides Language Server Protocol support for RulesDSL (Business Rules DSL).
Handles .rules files with syntax validation, completions, symbols, and hover.
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
from backend.parser.rules_parser import RulesParser
from backend.parser.base import ParseResult


class RulesModule(LanguageModule):
    """
    Language module for L4 RulesDSL (Business Rules DSL).

    Supports:
    - Real-time diagnostics (parse errors)
    - Keyword completion
    - Document symbols (decision tables, procedural rules)
    - Hover documentation for keywords

    File extensions: .rules
    """

    # RulesDSL keywords organized by category
    KEYWORDS = {
        # Structure
        "structure": ["decision_table", "rule", "end", "given", "decide", "return", "execute"],

        # Hit Policies
        "hit_policy": ["hit_policy", "first_match", "single_hit", "multi_hit"],

        # Control Flow
        "control_flow": ["if", "then", "elseif", "else", "endif"],

        # Logic
        "logic": ["and", "or", "not"],

        # Conditions
        "conditions": [
            "in", "is", "null", "is_null", "is_not_null",
            "matches", "contains", "starts_with", "ends_with", "to"
        ],

        # Actions
        "actions": ["lookup", "emit", "default", "as_of"],

        # Types
        "types": ["text", "number", "boolean", "date", "timestamp", "money", "percentage"],

        # Other keywords
        "other": ["description", "priority", "yes", "multi"],

        # Boolean literals
        "boolean": ["true", "false"],
    }

    # Hover documentation for keywords
    KEYWORD_DOCS: Dict[str, str] = {
        # Structure
        "decision_table": "**decision_table**: Matrix-based business rule definition\n\nDefines a decision matrix with conditions and actions.\n\n```\ndecision_table route_transaction\n    hit_policy first_match\n    given:\n        score: number\n        status: text\n    decide:\n        | score   | status   | action       |\n        |=========|==========|==============|\n        | >= 700  | *        | approve()    |\n        | 600-699 | 'active' | review()     |\n        | *       | *        | decline()    |\n    return:\n        result: text\nend\n```",
        "rule": "**rule**: Procedural business rule with if-then-else logic\n\nDefines a rule with procedural control flow.\n\n```\nrule route_by_score:\n    if score >= 750 then\n        route_to_premium()\n    elseif score >= 650 and score < 750 then\n        route_to_standard()\n    else\n        route_to_review()\n    endif\nend\n```",
        "end": "**end**: Closes a rule or decision table definition",
        "given": "**given**: Input parameter specification block\n\n```\ngiven:\n    score: number     // Credit score\n    amount: money     // Transaction amount\n    status: text      // Account status\n```",
        "decide": "**decide**: Decision matrix block containing condition/action rows\n\n```\ndecide:\n    | condition1 | condition2 | action     |\n    |============|============|============|\n    | >= 700     | 'active'   | approve()  |\n    | *          | *          | review()   |\n```",
        "return": "**return**: Output specification for decision table\n\n```\nreturn:\n    result: text\n    score: number\n```",
        "execute": "**execute**: Execution mode specification\n\n`yes` - Execute matching actions\n`multi` - Execute all matching rows",

        # Hit Policies
        "hit_policy": "**hit_policy**: How to handle multiple matching rows\n\n- `first_match`: Stop at first matching row (default)\n- `single_hit`: Error if multiple rows match\n- `multi_hit`: Execute all matching rows",
        "first_match": "**first_match**: Stop at first matching row (default policy)\n\nRows are evaluated top-to-bottom, first match wins.",
        "single_hit": "**single_hit**: Error if multiple rows match\n\nEnsures exactly one row matches for any input combination.",
        "multi_hit": "**multi_hit**: Execute all matching rows\n\nAll rows that match will have their actions executed.",

        # Control Flow
        "if": "**if**: Start a conditional block\n\n```\nif condition then\n    action()\nendif\n```",
        "then": "**then**: Begins the action block after condition",
        "elseif": "**elseif**: Alternative condition in if-then chain\n\n```\nif score >= 750 then\n    premium()\nelseif score >= 650 then\n    standard()\nelse\n    review()\nendif\n```",
        "else": "**else**: Default branch when no conditions match",
        "endif": "**endif**: Closes an if-then-elseif-else block",

        # Logic
        "and": "**and**: Logical AND operator\n\n`score >= 650 and status = 'active'`",
        "or": "**or**: Logical OR operator\n\n`status = 'vip' or score >= 800`",
        "not": "**not**: Logical NOT operator\n\n`not is_blocked`",

        # Conditions
        "in": "**in**: Set membership condition\n\n`status in ('active', 'pending', 'review')`\n`status not in ('closed', 'suspended')`",
        "is": "**is**: Null check operator\n\n`field is null` - Check if field is null\n`field is not null` - Check if field has value",
        "null": "**null**: Null/missing value literal",
        "is_null": "**is_null**: Check if value is null\n\n`value is_null` in conditions",
        "is_not_null": "**is_not_null**: Check if value is not null\n\n`value is_not_null` in conditions",
        "matches": "**matches**: Pattern match condition\n\n`field matches \"regex_pattern\"`",
        "contains": "**contains**: Substring check\n\n`field contains \"substring\"`",
        "starts_with": "**starts_with**: Prefix check\n\n`field starts_with \"prefix\"`",
        "ends_with": "**ends_with**: Suffix check\n\n`field ends_with \"suffix\"`",
        "to": "**to**: Inclusive range operator\n\n`600 to 699` means 600 <= value <= 699\n`$100 to $500` for money ranges",

        # Actions
        "lookup": "**lookup**: Table lookup action\n\n```\nlookup(table_name, key_value)\nlookup(rates, as_of: transaction_date)\nlookup(table, key, default: fallback)\n```",
        "emit": "**emit**: Emit to output stream\n\n`emit to stream_name`",
        "default": "**default**: Default value for lookup\n\n`lookup(table, key, default: fallback_value)`",
        "as_of": "**as_of**: Point-in-time lookup\n\n`lookup(rates, as_of: effective_date)`",

        # Types
        "text": "**text**: String/text type for textual data",
        "number": "**number**: Numeric type for integers and decimals",
        "boolean": "**boolean**: True/false type",
        "date": "**date**: Date without time component",
        "timestamp": "**timestamp**: Date with time component",
        "money": "**money**: Currency type with $ prefix\n\n`$100`, `$1,000.50`",
        "percentage": "**percentage**: Percentage type with % suffix\n\n`5%`, `12.5%`",

        # Other
        "description": "**description**: Human-readable description of the rule or table\n\n`description \"Validates credit transactions\"`",
        "priority": "**priority**: Row priority in decision table (lower = higher priority)\n\nUsed for conflict resolution when multiple rows match.",
        "yes": "**yes**: Boolean true value / execute mode indicator",
        "multi": "**multi**: Execute all matching rows mode",

        # Special
        "*": "**\\***: Wildcard - matches any value\n\nUsed in conditions (any input) and actions (no action).",
    }

    def __init__(self):
        super().__init__()
        self._parser = RulesParser()
        self._all_keywords = self._flatten_keywords()

    def _flatten_keywords(self) -> List[str]:
        """Flatten all keyword categories into a single list."""
        all_kw = []
        for keywords in self.KEYWORDS.values():
            all_kw.extend(keywords)
        return list(set(all_kw))

    @property
    def language_id(self) -> str:
        return "rulesdsl"

    @property
    def display_name(self) -> str:
        return "RulesDSL (L4 Business Rules)"

    @property
    def file_extensions(self) -> List[str]:
        return [".rules"]

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
        return [" ", "\n", ":", "|", "(", ","]

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
                detail="RulesDSL keyword",
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
            return ["decision_table", "rule", "end"] + self._all_keywords

        # After 'decision_table', suggest structure keywords
        if current_line.startswith("decision_table"):
            return ["hit_policy", "description", "given", "decide", "return", "execute", "end"]

        # After 'hit_policy', suggest policy types
        if "hit_policy" in current_line:
            return list(self.KEYWORDS["hit_policy"])[1:]  # Skip 'hit_policy' itself

        # After 'rule', suggest control flow
        if current_line.startswith("rule"):
            return ["if", "then", "elseif", "else", "endif", "end"] + list(self.KEYWORDS["logic"])

        # Inside 'given' block, suggest types
        if "given" in content[:content.find(current_line) if current_line else 0]:
            return list(self.KEYWORDS["types"])

        # Inside 'if' statement, suggest logic and condition keywords
        if "if" in current_line or "elseif" in current_line:
            return list(self.KEYWORDS["logic"]) + list(self.KEYWORDS["conditions"])

        # Inside 'decide' block, suggest condition and action keywords
        if "decide" in content[:content.find(current_line) if current_line else 0]:
            return list(self.KEYWORDS["conditions"]) + list(self.KEYWORDS["actions"])

        # After 'lookup', suggest lookup-related keywords
        if "lookup" in current_line:
            return ["default", "as_of"]

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
        """Extract decision tables and procedural rules as document symbols."""
        symbols: List[types.DocumentSymbol] = []

        try:
            result = self._parser.parse(content)

            if result.ast:
                # Process decision tables
                if hasattr(result.ast, 'decision_tables'):
                    for table in result.ast.decision_tables:
                        symbol = self._create_decision_table_symbol(table, content)
                        if symbol:
                            symbols.append(symbol)

                # Process procedural rules
                if hasattr(result.ast, 'procedural_rules'):
                    for rule in result.ast.procedural_rules:
                        symbol = self._create_rule_symbol(rule, content)
                        if symbol:
                            symbols.append(symbol)

        except Exception:
            pass

        return symbols

    def _create_decision_table_symbol(
        self,
        table,
        content: str
    ) -> Optional[types.DocumentSymbol]:
        """Create a document symbol for a decision table."""
        try:
            name = getattr(table, 'name', 'unknown')
            location = getattr(table, 'location', None)

            start_line = location.line - 1 if location else 0
            end_line = self._find_end_line(content, start_line)

            table_range = self.create_range(start_line, 0, end_line, 3)
            children = []

            # Add given block as child if present
            if hasattr(table, 'given') and table.given:
                children.append(types.DocumentSymbol(
                    name="given",
                    kind=types.SymbolKind.Interface,
                    range=table_range,
                    selection_range=table_range,
                ))

            # Add decide block as child if present
            if hasattr(table, 'decide') and table.decide:
                children.append(types.DocumentSymbol(
                    name="decide",
                    kind=types.SymbolKind.Array,
                    range=table_range,
                    selection_range=table_range,
                ))

            # Add return block as child if present
            if hasattr(table, 'return_spec') and table.return_spec:
                children.append(types.DocumentSymbol(
                    name="return",
                    kind=types.SymbolKind.Interface,
                    range=table_range,
                    selection_range=table_range,
                ))

            return types.DocumentSymbol(
                name=name,
                kind=types.SymbolKind.Class,
                range=table_range,
                selection_range=self.create_range(start_line, 0, start_line, len(name) + 20),
                detail="decision_table",
                children=children if children else None
            )
        except Exception:
            return None

    def _create_rule_symbol(
        self,
        rule,
        content: str
    ) -> Optional[types.DocumentSymbol]:
        """Create a document symbol for a procedural rule."""
        try:
            name = getattr(rule, 'name', 'unknown')
            location = getattr(rule, 'location', None)

            start_line = location.line - 1 if location else 0
            end_line = self._find_end_line(content, start_line)

            rule_range = self.create_range(start_line, 0, end_line, 3)

            return types.DocumentSymbol(
                name=name,
                kind=types.SymbolKind.Function,
                range=rule_range,
                selection_range=self.create_range(start_line, 0, start_line, len(name) + 10),
                detail="rule"
            )
        except Exception:
            return None

    def _find_end_line(self, content: str, start_line: int) -> int:
        """Find the line number of the 'end' keyword for a block starting at start_line."""
        lines = content.split("\n")
        depth = 0

        for i in range(start_line, min(len(lines), start_line + 500)):
            line = lines[i].strip().lower()

            # Count block openers
            if line.startswith("decision_table") or line.startswith("rule"):
                depth += 1
            # Count block closers
            if line == "end":
                depth -= 1
                if depth <= 0:
                    return i

        # Default to reasonable end
        return min(start_line + 50, len(lines) - 1)
