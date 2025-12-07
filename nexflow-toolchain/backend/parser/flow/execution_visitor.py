"""
Execution Block Visitor Mixin for Flow Parser

Handles parsing of execution configuration: parallelism, partitioning,
time declarations, watermarks, and mode settings.
"""

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class FlowExecutionVisitorMixin:
    """Mixin for execution block visitor methods."""

    def visitExecutionBlock(self, ctx: ProcDSLParser.ExecutionBlockContext) -> ast.ExecutionBlock:
        parallelism = None
        parallelism_hint = False
        partition_by = None
        time_decl = None
        mode_decl = None

        if ctx.parallelismDecl():
            par_ctx = ctx.parallelismDecl()
            parallelism = int(par_ctx.INTEGER().getText())
            parallelism_hint = any(
                self._get_text(child) == 'hint'
                for child in par_ctx.getChildren()
            )

        if ctx.partitionDecl():
            partition_by = self._get_field_list(ctx.partitionDecl().fieldList())

        if ctx.timeDecl():
            time_decl = self.visitTimeDecl(ctx.timeDecl())

        if ctx.modeDecl():
            mode_decl = self.visitModeDecl(ctx.modeDecl())

        return ast.ExecutionBlock(
            parallelism=parallelism,
            parallelism_hint=parallelism_hint,
            partition_by=partition_by,
            time=time_decl,
            mode=mode_decl,
            location=self._get_location(ctx)
        )

    def visitTimeDecl(self, ctx: ProcDSLParser.TimeDeclContext) -> ast.TimeDecl:
        time_field = self.visitFieldPath(ctx.fieldPath())

        watermark = None
        if ctx.watermarkDecl():
            watermark = self.visitWatermarkDecl(ctx.watermarkDecl())

        late_data = None
        if ctx.lateDataDecl():
            late_data = self.visitLateDataDecl(ctx.lateDataDecl())

        lateness = None
        if ctx.latenessDecl():
            lateness = self.visitLatenessDecl(ctx.latenessDecl())

        return ast.TimeDecl(
            time_field=time_field,
            watermark=watermark,
            late_data=late_data,
            lateness=lateness,
            location=self._get_location(ctx)
        )

    def visitWatermarkDecl(self, ctx: ProcDSLParser.WatermarkDeclContext) -> ast.WatermarkDecl:
        duration = self.visitDuration(ctx.duration())
        return ast.WatermarkDecl(
            delay=duration,
            location=self._get_location(ctx)
        )

    def visitLateDataDecl(self, ctx: ProcDSLParser.LateDataDeclContext) -> ast.LateDataDecl:
        target = ctx.IDENTIFIER().getText()
        return ast.LateDataDecl(
            target=target,
            location=self._get_location(ctx)
        )

    def visitLatenessDecl(self, ctx: ProcDSLParser.LatenessDeclContext) -> ast.LatenessDecl:
        duration = self.visitDuration(ctx.duration())
        return ast.LatenessDecl(
            duration=duration,
            location=self._get_location(ctx)
        )

    def visitModeDecl(self, ctx: ProcDSLParser.ModeDeclContext) -> ast.ModeDecl:
        mode_type_ctx = ctx.modeType()
        micro_batch_interval = None

        mode_text = self._get_text(mode_type_ctx)
        if 'micro_batch' in mode_text:
            mode = ast.ModeType.MICRO_BATCH
            if mode_type_ctx.duration():
                micro_batch_interval = self.visitDuration(mode_type_ctx.duration())
        elif 'batch' in mode_text:
            mode = ast.ModeType.BATCH
        else:
            mode = ast.ModeType.STREAM

        return ast.ModeDecl(
            mode=mode,
            micro_batch_interval=micro_batch_interval,
            location=self._get_location(ctx)
        )
