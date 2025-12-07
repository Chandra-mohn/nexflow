"""
Core Visitor Mixin for Flow Parser

Handles parsing of top-level elements: program and process definition.
"""

from typing import Optional

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

        input_block = None
        if ctx.inputBlock():
            input_block = self.visitInputBlock(ctx.inputBlock())

        processing = []
        for proc_block_ctx in ctx.processingBlock():
            processing.append(self.visitProcessingBlock(proc_block_ctx))

        correlation = None
        if ctx.correlationBlock():
            correlation = self.visitCorrelationBlock(ctx.correlationBlock())

        output = None
        if ctx.outputBlock():
            output = self.visitOutputBlock(ctx.outputBlock())

        completion = None
        if ctx.completionBlock():
            completion = self.visitCompletionBlock(ctx.completionBlock())

        state = None
        if ctx.stateBlock():
            state = self.visitStateBlock(ctx.stateBlock())

        resilience = None
        if ctx.resilienceBlock():
            resilience = self.visitResilienceBlock(ctx.resilienceBlock())

        return ast.ProcessDefinition(
            name=name,
            execution=execution,
            input=input_block,
            processing=processing,
            correlation=correlation,
            output=output,
            completion=completion,
            state=state,
            resilience=resilience,
            location=self._get_location(ctx)
        )
