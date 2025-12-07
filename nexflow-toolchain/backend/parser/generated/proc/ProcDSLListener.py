# Generated from grammar/ProcDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ProcDSLParser import ProcDSLParser
else:
    from ProcDSLParser import ProcDSLParser

# This class defines a complete listener for a parse tree produced by ProcDSLParser.
class ProcDSLListener(ParseTreeListener):

    # Enter a parse tree produced by ProcDSLParser#program.
    def enterProgram(self, ctx:ProcDSLParser.ProgramContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#program.
    def exitProgram(self, ctx:ProcDSLParser.ProgramContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#processDefinition.
    def enterProcessDefinition(self, ctx:ProcDSLParser.ProcessDefinitionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processDefinition.
    def exitProcessDefinition(self, ctx:ProcDSLParser.ProcessDefinitionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#processName.
    def enterProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processName.
    def exitProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#executionBlock.
    def enterExecutionBlock(self, ctx:ProcDSLParser.ExecutionBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#executionBlock.
    def exitExecutionBlock(self, ctx:ProcDSLParser.ExecutionBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#parallelismDecl.
    def enterParallelismDecl(self, ctx:ProcDSLParser.ParallelismDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#parallelismDecl.
    def exitParallelismDecl(self, ctx:ProcDSLParser.ParallelismDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#partitionDecl.
    def enterPartitionDecl(self, ctx:ProcDSLParser.PartitionDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#partitionDecl.
    def exitPartitionDecl(self, ctx:ProcDSLParser.PartitionDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#timeDecl.
    def enterTimeDecl(self, ctx:ProcDSLParser.TimeDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#timeDecl.
    def exitTimeDecl(self, ctx:ProcDSLParser.TimeDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#watermarkDecl.
    def enterWatermarkDecl(self, ctx:ProcDSLParser.WatermarkDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#watermarkDecl.
    def exitWatermarkDecl(self, ctx:ProcDSLParser.WatermarkDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#lateDataDecl.
    def enterLateDataDecl(self, ctx:ProcDSLParser.LateDataDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#lateDataDecl.
    def exitLateDataDecl(self, ctx:ProcDSLParser.LateDataDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#latenessDecl.
    def enterLatenessDecl(self, ctx:ProcDSLParser.LatenessDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#latenessDecl.
    def exitLatenessDecl(self, ctx:ProcDSLParser.LatenessDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#modeDecl.
    def enterModeDecl(self, ctx:ProcDSLParser.ModeDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#modeDecl.
    def exitModeDecl(self, ctx:ProcDSLParser.ModeDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#modeType.
    def enterModeType(self, ctx:ProcDSLParser.ModeTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#modeType.
    def exitModeType(self, ctx:ProcDSLParser.ModeTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#inputBlock.
    def enterInputBlock(self, ctx:ProcDSLParser.InputBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#inputBlock.
    def exitInputBlock(self, ctx:ProcDSLParser.InputBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#receiveDecl.
    def enterReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#receiveDecl.
    def exitReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#projectClause.
    def enterProjectClause(self, ctx:ProcDSLParser.ProjectClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#projectClause.
    def exitProjectClause(self, ctx:ProcDSLParser.ProjectClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#schemaDecl.
    def enterSchemaDecl(self, ctx:ProcDSLParser.SchemaDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#schemaDecl.
    def exitSchemaDecl(self, ctx:ProcDSLParser.SchemaDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#receiveAction.
    def enterReceiveAction(self, ctx:ProcDSLParser.ReceiveActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#receiveAction.
    def exitReceiveAction(self, ctx:ProcDSLParser.ReceiveActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#storeAction.
    def enterStoreAction(self, ctx:ProcDSLParser.StoreActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#storeAction.
    def exitStoreAction(self, ctx:ProcDSLParser.StoreActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#matchAction.
    def enterMatchAction(self, ctx:ProcDSLParser.MatchActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#matchAction.
    def exitMatchAction(self, ctx:ProcDSLParser.MatchActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#processingBlock.
    def enterProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processingBlock.
    def exitProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#enrichDecl.
    def enterEnrichDecl(self, ctx:ProcDSLParser.EnrichDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#enrichDecl.
    def exitEnrichDecl(self, ctx:ProcDSLParser.EnrichDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#selectClause.
    def enterSelectClause(self, ctx:ProcDSLParser.SelectClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#selectClause.
    def exitSelectClause(self, ctx:ProcDSLParser.SelectClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transformDecl.
    def enterTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transformDecl.
    def exitTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#routeDecl.
    def enterRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#routeDecl.
    def exitRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#aggregateDecl.
    def enterAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#aggregateDecl.
    def exitAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#mergeDecl.
    def enterMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#mergeDecl.
    def exitMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#windowDecl.
    def enterWindowDecl(self, ctx:ProcDSLParser.WindowDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#windowDecl.
    def exitWindowDecl(self, ctx:ProcDSLParser.WindowDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#windowType.
    def enterWindowType(self, ctx:ProcDSLParser.WindowTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#windowType.
    def exitWindowType(self, ctx:ProcDSLParser.WindowTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#windowOptions.
    def enterWindowOptions(self, ctx:ProcDSLParser.WindowOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#windowOptions.
    def exitWindowOptions(self, ctx:ProcDSLParser.WindowOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#joinDecl.
    def enterJoinDecl(self, ctx:ProcDSLParser.JoinDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#joinDecl.
    def exitJoinDecl(self, ctx:ProcDSLParser.JoinDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#joinType.
    def enterJoinType(self, ctx:ProcDSLParser.JoinTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#joinType.
    def exitJoinType(self, ctx:ProcDSLParser.JoinTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#correlationBlock.
    def enterCorrelationBlock(self, ctx:ProcDSLParser.CorrelationBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#correlationBlock.
    def exitCorrelationBlock(self, ctx:ProcDSLParser.CorrelationBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#awaitDecl.
    def enterAwaitDecl(self, ctx:ProcDSLParser.AwaitDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#awaitDecl.
    def exitAwaitDecl(self, ctx:ProcDSLParser.AwaitDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#holdDecl.
    def enterHoldDecl(self, ctx:ProcDSLParser.HoldDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#holdDecl.
    def exitHoldDecl(self, ctx:ProcDSLParser.HoldDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#completionClause.
    def enterCompletionClause(self, ctx:ProcDSLParser.CompletionClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#completionClause.
    def exitCompletionClause(self, ctx:ProcDSLParser.CompletionClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#completionCondition.
    def enterCompletionCondition(self, ctx:ProcDSLParser.CompletionConditionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#completionCondition.
    def exitCompletionCondition(self, ctx:ProcDSLParser.CompletionConditionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#timeoutAction.
    def enterTimeoutAction(self, ctx:ProcDSLParser.TimeoutActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#timeoutAction.
    def exitTimeoutAction(self, ctx:ProcDSLParser.TimeoutActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#outputBlock.
    def enterOutputBlock(self, ctx:ProcDSLParser.OutputBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#outputBlock.
    def exitOutputBlock(self, ctx:ProcDSLParser.OutputBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#outputDecl.
    def enterOutputDecl(self, ctx:ProcDSLParser.OutputDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#outputDecl.
    def exitOutputDecl(self, ctx:ProcDSLParser.OutputDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#emitDecl.
    def enterEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#emitDecl.
    def exitEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#fanoutDecl.
    def enterFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#fanoutDecl.
    def exitFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#completionBlock.
    def enterCompletionBlock(self, ctx:ProcDSLParser.CompletionBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#completionBlock.
    def exitCompletionBlock(self, ctx:ProcDSLParser.CompletionBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#completionDecl.
    def enterCompletionDecl(self, ctx:ProcDSLParser.CompletionDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#completionDecl.
    def exitCompletionDecl(self, ctx:ProcDSLParser.CompletionDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#onCommitDecl.
    def enterOnCommitDecl(self, ctx:ProcDSLParser.OnCommitDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#onCommitDecl.
    def exitOnCommitDecl(self, ctx:ProcDSLParser.OnCommitDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#onCommitFailureDecl.
    def enterOnCommitFailureDecl(self, ctx:ProcDSLParser.OnCommitFailureDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#onCommitFailureDecl.
    def exitOnCommitFailureDecl(self, ctx:ProcDSLParser.OnCommitFailureDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#correlationDecl.
    def enterCorrelationDecl(self, ctx:ProcDSLParser.CorrelationDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#correlationDecl.
    def exitCorrelationDecl(self, ctx:ProcDSLParser.CorrelationDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#includeDecl.
    def enterIncludeDecl(self, ctx:ProcDSLParser.IncludeDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#includeDecl.
    def exitIncludeDecl(self, ctx:ProcDSLParser.IncludeDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#stateBlock.
    def enterStateBlock(self, ctx:ProcDSLParser.StateBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#stateBlock.
    def exitStateBlock(self, ctx:ProcDSLParser.StateBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#stateDecl.
    def enterStateDecl(self, ctx:ProcDSLParser.StateDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#stateDecl.
    def exitStateDecl(self, ctx:ProcDSLParser.StateDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#usesDecl.
    def enterUsesDecl(self, ctx:ProcDSLParser.UsesDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#usesDecl.
    def exitUsesDecl(self, ctx:ProcDSLParser.UsesDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#localDecl.
    def enterLocalDecl(self, ctx:ProcDSLParser.LocalDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#localDecl.
    def exitLocalDecl(self, ctx:ProcDSLParser.LocalDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#stateType.
    def enterStateType(self, ctx:ProcDSLParser.StateTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#stateType.
    def exitStateType(self, ctx:ProcDSLParser.StateTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#ttlDecl.
    def enterTtlDecl(self, ctx:ProcDSLParser.TtlDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#ttlDecl.
    def exitTtlDecl(self, ctx:ProcDSLParser.TtlDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#ttlType.
    def enterTtlType(self, ctx:ProcDSLParser.TtlTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#ttlType.
    def exitTtlType(self, ctx:ProcDSLParser.TtlTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#cleanupDecl.
    def enterCleanupDecl(self, ctx:ProcDSLParser.CleanupDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#cleanupDecl.
    def exitCleanupDecl(self, ctx:ProcDSLParser.CleanupDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#cleanupStrategy.
    def enterCleanupStrategy(self, ctx:ProcDSLParser.CleanupStrategyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#cleanupStrategy.
    def exitCleanupStrategy(self, ctx:ProcDSLParser.CleanupStrategyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#bufferDecl.
    def enterBufferDecl(self, ctx:ProcDSLParser.BufferDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#bufferDecl.
    def exitBufferDecl(self, ctx:ProcDSLParser.BufferDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#bufferType.
    def enterBufferType(self, ctx:ProcDSLParser.BufferTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#bufferType.
    def exitBufferType(self, ctx:ProcDSLParser.BufferTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#resilienceBlock.
    def enterResilienceBlock(self, ctx:ProcDSLParser.ResilienceBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#resilienceBlock.
    def exitResilienceBlock(self, ctx:ProcDSLParser.ResilienceBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#errorBlock.
    def enterErrorBlock(self, ctx:ProcDSLParser.ErrorBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#errorBlock.
    def exitErrorBlock(self, ctx:ProcDSLParser.ErrorBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#errorHandler.
    def enterErrorHandler(self, ctx:ProcDSLParser.ErrorHandlerContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#errorHandler.
    def exitErrorHandler(self, ctx:ProcDSLParser.ErrorHandlerContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#errorType.
    def enterErrorType(self, ctx:ProcDSLParser.ErrorTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#errorType.
    def exitErrorType(self, ctx:ProcDSLParser.ErrorTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#errorAction.
    def enterErrorAction(self, ctx:ProcDSLParser.ErrorActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#errorAction.
    def exitErrorAction(self, ctx:ProcDSLParser.ErrorActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#checkpointBlock.
    def enterCheckpointBlock(self, ctx:ProcDSLParser.CheckpointBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#checkpointBlock.
    def exitCheckpointBlock(self, ctx:ProcDSLParser.CheckpointBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#backpressureBlock.
    def enterBackpressureBlock(self, ctx:ProcDSLParser.BackpressureBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#backpressureBlock.
    def exitBackpressureBlock(self, ctx:ProcDSLParser.BackpressureBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#backpressureStrategy.
    def enterBackpressureStrategy(self, ctx:ProcDSLParser.BackpressureStrategyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#backpressureStrategy.
    def exitBackpressureStrategy(self, ctx:ProcDSLParser.BackpressureStrategyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#alertDecl.
    def enterAlertDecl(self, ctx:ProcDSLParser.AlertDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#alertDecl.
    def exitAlertDecl(self, ctx:ProcDSLParser.AlertDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#fieldPath.
    def enterFieldPath(self, ctx:ProcDSLParser.FieldPathContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#fieldPath.
    def exitFieldPath(self, ctx:ProcDSLParser.FieldPathContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#fieldList.
    def enterFieldList(self, ctx:ProcDSLParser.FieldListContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#fieldList.
    def exitFieldList(self, ctx:ProcDSLParser.FieldListContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#duration.
    def enterDuration(self, ctx:ProcDSLParser.DurationContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#duration.
    def exitDuration(self, ctx:ProcDSLParser.DurationContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#timeUnit.
    def enterTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#timeUnit.
    def exitTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        pass



del ProcDSLParser