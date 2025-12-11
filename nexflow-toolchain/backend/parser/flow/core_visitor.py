"""
Core Visitor Mixin for Flow Parser

Handles parsing of top-level elements: program and process definition.

Updated for grammar v0.5.0+ which uses bodyContent for flexible ordering
instead of separate inputBlock/outputBlock.
"""

from typing import List, Optional

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowCoreVisitorMixin:
    """Mixin for core flow visitor methods."""

    def visitProgram(self, ctx: ProcDSLParser.ProgramContext) -> ast.Program:
        processes = []
        for proc_ctx in ctx.processDefinition():
            processes.append(self.visitProcessDefinition(proc_ctx))
        return ast.Program(
            processes=processes,
            location=self._get_location(ctx)
        )

    def visitProcessDefinition(self, ctx: ProcDSLParser.ProcessDefinitionContext) -> ast.ProcessDefinition:
        name = self._get_text(ctx.processName())

        execution = None
        if ctx.executionBlock():
            execution = self.visitExecutionBlock(ctx.executionBlock())

        # v0.5.0+: bodyContent contains receive, processing, emit, correlation, completion
        # in any order. We collect them by type.
        receives = []
        processing = []
        emits = []
        correlations = []
        completions = []

        for body_ctx in ctx.bodyContent():
            if body_ctx.receiveDecl():
                receives.append(self.visitReceiveDecl(body_ctx.receiveDecl()))
            elif body_ctx.processingBlock():
                processing.append(self.visitProcessingBlock(body_ctx.processingBlock()))
            elif body_ctx.emitDecl():
                emits.append(self.visitEmitDecl(body_ctx.emitDecl()))
            elif body_ctx.correlationBlock():
                correlations.append(self.visitCorrelationBlock(body_ctx.correlationBlock()))
            elif body_ctx.completionBlock():
                completions.append(self.visitCompletionBlock(body_ctx.completionBlock()))

        state = None
        if ctx.stateBlock():
            state = self.visitStateBlock(ctx.stateBlock())

        resilience = None
        if ctx.resilienceBlock():
            resilience = self.visitResilienceBlock(ctx.resilienceBlock())

        return ast.ProcessDefinition(
            name=name,
            execution=execution,
            receives=receives,
            processing=processing,
            emits=emits,
            correlations=correlations,
            completions=completions,
            state=state,
            resilience=resilience,
            location=self._get_location(ctx)
        )
