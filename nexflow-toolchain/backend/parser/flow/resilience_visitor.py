# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Resilience Block Visitor Mixin for Flow Parser

Handles parsing of resilience configuration: error handling, checkpointing,
backpressure strategies, and alerting.
"""

from typing import Optional, Tuple

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowResilienceVisitorMixin:
    """Mixin for resilience block visitor methods."""

    def visitResilienceBlock(self, ctx: ProcDSLParser.ResilienceBlockContext) -> ast.ResilienceBlock:
        error = None
        checkpoint = None
        backpressure = None

        if ctx.errorBlock():
            error = self.visitErrorBlock(ctx.errorBlock())
        if ctx.checkpointBlock():
            checkpoint = self.visitCheckpointBlock(ctx.checkpointBlock())
        if ctx.backpressureBlock():
            backpressure = self.visitBackpressureBlock(ctx.backpressureBlock())

        return ast.ResilienceBlock(
            error=error,
            checkpoint=checkpoint,
            backpressure=backpressure,
            location=self._get_location(ctx)
        )

    def visitErrorBlock(self, ctx: ProcDSLParser.ErrorBlockContext) -> ast.ErrorBlock:
        handlers = []
        for handler_ctx in ctx.errorHandler():
            handlers.append(self.visitErrorHandler(handler_ctx))
        return ast.ErrorBlock(
            handlers=handlers,
            location=self._get_location(ctx)
        )

    def visitErrorHandler(self, ctx: ProcDSLParser.ErrorHandlerContext) -> ast.ErrorHandler:
        error_type = self.visitErrorType(ctx.errorType())
        action = self.visitErrorAction(ctx.errorAction())
        return ast.ErrorHandler(
            error_type=error_type,
            action=action,
            location=self._get_location(ctx)
        )

    def visitErrorType(self, ctx: ProcDSLParser.ErrorTypeContext) -> ast.ErrorType:
        type_text = self._get_text(ctx).lower()
        if 'transform' in type_text:
            return ast.ErrorType.TRANSFORM_FAILURE
        elif 'lookup' in type_text:
            return ast.ErrorType.LOOKUP_FAILURE
        elif 'rule' in type_text:
            return ast.ErrorType.RULE_FAILURE
        elif 'correlation' in type_text:
            return ast.ErrorType.CORRELATION_FAILURE
        return ast.ErrorType.TRANSFORM_FAILURE

    def visitErrorAction(self, ctx: ProcDSLParser.ErrorActionContext) -> ast.ErrorAction:
        action_text = self._get_text(ctx)

        if 'skip' in action_text:
            return ast.ErrorAction(
                action_type=ast.ErrorActionType.SKIP,
                location=self._get_location(ctx)
            )
        elif 'retry' in action_text:
            retry_count = int(ctx.INTEGER().getText()) if ctx.INTEGER() else 3
            return ast.ErrorAction(
                action_type=ast.ErrorActionType.RETRY,
                retry_count=retry_count,
                location=self._get_location(ctx)
            )
        else:
            target = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else None
            return ast.ErrorAction(
                action_type=ast.ErrorActionType.DEAD_LETTER,
                target=target,
                location=self._get_location(ctx)
            )

    def visitCheckpointBlock(self, ctx: ProcDSLParser.CheckpointBlockContext) -> ast.CheckpointBlock:
        interval = self.visitDuration(ctx.duration())
        storage = ctx.IDENTIFIER().getText()
        return ast.CheckpointBlock(
            interval=interval,
            storage=storage,
            location=self._get_location(ctx)
        )

    def visitBackpressureBlock(self, ctx: ProcDSLParser.BackpressureBlockContext) -> ast.BackpressureBlock:
        strategy, sample_rate = self.visitBackpressureStrategy(ctx.backpressureStrategy())

        alert = None
        if ctx.alertDecl():
            alert = self.visitAlertDecl(ctx.alertDecl())

        return ast.BackpressureBlock(
            strategy=strategy,
            sample_rate=sample_rate,
            alert=alert,
            location=self._get_location(ctx)
        )

    def visitBackpressureStrategy(self, ctx: ProcDSLParser.BackpressureStrategyContext) -> Tuple[ast.BackpressureStrategy, Optional[float]]:
        strategy_text = self._get_text(ctx).lower()
        sample_rate = None

        if 'drop' in strategy_text:
            strategy = ast.BackpressureStrategy.DROP
        elif 'sample' in strategy_text:
            strategy = ast.BackpressureStrategy.SAMPLE
            if ctx.NUMBER():
                sample_rate = float(ctx.NUMBER().getText())
        else:
            strategy = ast.BackpressureStrategy.BLOCK

        return strategy, sample_rate

    def visitAlertDecl(self, ctx: ProcDSLParser.AlertDeclContext) -> ast.AlertDecl:
        after = self.visitDuration(ctx.duration())
        return ast.AlertDecl(
            after=after,
            location=self._get_location(ctx)
        )
