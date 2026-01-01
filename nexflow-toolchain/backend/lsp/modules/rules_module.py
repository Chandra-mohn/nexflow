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
        "structure": ["decision_table", "rule", "end", "given", "decide", "return", "execute", "import"],

        # Hit Policies
        "hit_policy": ["hit_policy", "first_match", "single_hit", "multi_hit", "collect_all"],

        # Control Flow
        "control_flow": ["if", "then", "elseif", "else", "endif", "when", "otherwise"],

        # Logic
        "logic": ["and", "or", "not", "mod"],

        # Conditions
        "conditions": [
            "in", "is", "null", "is_null", "is_not_null",
            "matches", "contains", "starts_with", "ends_with", "to"
        ],

        # EOD Marker Conditions (v0.6.0+)
        "marker_conditions": [
            "marker", "fired", "pending", "between"
        ],

        # Actions
        "actions": ["lookup", "emit", "default", "as_of"],

        # Variables
        "variables": ["let", "set"],

        # Post-processing
        "post_processing": ["post_calculate", "aggregate"],

        # Types
        "types": ["text", "number", "boolean", "date", "timestamp", "money", "percentage", "bizdate"],

        # Collection Functions
        "collection_functions": [
            "any", "all", "none", "sum", "count", "avg", "max", "min",
            "filter", "find", "distinct"
        ],

        # Services Block
        "services": ["services", "sync", "async", "cached", "timeout", "fallback", "retry"],

        # Actions Block
        "actions_block": ["actions", "state", "audit", "call"],

        # Other keywords
        "other": ["description", "priority", "yes", "multi", "version"],

        # Boolean literals
        "boolean": ["true", "false"],

        # Duration units
        "duration": ["ms", "s", "m", "h"],
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
        "mod": "**mod**: Modulo operator (remainder)\n\n`value mod 10` - remainder when divided by 10",

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

        # Import (v0.7.0+)
        "import": "**import** `path`\n\nImports definitions from another DSL file.\n\n```\nimport ../schemas/order.schema\nimport ./common_rules.rules\n```",

        # EOD Marker Conditions (v0.6.0+)
        "marker": "**marker** `name` `fired|pending`\n\nCondition based on EOD marker state.\n\n```\ndecision_table routing\n    decide:\n        | marker eod_1 fired  | action       |\n        |=====================|==============|\n        | true                | settle()     |\n        | false               | accumulate() |\n```",
        "fired": "**fired**\n\nMarker state: the marker condition has been met.\n\n```\nmarker eod_ready fired\n```",
        "pending": "**pending**\n\nMarker state: the marker condition has NOT yet been met.\n\n```\nmarker eod_ready pending\n```",
        "between": "**between** `marker1` **and** `marker2`\n\nCondition true when between two marker states.\n\n```\ndecide:\n    | between eod_1 and eod_2 | action      |\n    |========================|=============|\n    | true                   | process()   |\n```",

        # Hit Policy additions
        "collect_all": "**collect_all**\n\nCollect results from all matching rows into a list.\n\n```\ndecision_table validate_all\n    hit_policy collect_all\n    // All matching rows contribute to result\n```",

        # Control Flow additions
        "when": "**when** `condition` **then** `result`\n\nInline conditional expression.\n\n```\npost_calculate:\n    status = when score >= 700 then \"approved\" otherwise \"review\"\n```",
        "otherwise": "**otherwise**\n\nDefault branch in when expression.\n\n```\nwhen amount > 1000 then \"high\" otherwise \"normal\"\n```",

        # Variables
        "let": "**let** `var` `=` `expr`\n\nDeclares a local variable.\n\n```\nlet discount = base_price * 0.1\nlet total = base_price - discount\n```",
        "set": "**set** `var` `=` `expr`\n\nAssigns a value to a variable.\n\n```\nset result = calculate_total(items)\n```",

        # Post-processing
        "post_calculate": "**post_calculate:**\n\nDerived calculations after decision table evaluation.\n\n```\npost_calculate:\n    total_risk = credit_risk + fraud_risk\n    final_decision = when total_risk > 0.7 then \"decline\" otherwise base_decision\n```",
        "aggregate": "**aggregate:**\n\nAggregation block for collect_all results.\n\n```\naggregate:\n    total_amount = sum(amounts)\n    max_risk = max(risk_scores)\n```",

        # Types
        "bizdate": "**bizdate**\n\nBusiness date type (from L0 calendar context).\n\nRepresents logical business day.\n\n```\ngiven:\n    trade_date: bizdate\n    settlement_date: bizdate\n```",

        # Collection Functions
        "any": "**any**(`collection`, `predicate`)\n\nReturns true if any element matches predicate.\n\n```\nany(items, amount > 1000)\nany(flags, f -> f.type = \"critical\")\n```",
        "all": "**all**(`collection`, `predicate`)\n\nReturns true if all elements match predicate.\n\n```\nall(items, status = \"valid\")\n```",
        "none": "**none**(`collection`, `predicate`)\n\nReturns true if no elements match predicate.\n\n```\nnone(flags, type = \"blocked\")\n```",
        "sum": "**sum**(`collection`, `field?`)\n\nSums numeric values.\n\n```\nsum(items, amount)\nsum(scores)\n```",
        "count": "**count**(`collection`)\n\nCounts elements in collection.\n\n```\ncount(items)\n```",
        "avg": "**avg**(`collection`, `field?`)\n\nCalculates average of numeric values.\n\n```\navg(scores)\navg(items, rating)\n```",
        "max": "**max**(`collection`, `field?`)\n\nFinds maximum value.\n\n```\nmax(items, price)\n```",
        "min": "**min**(`collection`, `field?`)\n\nFinds minimum value.\n\n```\nmin(items, quantity)\n```",
        "filter": "**filter**(`collection`, `predicate`)\n\nFilters elements matching predicate.\n\n```\nfilter(items, active = true)\nfilter(transactions, t -> t.amount > 100)\n```",
        "find": "**find**(`collection`, `predicate`)\n\nFinds first element matching predicate.\n\n```\nfind(items, type = \"premium\")\n```",
        "distinct": "**distinct**(`collection`)\n\nRemoves duplicate elements.\n\n```\ndistinct(categories)\n```",

        # Services Block
        "services": "**services** `{...}`\n\nDeclares external service dependencies.\n\n```\nservices {\n    fraud_check: async FraudService.check(id: text) -> boolean\n        timeout: 5s\n        fallback: false\n}\n```",
        "sync": "**sync**\n\nSynchronous service call (blocking).",
        "async": "**async**\n\nAsynchronous service call (non-blocking).",
        "cached": "**cached**(`duration`)\n\nCaches service results for specified duration.\n\n```\ncached(5m) LookupService.get(key: text) -> text\n```",
        "timeout": "**timeout:** `duration`\n\nMaximum time to wait for service response.\n\n```\ntimeout: 5s\n```",
        "fallback": "**fallback:** `value`\n\nDefault value if service fails.\n\n```\nfallback: false\n```",
        "retry": "**retry:** `count`\n\nNumber of retry attempts on failure.\n\n```\nretry: 3\n```",

        # Actions Block
        "actions": "**actions** `{...}`\n\nDeclares action method implementations.\n\n```\nactions {\n    flag_suspicious(reason: text) -> emit to fraud_alerts\n    update_score(delta: number) -> state scores.adjust(delta)\n}\n```",
        "state": "**state** `name.operation`\n\nState store operation target.\n\n```\n-> state scores.increment\n-> state flags.add(\"suspicious\")\n```",
        "audit": "**audit**\n\nAudit logging target.\n\n```\n-> audit\n```",
        "call": "**call** `Service.method`\n\nExternal service call target.\n\n```\n-> call NotificationService.send\n```",

        # Version
        "version": "**version:** `x.y.z`\n\nDecision table version for tracking changes.\n\n```\ndecision_table routing\n    version: 1.2.0\n```",
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
