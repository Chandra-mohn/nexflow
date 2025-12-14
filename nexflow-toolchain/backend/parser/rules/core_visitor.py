"""
Core Visitor Mixin for Rules Parser

Handles program-level parsing.
"""

from backend.ast import rules_ast as ast
from backend.ast.common import ImportStatement
from backend.parser.generated.rules import RulesDSLParser


class RulesCoreVisitorMixin:
    """Mixin for program-level visitor methods."""

    def visitProgram(self, ctx: RulesDSLParser.ProgramContext) -> ast.Program:
        decision_tables = []
        procedural_rules = []
        services = None
        actions = None
        imports = []

        for child in ctx.getChildren():
            if isinstance(child, RulesDSLParser.DecisionTableDefContext):
                decision_tables.append(self.visitDecisionTableDef(child))
            elif isinstance(child, RulesDSLParser.ProceduralRuleDefContext):
                procedural_rules.append(self.visitProceduralRuleDef(child))
            elif isinstance(child, RulesDSLParser.ServicesBlockContext):
                services = self.visitServicesBlock(child)
            elif isinstance(child, RulesDSLParser.ActionsBlockContext):
                actions = self.visitActionsBlock(child)
            elif isinstance(child, RulesDSLParser.ImportStatementContext):
                imports.append(self.visitImportStatement(child))

        return ast.Program(
            decision_tables=decision_tables,
            procedural_rules=procedural_rules,
            services=services,
            actions=actions,
            imports=imports,
            location=self._get_location(ctx)
        )

    def visitImportStatement(self, ctx: RulesDSLParser.ImportStatementContext) -> ImportStatement:
        """Parse an import statement."""
        path = ctx.importPath().getText()
        line = ctx.start.line if ctx.start else 0
        column = ctx.start.column if ctx.start else 0
        return ImportStatement(path=path, line=line, column=column)
