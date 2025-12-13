"""
Rules DSL (L4) Parser

Parser wrapper for L4 Business Rules DSL with AST building.
Composed from modular visitor mixins for maintainability.
"""

from .base import BaseParser, ParseResult
from .generated.rules import RulesDSLLexer, RulesDSLParser, RulesDSLVisitor
from .rules import (
    RulesHelpersVisitorMixin,
    RulesCoreVisitorMixin,
    RulesDecisionTableVisitorMixin,
    RulesConditionVisitorMixin,
    RulesActionVisitorMixin,
    RulesProceduralVisitorMixin,
    RulesExpressionVisitorMixin,
    RulesLiteralVisitorMixin,
    RulesServicesVisitorMixin,
    RulesActionsVisitorMixin,
    RulesCollectionVisitorMixin,
)


class RulesASTBuilder(
    RulesHelpersVisitorMixin,
    RulesCoreVisitorMixin,
    RulesDecisionTableVisitorMixin,
    RulesConditionVisitorMixin,
    RulesActionVisitorMixin,
    RulesProceduralVisitorMixin,
    RulesExpressionVisitorMixin,
    RulesLiteralVisitorMixin,
    RulesServicesVisitorMixin,
    RulesActionsVisitorMixin,
    RulesCollectionVisitorMixin,
    RulesDSLVisitor
):
    """Visitor that builds AST from ANTLR parse tree for L4 Rules DSL.

    Composed from modular mixins:
    - RulesHelpersVisitorMixin: Common helper methods
    - RulesCoreVisitorMixin: Program-level parsing
    - RulesDecisionTableVisitorMixin: Decision tables, given/decide blocks
    - RulesConditionVisitorMixin: Condition types (range, set, pattern, etc.)
    - RulesActionVisitorMixin: Action types (assign, lookup, call, etc.)
    - RulesProceduralVisitorMixin: Procedural rules and blocks
    - RulesExpressionVisitorMixin: Boolean and value expressions
    - RulesLiteralVisitorMixin: Literal value parsing
    - RulesServicesVisitorMixin: External service declarations
    - RulesActionsVisitorMixin: Action method declarations (RFC Solution 5)
    """
    pass


class RulesParser(BaseParser):
    """Parser for L4 Business Rules DSL."""

    def parse(self, content: str) -> ParseResult:
        """Parse Rules DSL content and build AST."""
        result = ParseResult(success=True)

        try:
            parser = self._setup_parser(RulesDSLLexer, RulesDSLParser, content)
            tree = parser.program()
            self._collect_errors(result)

            if result.success:
                builder = RulesASTBuilder()
                result.ast = builder.visitProgram(tree)
                result.parse_tree = tree

        except Exception as e:
            result.add_error(f"Parsing failed: {str(e)}")

        return result
