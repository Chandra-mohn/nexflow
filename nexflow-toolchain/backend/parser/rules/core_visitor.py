"""
Core Visitor Mixin for Rules Parser

Handles program-level parsing.
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesCoreVisitorMixin:
    """Mixin for program-level visitor methods."""

    def visitProgram(self, ctx: RulesDSLParser.ProgramContext) -> ast.Program:
        decision_tables = []
        procedural_rules = []

        for child in ctx.getChildren():
            if isinstance(child, RulesDSLParser.DecisionTableDefContext):
                decision_tables.append(self.visitDecisionTableDef(child))
            elif isinstance(child, RulesDSLParser.ProceduralRuleDefContext):
                procedural_rules.append(self.visitProceduralRuleDef(child))

        return ast.Program(
            decision_tables=decision_tables,
            procedural_rules=procedural_rules,
            location=self._get_location(ctx)
        )
