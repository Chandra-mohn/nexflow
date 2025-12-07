"""
Procedural Rules Visitor Mixin for Rules Parser

Handles parsing of procedural rule definitions, steps, and blocks.
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesProceduralVisitorMixin:
    """Mixin for procedural rules visitor methods."""

    def visitProceduralRuleDef(self, ctx: RulesDSLParser.ProceduralRuleDefContext) -> ast.ProceduralRuleDef:
        name_ctx = ctx.ruleName()
        if name_ctx.IDENTIFIER():
            name = name_ctx.IDENTIFIER().getText()
        elif name_ctx.DQUOTED_STRING():
            name = self._strip_quotes(name_ctx.DQUOTED_STRING().getText())
        elif name_ctx.SQUOTED_STRING():
            name = self._strip_quotes(name_ctx.SQUOTED_STRING().getText())
        else:
            name = ""

        items = []
        for item_ctx in ctx.blockItem():
            items.append(self.visitBlockItem(item_ctx))

        return ast.ProceduralRuleDef(
            name=name,
            items=items,
            location=self._get_location(ctx)
        )

    def visitBlockItem(self, ctx: RulesDSLParser.BlockItemContext) -> ast.BlockItem:
        if ctx.ruleStep():
            return self.visitRuleStep(ctx.ruleStep())
        elif ctx.actionSequence():
            return self.visitActionSequence(ctx.actionSequence())
        elif ctx.returnStatement():
            return ast.ReturnStatement(location=self._get_location(ctx))

        return ast.ReturnStatement(location=self._get_location(ctx))

    def visitRuleStep(self, ctx: RulesDSLParser.RuleStepContext) -> ast.RuleStep:
        condition = self.visitBooleanExpr(ctx.booleanExpr()[0])
        then_block = self.visitBlock(ctx.block()[0])

        elseif_branches = []
        elseif_count = len(ctx.ELSEIF()) if ctx.ELSEIF() else 0
        for i in range(elseif_count):
            elseif_condition = self.visitBooleanExpr(ctx.booleanExpr()[i + 1])
            elseif_block = self.visitBlock(ctx.block()[i + 1])
            elseif_branches.append(ast.ElseIfBranch(
                condition=elseif_condition,
                block=elseif_block,
                location=self._get_location(ctx)
            ))

        else_block = None
        if ctx.ELSE():
            else_block = self.visitBlock(ctx.block()[-1])

        return ast.RuleStep(
            condition=condition,
            then_block=then_block,
            elseif_branches=elseif_branches,
            else_block=else_block,
            location=self._get_location(ctx)
        )

    def visitBlock(self, ctx: RulesDSLParser.BlockContext) -> ast.Block:
        items = []
        for item_ctx in ctx.blockItem():
            items.append(self.visitBlockItem(item_ctx))
        return ast.Block(items=items, location=self._get_location(ctx))

    def visitActionSequence(self, ctx: RulesDSLParser.ActionSequenceContext) -> ast.ActionSequence:
        actions = []
        for action_ctx in ctx.actionCall():
            actions.append(self.visitActionCall(action_ctx))
        return ast.ActionSequence(actions=actions, location=self._get_location(ctx))

    def visitActionCall(self, ctx: RulesDSLParser.ActionCallContext) -> ast.ActionCallStmt:
        if ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()
        elif ctx.DQUOTED_STRING():
            name = self._strip_quotes(ctx.DQUOTED_STRING().getText())
        else:
            name = ""

        arguments = []
        if ctx.parameterList():
            for param_ctx in ctx.parameterList().parameter():
                arguments.append(self.visitValueExpr(param_ctx.valueExpr()))

        return ast.ActionCallStmt(
            name=name,
            arguments=arguments,
            location=self._get_location(ctx)
        )
