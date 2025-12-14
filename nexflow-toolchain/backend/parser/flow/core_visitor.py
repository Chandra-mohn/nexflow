"""
Core Visitor Mixin for Flow Parser

Handles parsing of top-level elements: program and process definition.

Updated for grammar v0.5.0+ which uses bodyContent for flexible ordering
instead of separate inputBlock/outputBlock.

Extended for v0.6.0+ with business date, markers, and phases support.
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

        # v0.6.0+: business date calendar reference
        business_date = None
        if ctx.businessDateDecl():
            business_date = self.visitBusinessDateDecl(ctx.businessDateDecl())

        # v0.6.0+: EOD markers block
        markers = None
        if ctx.markersBlock():
            markers = self.visitMarkersBlock(ctx.markersBlock())

        # v0.6.0+: Process body can be traditional statements OR phase blocks
        receives = []
        processing = []
        emits = []
        correlations = []
        completions = []
        phases = []

        body_or_phases = ctx.processBodyOrPhases()
        if body_or_phases:
            # Check if we have phase blocks
            if body_or_phases.phaseBlock():
                for phase_ctx in body_or_phases.phaseBlock():
                    phases.append(self.visitPhaseBlock(phase_ctx))
            # Or traditional body content
            elif body_or_phases.bodyContent():
                for body_ctx in body_or_phases.bodyContent():
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
        # Grammar: processDefinition has processTailBlocks which optionally contains resilienceBlock
        if ctx.processTailBlocks() and ctx.processTailBlocks().resilienceBlock():
            resilience = self.visitResilienceBlock(ctx.processTailBlocks().resilienceBlock())

        return ast.ProcessDefinition(
            name=name,
            execution=execution,
            business_date=business_date,
            markers=markers,
            phases=phases,
            receives=receives,
            processing=processing,
            emits=emits,
            correlations=correlations,
            completions=completions,
            state=state,
            resilience=resilience,
            location=self._get_location(ctx)
        )
