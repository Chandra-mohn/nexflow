# Generated from ProcDSL.g4 by ANTLR 4.13.2
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


    # Visit a parse tree produced by ProcDSLParser#importStatement.
    def visitImportStatement(self, ctx:ProcDSLParser.ImportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#importPath.
    def visitImportPath(self, ctx:ProcDSLParser.ImportPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#importPathSegment.
    def visitImportPathSegment(self, ctx:ProcDSLParser.ImportPathSegmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#importFileExtension.
    def visitImportFileExtension(self, ctx:ProcDSLParser.ImportFileExtensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processDefinition.
    def visitProcessDefinition(self, ctx:ProcDSLParser.ProcessDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processBodyOrPhases.
    def visitProcessBodyOrPhases(self, ctx:ProcDSLParser.ProcessBodyOrPhasesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processTailBlocks.
    def visitProcessTailBlocks(self, ctx:ProcDSLParser.ProcessTailBlocksContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#bodyContent.
    def visitBodyContent(self, ctx:ProcDSLParser.BodyContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processName.
    def visitProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processingBlock.
    def visitProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
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


    # Visit a parse tree produced by ProcDSLParser#businessDateDecl.
    def visitBusinessDateDecl(self, ctx:ProcDSLParser.BusinessDateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#processingDateDecl.
    def visitProcessingDateDecl(self, ctx:ProcDSLParser.ProcessingDateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#markersBlock.
    def visitMarkersBlock(self, ctx:ProcDSLParser.MarkersBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#markerDef.
    def visitMarkerDef(self, ctx:ProcDSLParser.MarkerDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#markerCondition.
    def visitMarkerCondition(self, ctx:ProcDSLParser.MarkerConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timeSpec.
    def visitTimeSpec(self, ctx:ProcDSLParser.TimeSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#phaseBlock.
    def visitPhaseBlock(self, ctx:ProcDSLParser.PhaseBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#phaseSpec.
    def visitPhaseSpec(self, ctx:ProcDSLParser.PhaseSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onCompleteClause.
    def visitOnCompleteClause(self, ctx:ProcDSLParser.OnCompleteClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#signalStatement.
    def visitSignalStatement(self, ctx:ProcDSLParser.SignalStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#stateMachineDecl.
    def visitStateMachineDecl(self, ctx:ProcDSLParser.StateMachineDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#persistenceDecl.
    def visitPersistenceDecl(self, ctx:ProcDSLParser.PersistenceDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#checkpointDecl.
    def visitCheckpointDecl(self, ctx:ProcDSLParser.CheckpointDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#receiveDecl.
    def visitReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#receiveClause.
    def visitReceiveClause(self, ctx:ProcDSLParser.ReceiveClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#connectorClause.
    def visitConnectorClause(self, ctx:ProcDSLParser.ConnectorClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#connectorType.
    def visitConnectorType(self, ctx:ProcDSLParser.ConnectorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#connectorConfig.
    def visitConnectorConfig(self, ctx:ProcDSLParser.ConnectorConfigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#connectorOptions.
    def visitConnectorOptions(self, ctx:ProcDSLParser.ConnectorOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timestampBounds.
    def visitTimestampBounds(self, ctx:ProcDSLParser.TimestampBoundsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#parquetOptions.
    def visitParquetOptions(self, ctx:ProcDSLParser.ParquetOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#csvOptions.
    def visitCsvOptions(self, ctx:ProcDSLParser.CsvOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#headerBindings.
    def visitHeaderBindings(self, ctx:ProcDSLParser.HeaderBindingsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#headerBinding.
    def visitHeaderBinding(self, ctx:ProcDSLParser.HeaderBindingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#keywordOrIdentifier.
    def visitKeywordOrIdentifier(self, ctx:ProcDSLParser.KeywordOrIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#offsetType.
    def visitOffsetType(self, ctx:ProcDSLParser.OffsetTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#isolationType.
    def visitIsolationType(self, ctx:ProcDSLParser.IsolationTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#compactionType.
    def visitCompactionType(self, ctx:ProcDSLParser.CompactionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#retentionType.
    def visitRetentionType(self, ctx:ProcDSLParser.RetentionTypeContext):
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


    # Visit a parse tree produced by ProcDSLParser#processingStatement.
    def visitProcessingStatement(self, ctx:ProcDSLParser.ProcessingStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transformDecl.
    def visitTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transformStateRef.
    def visitTransformStateRef(self, ctx:ProcDSLParser.TransformStateRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transformOptions.
    def visitTransformOptions(self, ctx:ProcDSLParser.TransformOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transformOption.
    def visitTransformOption(self, ctx:ProcDSLParser.TransformOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#lookupsBlock.
    def visitLookupsBlock(self, ctx:ProcDSLParser.LookupsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#lookupBinding.
    def visitLookupBinding(self, ctx:ProcDSLParser.LookupBindingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#embeddedLookup.
    def visitEmbeddedLookup(self, ctx:ProcDSLParser.EmbeddedLookupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onSuccessBlock.
    def visitOnSuccessBlock(self, ctx:ProcDSLParser.OnSuccessBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onFailureBlock.
    def visitOnFailureBlock(self, ctx:ProcDSLParser.OnFailureBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#actionContent.
    def visitActionContent(self, ctx:ProcDSLParser.ActionContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#inlineTransformBody.
    def visitInlineTransformBody(self, ctx:ProcDSLParser.InlineTransformBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#assignment.
    def visitAssignment(self, ctx:ProcDSLParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#evaluateStatement.
    def visitEvaluateStatement(self, ctx:ProcDSLParser.EvaluateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#evaluateOptions.
    def visitEvaluateOptions(self, ctx:ProcDSLParser.EvaluateOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#outputCapture.
    def visitOutputCapture(self, ctx:ProcDSLParser.OutputCaptureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#evaluateActions.
    def visitEvaluateActions(self, ctx:ProcDSLParser.EvaluateActionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#directActions.
    def visitDirectActions(self, ctx:ProcDSLParser.DirectActionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#conditionalAction.
    def visitConditionalAction(self, ctx:ProcDSLParser.ConditionalActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#conditionalBody.
    def visitConditionalBody(self, ctx:ProcDSLParser.ConditionalBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#addFlagStatement.
    def visitAddFlagStatement(self, ctx:ProcDSLParser.AddFlagStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#addMetadataStatement.
    def visitAddMetadataStatement(self, ctx:ProcDSLParser.AddMetadataStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#adjustScoreStatement.
    def visitAdjustScoreStatement(self, ctx:ProcDSLParser.AdjustScoreStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#routeDecl.
    def visitRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#routeSource.
    def visitRouteSource(self, ctx:ProcDSLParser.RouteSourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#routeDestination.
    def visitRouteDestination(self, ctx:ProcDSLParser.RouteDestinationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#otherwiseClause.
    def visitOtherwiseClause(self, ctx:ProcDSLParser.OtherwiseClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowDecl.
    def visitWindowDecl(self, ctx:ProcDSLParser.WindowDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowType.
    def visitWindowType(self, ctx:ProcDSLParser.WindowTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#windowBody.
    def visitWindowBody(self, ctx:ProcDSLParser.WindowBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#keyByClause.
    def visitKeyByClause(self, ctx:ProcDSLParser.KeyByClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#inlineAggregateBlock.
    def visitInlineAggregateBlock(self, ctx:ProcDSLParser.InlineAggregateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#aggregationExpr.
    def visitAggregationExpr(self, ctx:ProcDSLParser.AggregationExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#aggregateFunction.
    def visitAggregateFunction(self, ctx:ProcDSLParser.AggregateFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#stateClause.
    def visitStateClause(self, ctx:ProcDSLParser.StateClauseContext):
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


    # Visit a parse tree produced by ProcDSLParser#mergeDecl.
    def visitMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#enrichDecl.
    def visitEnrichDecl(self, ctx:ProcDSLParser.EnrichDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#selectClause.
    def visitSelectClause(self, ctx:ProcDSLParser.SelectClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#aggregateDecl.
    def visitAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#aggregateOptions.
    def visitAggregateOptions(self, ctx:ProcDSLParser.AggregateOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#onPartialTimeoutBlock.
    def visitOnPartialTimeoutBlock(self, ctx:ProcDSLParser.OnPartialTimeoutBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#logWarningStatement.
    def visitLogWarningStatement(self, ctx:ProcDSLParser.LogWarningStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#lookupStatement.
    def visitLookupStatement(self, ctx:ProcDSLParser.LookupStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#lookupSource.
    def visitLookupSource(self, ctx:ProcDSLParser.LookupSourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#branchStatement.
    def visitBranchStatement(self, ctx:ProcDSLParser.BranchStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#branchBody.
    def visitBranchBody(self, ctx:ProcDSLParser.BranchBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#parallelStatement.
    def visitParallelStatement(self, ctx:ProcDSLParser.ParallelStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#parallelOptions.
    def visitParallelOptions(self, ctx:ProcDSLParser.ParallelOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#parallelBranch.
    def visitParallelBranch(self, ctx:ProcDSLParser.ParallelBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#transitionStatement.
    def visitTransitionStatement(self, ctx:ProcDSLParser.TransitionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#emitAuditStatement.
    def visitEmitAuditStatement(self, ctx:ProcDSLParser.EmitAuditStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#actorType.
    def visitActorType(self, ctx:ProcDSLParser.ActorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#deduplicateStatement.
    def visitDeduplicateStatement(self, ctx:ProcDSLParser.DeduplicateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#validateInputStatement.
    def visitValidateInputStatement(self, ctx:ProcDSLParser.ValidateInputStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#validationRule.
    def visitValidationRule(self, ctx:ProcDSLParser.ValidationRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#foreachStatement.
    def visitForeachStatement(self, ctx:ProcDSLParser.ForeachStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#foreachBody.
    def visitForeachBody(self, ctx:ProcDSLParser.ForeachBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#callStatement.
    def visitCallStatement(self, ctx:ProcDSLParser.CallStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#callType.
    def visitCallType(self, ctx:ProcDSLParser.CallTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#callOptions.
    def visitCallOptions(self, ctx:ProcDSLParser.CallOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#callOption.
    def visitCallOption(self, ctx:ProcDSLParser.CallOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#circuitBreakerClause.
    def visitCircuitBreakerClause(self, ctx:ProcDSLParser.CircuitBreakerClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#scheduleStatement.
    def visitScheduleStatement(self, ctx:ProcDSLParser.ScheduleStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#scheduleDuration.
    def visitScheduleDuration(self, ctx:ProcDSLParser.ScheduleDurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#sqlStatement.
    def visitSqlStatement(self, ctx:ProcDSLParser.SqlStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#setStatement.
    def visitSetStatement(self, ctx:ProcDSLParser.SetStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#letStatement.
    def visitLetStatement(self, ctx:ProcDSLParser.LetStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#ifStatement.
    def visitIfStatement(self, ctx:ProcDSLParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#ifBody.
    def visitIfBody(self, ctx:ProcDSLParser.IfBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#emitDecl.
    def visitEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#sinkName.
    def visitSinkName(self, ctx:ProcDSLParser.SinkNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#emitClause.
    def visitEmitClause(self, ctx:ProcDSLParser.EmitClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#persistClause.
    def visitPersistClause(self, ctx:ProcDSLParser.PersistClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#persistTarget.
    def visitPersistTarget(self, ctx:ProcDSLParser.PersistTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#persistOption.
    def visitPersistOption(self, ctx:ProcDSLParser.PersistOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#persistErrorAction.
    def visitPersistErrorAction(self, ctx:ProcDSLParser.PersistErrorActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fanoutDecl.
    def visitFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#emitOptions.
    def visitEmitOptions(self, ctx:ProcDSLParser.EmitOptionsContext):
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


    # Visit a parse tree produced by ProcDSLParser#metricsBlock.
    def visitMetricsBlock(self, ctx:ProcDSLParser.MetricsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#metricDecl.
    def visitMetricDecl(self, ctx:ProcDSLParser.MetricDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#resilienceBlock.
    def visitResilienceBlock(self, ctx:ProcDSLParser.ResilienceBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorBlock.
    def visitErrorBlock(self, ctx:ProcDSLParser.ErrorBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#simpleErrorHandler.
    def visitSimpleErrorHandler(self, ctx:ProcDSLParser.SimpleErrorHandlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#errorHandlerStatement.
    def visitErrorHandlerStatement(self, ctx:ProcDSLParser.ErrorHandlerStatementContext):
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


    # Visit a parse tree produced by ProcDSLParser#logErrorStatement.
    def visitLogErrorStatement(self, ctx:ProcDSLParser.LogErrorStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#logInfoStatement.
    def visitLogInfoStatement(self, ctx:ProcDSLParser.LogInfoStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#retryBlock.
    def visitRetryBlock(self, ctx:ProcDSLParser.RetryBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#retryOptions.
    def visitRetryOptions(self, ctx:ProcDSLParser.RetryOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#backoffType.
    def visitBackoffType(self, ctx:ProcDSLParser.BackoffTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#thenBlock.
    def visitThenBlock(self, ctx:ProcDSLParser.ThenBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#thenContent.
    def visitThenContent(self, ctx:ProcDSLParser.ThenContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#expression.
    def visitExpression(self, ctx:ProcDSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#orExpression.
    def visitOrExpression(self, ctx:ProcDSLParser.OrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#andExpression.
    def visitAndExpression(self, ctx:ProcDSLParser.AndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#notExpression.
    def visitNotExpression(self, ctx:ProcDSLParser.NotExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#comparisonExpression.
    def visitComparisonExpression(self, ctx:ProcDSLParser.ComparisonExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#comparisonOp.
    def visitComparisonOp(self, ctx:ProcDSLParser.ComparisonOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:ProcDSLParser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:ProcDSLParser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#unaryExpression.
    def visitUnaryExpression(self, ctx:ProcDSLParser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:ProcDSLParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#ternaryExpression.
    def visitTernaryExpression(self, ctx:ProcDSLParser.TernaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#functionCall.
    def visitFunctionCall(self, ctx:ProcDSLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#functionName.
    def visitFunctionName(self, ctx:ProcDSLParser.FunctionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#interpolatedString.
    def visitInterpolatedString(self, ctx:ProcDSLParser.InterpolatedStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fieldPath.
    def visitFieldPath(self, ctx:ProcDSLParser.FieldPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#fieldList.
    def visitFieldList(self, ctx:ProcDSLParser.FieldListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#identifierList.
    def visitIdentifierList(self, ctx:ProcDSLParser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#valueList.
    def visitValueList(self, ctx:ProcDSLParser.ValueListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#duration.
    def visitDuration(self, ctx:ProcDSLParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#durationLiteral.
    def visitDurationLiteral(self, ctx:ProcDSLParser.DurationLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#timeUnit.
    def visitTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#literal.
    def visitLiteral(self, ctx:ProcDSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#booleanLiteral.
    def visitBooleanLiteral(self, ctx:ProcDSLParser.BooleanLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#objectLiteral.
    def visitObjectLiteral(self, ctx:ProcDSLParser.ObjectLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#objectField.
    def visitObjectField(self, ctx:ProcDSLParser.ObjectFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#arrayLiteral.
    def visitArrayLiteral(self, ctx:ProcDSLParser.ArrayLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#paramBlock.
    def visitParamBlock(self, ctx:ProcDSLParser.ParamBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ProcDSLParser#paramField.
    def visitParamField(self, ctx:ProcDSLParser.ParamFieldContext):
        return self.visitChildren(ctx)



del ProcDSLParser