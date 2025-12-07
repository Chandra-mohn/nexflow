# Generated from grammar/ProcDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ProcDSLParser import ProcDSLParser
else:
    from ProcDSLParser import ProcDSLParser

# This class defines a complete generic visitor for a parse tree produced by ProcDSLParser.

class ProcDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ProcDSLParser#program.
    def visitProgram(self, ctx:ProcDSLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processDefinition.
    def visitProcessDefinition(self, ctx:ProcDSLParser.ProcessDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processName.
    def visitProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#executionBlock.
    def visitExecutionBlock(self, ctx:ProcDSLParser.ExecutionBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#parallelismDecl.
    def visitParallelismDecl(self, ctx:ProcDSLParser.ParallelismDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#partitionDecl.
    def visitPartitionDecl(self, ctx:ProcDSLParser.PartitionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timeDecl.
    def visitTimeDecl(self, ctx:ProcDSLParser.TimeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#watermarkDecl.
    def visitWatermarkDecl(self, ctx:ProcDSLParser.WatermarkDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#lateDataDecl.
    def visitLateDataDecl(self, ctx:ProcDSLParser.LateDataDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#latenessDecl.
    def visitLatenessDecl(self, ctx:ProcDSLParser.LatenessDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#modeDecl.
    def visitModeDecl(self, ctx:ProcDSLParser.ModeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#modeType.
    def visitModeType(self, ctx:ProcDSLParser.ModeTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#inputBlock.
    def visitInputBlock(self, ctx:ProcDSLParser.InputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#receiveDecl.
    def visitReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#projectClause.
    def visitProjectClause(self, ctx:ProcDSLParser.ProjectClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#schemaDecl.
    def visitSchemaDecl(self, ctx:ProcDSLParser.SchemaDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#receiveAction.
    def visitReceiveAction(self, ctx:ProcDSLParser.ReceiveActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#storeAction.
    def visitStoreAction(self, ctx:ProcDSLParser.StoreActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#matchAction.
    def visitMatchAction(self, ctx:ProcDSLParser.MatchActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processingBlock.
    def visitProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#enrichDecl.
    def visitEnrichDecl(self, ctx:ProcDSLParser.EnrichDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#selectClause.
    def visitSelectClause(self, ctx:ProcDSLParser.SelectClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transformDecl.
    def visitTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#routeDecl.
    def visitRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#aggregateDecl.
    def visitAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#mergeDecl.
    def visitMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowDecl.
    def visitWindowDecl(self, ctx:ProcDSLParser.WindowDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowType.
    def visitWindowType(self, ctx:ProcDSLParser.WindowTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowOptions.
    def visitWindowOptions(self, ctx:ProcDSLParser.WindowOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#joinDecl.
    def visitJoinDecl(self, ctx:ProcDSLParser.JoinDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#joinType.
    def visitJoinType(self, ctx:ProcDSLParser.JoinTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#correlationBlock.
    def visitCorrelationBlock(self, ctx:ProcDSLParser.CorrelationBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#awaitDecl.
    def visitAwaitDecl(self, ctx:ProcDSLParser.AwaitDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#holdDecl.
    def visitHoldDecl(self, ctx:ProcDSLParser.HoldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#completionClause.
    def visitCompletionClause(self, ctx:ProcDSLParser.CompletionClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#completionCondition.
    def visitCompletionCondition(self, ctx:ProcDSLParser.CompletionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timeoutAction.
    def visitTimeoutAction(self, ctx:ProcDSLParser.TimeoutActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#outputBlock.
    def visitOutputBlock(self, ctx:ProcDSLParser.OutputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#outputDecl.
    def visitOutputDecl(self, ctx:ProcDSLParser.OutputDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#emitDecl.
    def visitEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fanoutDecl.
    def visitFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#completionBlock.
    def visitCompletionBlock(self, ctx:ProcDSLParser.CompletionBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#completionDecl.
    def visitCompletionDecl(self, ctx:ProcDSLParser.CompletionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onCommitDecl.
    def visitOnCommitDecl(self, ctx:ProcDSLParser.OnCommitDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onCommitFailureDecl.
    def visitOnCommitFailureDecl(self, ctx:ProcDSLParser.OnCommitFailureDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#correlationDecl.
    def visitCorrelationDecl(self, ctx:ProcDSLParser.CorrelationDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#includeDecl.
    def visitIncludeDecl(self, ctx:ProcDSLParser.IncludeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#stateBlock.
    def visitStateBlock(self, ctx:ProcDSLParser.StateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#stateDecl.
    def visitStateDecl(self, ctx:ProcDSLParser.StateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#usesDecl.
    def visitUsesDecl(self, ctx:ProcDSLParser.UsesDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#localDecl.
    def visitLocalDecl(self, ctx:ProcDSLParser.LocalDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#stateType.
    def visitStateType(self, ctx:ProcDSLParser.StateTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#ttlDecl.
    def visitTtlDecl(self, ctx:ProcDSLParser.TtlDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#ttlType.
    def visitTtlType(self, ctx:ProcDSLParser.TtlTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#cleanupDecl.
    def visitCleanupDecl(self, ctx:ProcDSLParser.CleanupDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#cleanupStrategy.
    def visitCleanupStrategy(self, ctx:ProcDSLParser.CleanupStrategyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#bufferDecl.
    def visitBufferDecl(self, ctx:ProcDSLParser.BufferDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#bufferType.
    def visitBufferType(self, ctx:ProcDSLParser.BufferTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#resilienceBlock.
    def visitResilienceBlock(self, ctx:ProcDSLParser.ResilienceBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorBlock.
    def visitErrorBlock(self, ctx:ProcDSLParser.ErrorBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorHandler.
    def visitErrorHandler(self, ctx:ProcDSLParser.ErrorHandlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorType.
    def visitErrorType(self, ctx:ProcDSLParser.ErrorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorAction.
    def visitErrorAction(self, ctx:ProcDSLParser.ErrorActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#checkpointBlock.
    def visitCheckpointBlock(self, ctx:ProcDSLParser.CheckpointBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#backpressureBlock.
    def visitBackpressureBlock(self, ctx:ProcDSLParser.BackpressureBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#backpressureStrategy.
    def visitBackpressureStrategy(self, ctx:ProcDSLParser.BackpressureStrategyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#alertDecl.
    def visitAlertDecl(self, ctx:ProcDSLParser.AlertDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fieldPath.
    def visitFieldPath(self, ctx:ProcDSLParser.FieldPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fieldList.
    def visitFieldList(self, ctx:ProcDSLParser.FieldListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#duration.
    def visitDuration(self, ctx:ProcDSLParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timeUnit.
    def visitTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        return self.visitChildren(ctx)



del ProcDSLParser