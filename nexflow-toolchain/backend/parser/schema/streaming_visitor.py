"""
Streaming Block Visitor Mixin

Handles parsing of streaming configuration: watermarks, time semantics,
late data handling, sparsity, and retention options.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class StreamingVisitorMixin:
    """Mixin for streaming block visitor methods."""

    def visitStreamingBlock(self, ctx: SchemaDSLParser.StreamingBlockContext) -> ast.StreamingBlock:
        streaming = ast.StreamingBlock(location=self._get_location(ctx))
        for decl_ctx in ctx.streamingDecl():
            self._process_streaming_decl(decl_ctx, streaming)
        return streaming

    def _process_streaming_decl(self, ctx: SchemaDSLParser.StreamingDeclContext,
                                 streaming: ast.StreamingBlock):
        if ctx.keyFieldsDecl():
            streaming.key_fields = self.visitKeyFieldsDecl(ctx.keyFieldsDecl())
        elif ctx.timeFieldDecl():
            streaming.time_field = self.visitTimeFieldDecl(ctx.timeFieldDecl())
        elif ctx.timeSemanticsDecl():
            streaming.time_semantics = self.visitTimeSemanticsDecl(ctx.timeSemanticsDecl())
        elif ctx.watermarkDecl():
            self._process_watermark_decl(ctx.watermarkDecl(), streaming)
        elif ctx.lateDataDecl():
            self._process_late_data_decl(ctx.lateDataDecl(), streaming)
        elif ctx.allowedLatenessDecl():
            streaming.allowed_lateness = self.visitAllowedLatenessDecl(ctx.allowedLatenessDecl())
        elif ctx.idleDecl():
            self._process_idle_decl(ctx.idleDecl(), streaming)
        elif ctx.sparsityDecl():
            streaming.sparsity = self.visitSparsityDecl(ctx.sparsityDecl())
        elif ctx.retentionBlockDecl():
            streaming.retention = self.visitRetentionBlockDecl(ctx.retentionBlockDecl())

    def visitKeyFieldsDecl(self, ctx: SchemaDSLParser.KeyFieldsDeclContext) -> List[str]:
        return self._get_field_list(ctx.fieldArray())

    def visitTimeFieldDecl(self, ctx: SchemaDSLParser.TimeFieldDeclContext) -> ast.FieldPath:
        return self.visitFieldPath(ctx.fieldPath())

    def visitTimeSemanticsDecl(self, ctx: SchemaDSLParser.TimeSemanticsDeclContext) -> ast.TimeSemantics:
        semantics_text = self._get_text(ctx.timeSemanticsType()).lower()
        semantics_map = {
            'event_time': ast.TimeSemantics.EVENT_TIME,
            'processing_time': ast.TimeSemantics.PROCESSING_TIME,
            'ingestion_time': ast.TimeSemantics.INGESTION_TIME,
        }
        return semantics_map.get(semantics_text, ast.TimeSemantics.EVENT_TIME)

    def _process_watermark_decl(self, ctx: SchemaDSLParser.WatermarkDeclContext,
                                 streaming: ast.StreamingBlock):
        if ctx.duration():
            streaming.watermark_delay = self.visitDuration(ctx.duration())
        if ctx.watermarkStrategy():
            streaming.watermark_strategy = self.visitWatermarkStrategy(ctx.watermarkStrategy())

    def visitWatermarkStrategy(self, ctx: SchemaDSLParser.WatermarkStrategyContext) -> ast.WatermarkStrategy:
        strategy_text = self._get_text(ctx).lower()
        strategy_map = {
            'bounded_out_of_orderness': ast.WatermarkStrategy.BOUNDED_OUT_OF_ORDERNESS,
            'periodic': ast.WatermarkStrategy.PERIODIC,
            'punctuated': ast.WatermarkStrategy.PUNCTUATED,
        }
        return strategy_map.get(strategy_text, ast.WatermarkStrategy.BOUNDED_OUT_OF_ORDERNESS)

    def _process_late_data_decl(self, ctx: SchemaDSLParser.LateDataDeclContext,
                                 streaming: ast.StreamingBlock):
        if ctx.lateDataStrategy():
            streaming.late_data_handling = self.visitLateDataStrategy(ctx.lateDataStrategy())
        if ctx.IDENTIFIER():
            streaming.late_data_stream = ctx.IDENTIFIER().getText()

    def visitLateDataStrategy(self, ctx: SchemaDSLParser.LateDataStrategyContext) -> ast.LateDataStrategy:
        strategy_text = self._get_text(ctx).lower()
        strategy_map = {
            'side_output': ast.LateDataStrategy.SIDE_OUTPUT,
            'drop': ast.LateDataStrategy.DROP,
            'update': ast.LateDataStrategy.UPDATE,
        }
        return strategy_map.get(strategy_text, ast.LateDataStrategy.SIDE_OUTPUT)

    def visitAllowedLatenessDecl(self, ctx: SchemaDSLParser.AllowedLatenessDeclContext) -> ast.Duration:
        return self.visitDuration(ctx.duration())

    def _process_idle_decl(self, ctx: SchemaDSLParser.IdleDeclContext,
                            streaming: ast.StreamingBlock):
        if ctx.duration():
            streaming.idle_timeout = self.visitDuration(ctx.duration())
        if ctx.idleBehavior():
            streaming.idle_behavior = self.visitIdleBehavior(ctx.idleBehavior())

    def visitIdleBehavior(self, ctx: SchemaDSLParser.IdleBehaviorContext) -> ast.IdleBehavior:
        behavior_text = self._get_text(ctx).lower()
        behavior_map = {
            'mark_idle': ast.IdleBehavior.MARK_IDLE,
            'advance_to_infinity': ast.IdleBehavior.ADVANCE_TO_INFINITY,
            'keep_waiting': ast.IdleBehavior.KEEP_WAITING,
        }
        return behavior_map.get(behavior_text, ast.IdleBehavior.MARK_IDLE)

    def visitSparsityDecl(self, ctx: SchemaDSLParser.SparsityDeclContext) -> ast.SparsityBlock:
        sparsity = ast.SparsityBlock(location=self._get_location(ctx))
        if ctx.sparsityBlock():
            pass  # Simplified - parse block contents if needed
        return sparsity

    def visitRetentionBlockDecl(self, ctx: SchemaDSLParser.RetentionBlockDeclContext) -> ast.RetentionOptions:
        options = ast.RetentionOptions(location=self._get_location(ctx))
        if ctx.retentionOptions():
            opts_ctx = ctx.retentionOptions()
            if opts_ctx.duration():
                options.time = self.visitDuration(opts_ctx.duration())
            if opts_ctx.sizeSpec():
                options.size = self.visitSizeSpec(opts_ctx.sizeSpec())
            if opts_ctx.retentionPolicy():
                options.policy = self.visitRetentionPolicy(opts_ctx.retentionPolicy())
        return options

    def visitRetentionPolicy(self, ctx: SchemaDSLParser.RetentionPolicyContext) -> ast.RetentionPolicy:
        policy_text = self._get_text(ctx).lower()
        policy_map = {
            'delete_oldest': ast.RetentionPolicy.DELETE_OLDEST,
            'archive': ast.RetentionPolicy.ARCHIVE,
            'compact': ast.RetentionPolicy.COMPACT,
        }
        return policy_map.get(policy_text, ast.RetentionPolicy.DELETE_OLDEST)
