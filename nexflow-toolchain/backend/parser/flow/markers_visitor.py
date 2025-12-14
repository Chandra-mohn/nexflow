"""
Markers Visitor Mixin for Flow Parser

Handles parsing of EOD markers, phases, business date, and processing date declarations.
Added in v0.6.0+ for phase-based execution control.
Extended in v0.7.0+ for processing date support.
"""

from typing import List, Optional

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowMarkersVisitorMixin:
    """Mixin for markers and phases visitor methods."""

    def visitBusinessDateDecl(self, ctx: ProcDSLParser.BusinessDateDeclContext) -> ast.BusinessDateDecl:
        """Parse: business_date from trading_calendar"""
        calendar_name = ctx.IDENTIFIER().getText()
        return ast.BusinessDateDecl(
            calendar_name=calendar_name,
            location=self._get_location(ctx)
        )

    def visitProcessingDateDecl(self, ctx: ProcDSLParser.ProcessingDateDeclContext) -> ast.ProcessingDateDecl:
        """Parse: processing_date auto

        The processing_date declaration indicates that the system clock time
        should be captured when each record is processed.
        """
        # Currently only 'auto' mode is supported
        return ast.ProcessingDateDecl(
            mode="auto",
            location=self._get_location(ctx)
        )

    def visitMarkersBlock(self, ctx: ProcDSLParser.MarkersBlockContext) -> ast.MarkersBlock:
        """Parse: markers ... end"""
        markers = []
        for marker_ctx in ctx.markerDef():
            markers.append(self.visitMarkerDef(marker_ctx))
        return ast.MarkersBlock(
            markers=markers,
            location=self._get_location(ctx)
        )

    def visitMarkerDef(self, ctx: ProcDSLParser.MarkerDefContext) -> ast.MarkerDef:
        """Parse: eod_1: when condition"""
        name = ctx.IDENTIFIER().getText()
        condition = self.visitMarkerCondition(ctx.markerCondition())
        return ast.MarkerDef(
            name=name,
            condition=condition,
            location=self._get_location(ctx)
        )

    def visitMarkerCondition(self, ctx: ProcDSLParser.MarkerConditionContext) -> ast.AnyMarkerCondition:
        """Parse marker conditions (recursive for AND/OR)."""
        # Check for compound conditions (AND/OR)
        if ctx.AND():
            left = self.visitMarkerCondition(ctx.markerCondition(0))
            right = self.visitMarkerCondition(ctx.markerCondition(1))
            return ast.CompoundCondition(
                operator='and',
                conditions=[left, right],
                location=self._get_location(ctx)
            )
        elif ctx.OR():
            left = self.visitMarkerCondition(ctx.markerCondition(0))
            right = self.visitMarkerCondition(ctx.markerCondition(1))
            return ast.CompoundCondition(
                operator='or',
                conditions=[left, right],
                location=self._get_location(ctx)
            )
        # Parenthesized expression
        elif ctx.LPAREN():
            return self.visitMarkerCondition(ctx.markerCondition(0))
        # stream.drained condition
        elif ctx.DRAINED():
            stream_name = ctx.IDENTIFIER(0).getText()
            return ast.StreamDrainedCondition(
                stream_name=stream_name,
                location=self._get_location(ctx)
            )
        # stream.count >= N condition
        elif ctx.COUNT():
            stream_name = ctx.IDENTIFIER(0).getText()
            operator = self._get_text(ctx.comparisonOp())
            threshold = int(ctx.INTEGER().getText())
            return ast.CountThresholdCondition(
                stream_name=stream_name,
                operator=operator,
                threshold=threshold,
                location=self._get_location(ctx)
            )
        # after time_spec condition
        elif ctx.AFTER():
            time_spec = self.visitTimeSpec(ctx.timeSpec())
            return ast.TimeBasedCondition(
                time_spec=time_spec,
                location=self._get_location(ctx)
            )
        # api.service.check condition
        elif ctx.API():
            # API DOT IDENTIFIER(0) DOT IDENTIFIER(1)
            # ctx.IDENTIFIER() returns all identifiers - API has 2
            identifiers = ctx.IDENTIFIER()
            service_name = identifiers[0].getText()
            check_name = identifiers[1].getText()
            return ast.ApiCheckCondition(
                api_name='api',
                service_name=service_name,
                check_name=check_name,
                location=self._get_location(ctx)
            )
        # Simple identifier - could be signal name or marker reference
        elif ctx.IDENTIFIER() and len(ctx.IDENTIFIER()) == 1:
            name = ctx.IDENTIFIER(0).getText()
            # We can't distinguish signal from marker ref at parse time
            # Use SignalCondition as default (semantic analysis will resolve)
            return ast.SignalCondition(
                signal_name=name,
                location=self._get_location(ctx)
            )

        # Fallback - shouldn't reach here with valid grammar
        raise ValueError(f"Unknown marker condition type at {self._get_location(ctx)}")

    def visitTimeSpec(self, ctx: ProcDSLParser.TimeSpecContext) -> str:
        """Parse time specification."""
        if ctx.TIME_LITERAL():
            # Remove quotes from "18:00"
            return ctx.TIME_LITERAL().getText().strip('"')
        elif ctx.END_OF_DAY():
            return "end_of_day"
        return ctx.getText()

    def visitPhaseBlock(self, ctx: ProcDSLParser.PhaseBlockContext) -> ast.PhaseBlock:
        """Parse: phase before eod_1 ... end"""
        spec = self.visitPhaseSpec(ctx.phaseSpec())

        # Parse body content (same as traditional process body)
        statements = []
        for body_ctx in ctx.bodyContent():
            if body_ctx.receiveDecl():
                statements.append(self.visitReceiveDecl(body_ctx.receiveDecl()))
            elif body_ctx.processingBlock():
                statements.append(self.visitProcessingBlock(body_ctx.processingBlock()))
            elif body_ctx.emitDecl():
                statements.append(self.visitEmitDecl(body_ctx.emitDecl()))
            elif body_ctx.correlationBlock():
                statements.append(self.visitCorrelationBlock(body_ctx.correlationBlock()))
            elif body_ctx.completionBlock():
                statements.append(self.visitCompletionBlock(body_ctx.completionBlock()))

        # Parse on_complete clauses
        on_complete = []
        for complete_ctx in ctx.onCompleteClause():
            on_complete.append(self.visitOnCompleteClause(complete_ctx))

        return ast.PhaseBlock(
            spec=spec,
            statements=statements,
            on_complete=on_complete,
            location=self._get_location(ctx)
        )

    def visitPhaseSpec(self, ctx: ProcDSLParser.PhaseSpecContext) -> ast.PhaseSpec:
        """Parse phase specification."""
        location = self._get_location(ctx)

        if ctx.BEFORE():
            marker = ctx.IDENTIFIER(0).getText()
            return ast.PhaseSpec.before(marker, location)
        elif ctx.BETWEEN():
            start_marker = ctx.IDENTIFIER(0).getText()
            end_marker = ctx.IDENTIFIER(1).getText()
            return ast.PhaseSpec.between(start_marker, end_marker, location)
        elif ctx.AFTER():
            marker = ctx.IDENTIFIER(0).getText()
            return ast.PhaseSpec.after(marker, location)
        elif ctx.ANYTIME():
            return ast.PhaseSpec.anytime(location)

        raise ValueError(f"Unknown phase spec at {location}")

    def visitOnCompleteClause(self, ctx: ProcDSLParser.OnCompleteClauseContext) -> ast.OnCompleteClause:
        """Parse: on complete [when expr] signal name [to target]"""
        # Get signal name - it's after SIGNAL keyword
        identifiers = ctx.IDENTIFIER()
        signal_name = identifiers[0].getText()

        # Optional target (to target_name)
        target = None
        if ctx.TO() and len(identifiers) > 1:
            target = identifiers[1].getText()

        # Optional when condition
        condition = None
        if ctx.WHEN() and ctx.expression():
            # Convert expression to string for now
            condition = self._get_text(ctx.expression())

        return ast.OnCompleteClause(
            signal_name=signal_name,
            target=target,
            condition=condition,
            location=self._get_location(ctx)
        )

    def visitSignalStatement(self, ctx: ProcDSLParser.SignalStatementContext) -> ast.OnCompleteClause:
        """Parse: signal rollover to trading_calendar"""
        identifiers = ctx.IDENTIFIER()
        signal_name = identifiers[0].getText()
        target = identifiers[1].getText()

        return ast.OnCompleteClause(
            signal_name=signal_name,
            target=target,
            location=self._get_location(ctx)
        )
