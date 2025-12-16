# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Correlation Block Visitor Mixin for Proc Parser

Handles parsing of correlation operations: await declarations, hold declarations,
completion conditions, and timeout actions.
"""

from typing import Union

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcCorrelationVisitorMixin:
    """Mixin for correlation block visitor methods."""

    def visitCorrelationBlock(self, ctx: ProcDSLParser.CorrelationBlockContext) -> Union[ast.AwaitDecl, ast.HoldDecl]:
        if ctx.awaitDecl():
            return self.visitAwaitDecl(ctx.awaitDecl())
        elif ctx.holdDecl():
            return self.visitHoldDecl(ctx.holdDecl())
        return None

    def visitAwaitDecl(self, ctx: ProcDSLParser.AwaitDeclContext) -> ast.AwaitDecl:
        identifiers = ctx.IDENTIFIER()
        initial_event = identifiers[0].getText()
        trigger_event = identifiers[1].getText()
        matching_fields = self._get_field_list(ctx.fieldList())
        timeout = self.visitDuration(ctx.duration())
        timeout_action = self.visitTimeoutAction(ctx.timeoutAction())

        return ast.AwaitDecl(
            initial_event=initial_event,
            trigger_event=trigger_event,
            matching_fields=matching_fields,
            timeout=timeout,
            timeout_action=timeout_action,
            location=self._get_location(ctx)
        )

    def visitHoldDecl(self, ctx: ProcDSLParser.HoldDeclContext) -> ast.HoldDecl:
        identifiers = ctx.IDENTIFIER()
        event = identifiers[0].getText()

        buffer_name = None
        has_in = any(
            self._get_text(child) == 'in'
            for child in ctx.getChildren()
        )
        if has_in and len(identifiers) > 1:
            buffer_name = identifiers[1].getText()

        keyed_by = self._get_field_list(ctx.fieldList())

        completion = None
        if ctx.completionClause():
            completion = self.visitCompletionClause(ctx.completionClause())

        timeout = None
        timeout_action = None
        if ctx.duration():
            timeout = self.visitDuration(ctx.duration())
        if ctx.timeoutAction():
            timeout_action = self.visitTimeoutAction(ctx.timeoutAction())

        return ast.HoldDecl(
            event=event,
            buffer_name=buffer_name,
            keyed_by=keyed_by,
            completion=completion,
            timeout=timeout,
            timeout_action=timeout_action,
            location=self._get_location(ctx)
        )

    def visitCompletionClause(self, ctx: ProcDSLParser.CompletionClauseContext) -> ast.CompletionClause:
        condition = self.visitCompletionCondition(ctx.completionCondition())
        return ast.CompletionClause(
            condition=condition,
            location=self._get_location(ctx)
        )

    def visitCompletionCondition(self, ctx: ProcDSLParser.CompletionConditionContext) -> ast.CompletionCondition:
        condition_text = self._get_text(ctx)

        if ctx.INTEGER():
            return ast.CompletionCondition(
                condition_type=ast.CompletionConditionType.COUNT,
                count_threshold=int(ctx.INTEGER().getText()),
                location=self._get_location(ctx)
            )
        elif 'marker' in condition_text:
            return ast.CompletionCondition(
                condition_type=ast.CompletionConditionType.MARKER,
                location=self._get_location(ctx)
            )
        elif ctx.IDENTIFIER():
            return ast.CompletionCondition(
                condition_type=ast.CompletionConditionType.RULE,
                rule_name=ctx.IDENTIFIER().getText(),
                location=self._get_location(ctx)
            )

        return ast.CompletionCondition(
            condition_type=ast.CompletionConditionType.COUNT,
            location=self._get_location(ctx)
        )

    def visitTimeoutAction(self, ctx: ProcDSLParser.TimeoutActionContext) -> ast.TimeoutAction:
        action_text = self._get_text(ctx)

        if 'skip' in action_text:
            return ast.TimeoutAction(
                action_type=ast.TimeoutActionType.SKIP,
                location=self._get_location(ctx)
            )
        elif 'dead_letter' in action_text:
            target = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else None
            return ast.TimeoutAction(
                action_type=ast.TimeoutActionType.DEAD_LETTER,
                target=target,
                location=self._get_location(ctx)
            )
        else:
            target = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else None
            return ast.TimeoutAction(
                action_type=ast.TimeoutActionType.EMIT,
                target=target,
                location=self._get_location(ctx)
            )
