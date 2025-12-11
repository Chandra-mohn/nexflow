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


    # Enter a parse tree produced by ProcDSLParser#processTailBlocks.
    def enterProcessTailBlocks(self, ctx:ProcDSLParser.ProcessTailBlocksContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processTailBlocks.
    def exitProcessTailBlocks(self, ctx:ProcDSLParser.ProcessTailBlocksContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#bodyContent.
    def enterBodyContent(self, ctx:ProcDSLParser.BodyContentContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#bodyContent.
    def exitBodyContent(self, ctx:ProcDSLParser.BodyContentContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#processName.
    def enterProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processName.
    def exitProcessName(self, ctx:ProcDSLParser.ProcessNameContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#processingBlock.
    def enterProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processingBlock.
    def exitProcessingBlock(self, ctx:ProcDSLParser.ProcessingBlockContext):
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


    # Enter a parse tree produced by ProcDSLParser#stateMachineDecl.
    def enterStateMachineDecl(self, ctx:ProcDSLParser.StateMachineDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#stateMachineDecl.
    def exitStateMachineDecl(self, ctx:ProcDSLParser.StateMachineDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#persistenceDecl.
    def enterPersistenceDecl(self, ctx:ProcDSLParser.PersistenceDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#persistenceDecl.
    def exitPersistenceDecl(self, ctx:ProcDSLParser.PersistenceDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#checkpointDecl.
    def enterCheckpointDecl(self, ctx:ProcDSLParser.CheckpointDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#checkpointDecl.
    def exitCheckpointDecl(self, ctx:ProcDSLParser.CheckpointDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#receiveDecl.
    def enterReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#receiveDecl.
    def exitReceiveDecl(self, ctx:ProcDSLParser.ReceiveDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#receiveClause.
    def enterReceiveClause(self, ctx:ProcDSLParser.ReceiveClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#receiveClause.
    def exitReceiveClause(self, ctx:ProcDSLParser.ReceiveClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#connectorClause.
    def enterConnectorClause(self, ctx:ProcDSLParser.ConnectorClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#connectorClause.
    def exitConnectorClause(self, ctx:ProcDSLParser.ConnectorClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#connectorType.
    def enterConnectorType(self, ctx:ProcDSLParser.ConnectorTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#connectorType.
    def exitConnectorType(self, ctx:ProcDSLParser.ConnectorTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#connectorConfig.
    def enterConnectorConfig(self, ctx:ProcDSLParser.ConnectorConfigContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#connectorConfig.
    def exitConnectorConfig(self, ctx:ProcDSLParser.ConnectorConfigContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#connectorOptions.
    def enterConnectorOptions(self, ctx:ProcDSLParser.ConnectorOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#connectorOptions.
    def exitConnectorOptions(self, ctx:ProcDSLParser.ConnectorOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#headerBindings.
    def enterHeaderBindings(self, ctx:ProcDSLParser.HeaderBindingsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#headerBindings.
    def exitHeaderBindings(self, ctx:ProcDSLParser.HeaderBindingsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#headerBinding.
    def enterHeaderBinding(self, ctx:ProcDSLParser.HeaderBindingContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#headerBinding.
    def exitHeaderBinding(self, ctx:ProcDSLParser.HeaderBindingContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#keywordOrIdentifier.
    def enterKeywordOrIdentifier(self, ctx:ProcDSLParser.KeywordOrIdentifierContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#keywordOrIdentifier.
    def exitKeywordOrIdentifier(self, ctx:ProcDSLParser.KeywordOrIdentifierContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#offsetType.
    def enterOffsetType(self, ctx:ProcDSLParser.OffsetTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#offsetType.
    def exitOffsetType(self, ctx:ProcDSLParser.OffsetTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#isolationType.
    def enterIsolationType(self, ctx:ProcDSLParser.IsolationTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#isolationType.
    def exitIsolationType(self, ctx:ProcDSLParser.IsolationTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#compactionType.
    def enterCompactionType(self, ctx:ProcDSLParser.CompactionTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#compactionType.
    def exitCompactionType(self, ctx:ProcDSLParser.CompactionTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#retentionType.
    def enterRetentionType(self, ctx:ProcDSLParser.RetentionTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#retentionType.
    def exitRetentionType(self, ctx:ProcDSLParser.RetentionTypeContext):
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


    # Enter a parse tree produced by ProcDSLParser#processingStatement.
    def enterProcessingStatement(self, ctx:ProcDSLParser.ProcessingStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#processingStatement.
    def exitProcessingStatement(self, ctx:ProcDSLParser.ProcessingStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transformDecl.
    def enterTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transformDecl.
    def exitTransformDecl(self, ctx:ProcDSLParser.TransformDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transformStateRef.
    def enterTransformStateRef(self, ctx:ProcDSLParser.TransformStateRefContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transformStateRef.
    def exitTransformStateRef(self, ctx:ProcDSLParser.TransformStateRefContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transformOptions.
    def enterTransformOptions(self, ctx:ProcDSLParser.TransformOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transformOptions.
    def exitTransformOptions(self, ctx:ProcDSLParser.TransformOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transformOption.
    def enterTransformOption(self, ctx:ProcDSLParser.TransformOptionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transformOption.
    def exitTransformOption(self, ctx:ProcDSLParser.TransformOptionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#lookupsBlock.
    def enterLookupsBlock(self, ctx:ProcDSLParser.LookupsBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#lookupsBlock.
    def exitLookupsBlock(self, ctx:ProcDSLParser.LookupsBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#lookupBinding.
    def enterLookupBinding(self, ctx:ProcDSLParser.LookupBindingContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#lookupBinding.
    def exitLookupBinding(self, ctx:ProcDSLParser.LookupBindingContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#embeddedLookup.
    def enterEmbeddedLookup(self, ctx:ProcDSLParser.EmbeddedLookupContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#embeddedLookup.
    def exitEmbeddedLookup(self, ctx:ProcDSLParser.EmbeddedLookupContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#onSuccessBlock.
    def enterOnSuccessBlock(self, ctx:ProcDSLParser.OnSuccessBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#onSuccessBlock.
    def exitOnSuccessBlock(self, ctx:ProcDSLParser.OnSuccessBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#onFailureBlock.
    def enterOnFailureBlock(self, ctx:ProcDSLParser.OnFailureBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#onFailureBlock.
    def exitOnFailureBlock(self, ctx:ProcDSLParser.OnFailureBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#actionContent.
    def enterActionContent(self, ctx:ProcDSLParser.ActionContentContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#actionContent.
    def exitActionContent(self, ctx:ProcDSLParser.ActionContentContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#inlineTransformBody.
    def enterInlineTransformBody(self, ctx:ProcDSLParser.InlineTransformBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#inlineTransformBody.
    def exitInlineTransformBody(self, ctx:ProcDSLParser.InlineTransformBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#assignment.
    def enterAssignment(self, ctx:ProcDSLParser.AssignmentContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#assignment.
    def exitAssignment(self, ctx:ProcDSLParser.AssignmentContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#evaluateStatement.
    def enterEvaluateStatement(self, ctx:ProcDSLParser.EvaluateStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#evaluateStatement.
    def exitEvaluateStatement(self, ctx:ProcDSLParser.EvaluateStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#evaluateOptions.
    def enterEvaluateOptions(self, ctx:ProcDSLParser.EvaluateOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#evaluateOptions.
    def exitEvaluateOptions(self, ctx:ProcDSLParser.EvaluateOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#outputCapture.
    def enterOutputCapture(self, ctx:ProcDSLParser.OutputCaptureContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#outputCapture.
    def exitOutputCapture(self, ctx:ProcDSLParser.OutputCaptureContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#evaluateActions.
    def enterEvaluateActions(self, ctx:ProcDSLParser.EvaluateActionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#evaluateActions.
    def exitEvaluateActions(self, ctx:ProcDSLParser.EvaluateActionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#directActions.
    def enterDirectActions(self, ctx:ProcDSLParser.DirectActionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#directActions.
    def exitDirectActions(self, ctx:ProcDSLParser.DirectActionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#conditionalAction.
    def enterConditionalAction(self, ctx:ProcDSLParser.ConditionalActionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#conditionalAction.
    def exitConditionalAction(self, ctx:ProcDSLParser.ConditionalActionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#conditionalBody.
    def enterConditionalBody(self, ctx:ProcDSLParser.ConditionalBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#conditionalBody.
    def exitConditionalBody(self, ctx:ProcDSLParser.ConditionalBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#addFlagStatement.
    def enterAddFlagStatement(self, ctx:ProcDSLParser.AddFlagStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#addFlagStatement.
    def exitAddFlagStatement(self, ctx:ProcDSLParser.AddFlagStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#addMetadataStatement.
    def enterAddMetadataStatement(self, ctx:ProcDSLParser.AddMetadataStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#addMetadataStatement.
    def exitAddMetadataStatement(self, ctx:ProcDSLParser.AddMetadataStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#adjustScoreStatement.
    def enterAdjustScoreStatement(self, ctx:ProcDSLParser.AdjustScoreStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#adjustScoreStatement.
    def exitAdjustScoreStatement(self, ctx:ProcDSLParser.AdjustScoreStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#routeDecl.
    def enterRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#routeDecl.
    def exitRouteDecl(self, ctx:ProcDSLParser.RouteDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#routeSource.
    def enterRouteSource(self, ctx:ProcDSLParser.RouteSourceContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#routeSource.
    def exitRouteSource(self, ctx:ProcDSLParser.RouteSourceContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#routeDestination.
    def enterRouteDestination(self, ctx:ProcDSLParser.RouteDestinationContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#routeDestination.
    def exitRouteDestination(self, ctx:ProcDSLParser.RouteDestinationContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#otherwiseClause.
    def enterOtherwiseClause(self, ctx:ProcDSLParser.OtherwiseClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#otherwiseClause.
    def exitOtherwiseClause(self, ctx:ProcDSLParser.OtherwiseClauseContext):
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


    # Enter a parse tree produced by ProcDSLParser#windowBody.
    def enterWindowBody(self, ctx:ProcDSLParser.WindowBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#windowBody.
    def exitWindowBody(self, ctx:ProcDSLParser.WindowBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#keyByClause.
    def enterKeyByClause(self, ctx:ProcDSLParser.KeyByClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#keyByClause.
    def exitKeyByClause(self, ctx:ProcDSLParser.KeyByClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#inlineAggregateBlock.
    def enterInlineAggregateBlock(self, ctx:ProcDSLParser.InlineAggregateBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#inlineAggregateBlock.
    def exitInlineAggregateBlock(self, ctx:ProcDSLParser.InlineAggregateBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#aggregationExpr.
    def enterAggregationExpr(self, ctx:ProcDSLParser.AggregationExprContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#aggregationExpr.
    def exitAggregationExpr(self, ctx:ProcDSLParser.AggregationExprContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#aggregateFunction.
    def enterAggregateFunction(self, ctx:ProcDSLParser.AggregateFunctionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#aggregateFunction.
    def exitAggregateFunction(self, ctx:ProcDSLParser.AggregateFunctionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#stateClause.
    def enterStateClause(self, ctx:ProcDSLParser.StateClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#stateClause.
    def exitStateClause(self, ctx:ProcDSLParser.StateClauseContext):
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


    # Enter a parse tree produced by ProcDSLParser#mergeDecl.
    def enterMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#mergeDecl.
    def exitMergeDecl(self, ctx:ProcDSLParser.MergeDeclContext):
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


    # Enter a parse tree produced by ProcDSLParser#aggregateDecl.
    def enterAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#aggregateDecl.
    def exitAggregateDecl(self, ctx:ProcDSLParser.AggregateDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#aggregateOptions.
    def enterAggregateOptions(self, ctx:ProcDSLParser.AggregateOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#aggregateOptions.
    def exitAggregateOptions(self, ctx:ProcDSLParser.AggregateOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#onPartialTimeoutBlock.
    def enterOnPartialTimeoutBlock(self, ctx:ProcDSLParser.OnPartialTimeoutBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#onPartialTimeoutBlock.
    def exitOnPartialTimeoutBlock(self, ctx:ProcDSLParser.OnPartialTimeoutBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#logWarningStatement.
    def enterLogWarningStatement(self, ctx:ProcDSLParser.LogWarningStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#logWarningStatement.
    def exitLogWarningStatement(self, ctx:ProcDSLParser.LogWarningStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#lookupStatement.
    def enterLookupStatement(self, ctx:ProcDSLParser.LookupStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#lookupStatement.
    def exitLookupStatement(self, ctx:ProcDSLParser.LookupStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#lookupSource.
    def enterLookupSource(self, ctx:ProcDSLParser.LookupSourceContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#lookupSource.
    def exitLookupSource(self, ctx:ProcDSLParser.LookupSourceContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#branchStatement.
    def enterBranchStatement(self, ctx:ProcDSLParser.BranchStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#branchStatement.
    def exitBranchStatement(self, ctx:ProcDSLParser.BranchStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#branchBody.
    def enterBranchBody(self, ctx:ProcDSLParser.BranchBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#branchBody.
    def exitBranchBody(self, ctx:ProcDSLParser.BranchBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#parallelStatement.
    def enterParallelStatement(self, ctx:ProcDSLParser.ParallelStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#parallelStatement.
    def exitParallelStatement(self, ctx:ProcDSLParser.ParallelStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#parallelOptions.
    def enterParallelOptions(self, ctx:ProcDSLParser.ParallelOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#parallelOptions.
    def exitParallelOptions(self, ctx:ProcDSLParser.ParallelOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#parallelBranch.
    def enterParallelBranch(self, ctx:ProcDSLParser.ParallelBranchContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#parallelBranch.
    def exitParallelBranch(self, ctx:ProcDSLParser.ParallelBranchContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#transitionStatement.
    def enterTransitionStatement(self, ctx:ProcDSLParser.TransitionStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#transitionStatement.
    def exitTransitionStatement(self, ctx:ProcDSLParser.TransitionStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#emitAuditStatement.
    def enterEmitAuditStatement(self, ctx:ProcDSLParser.EmitAuditStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#emitAuditStatement.
    def exitEmitAuditStatement(self, ctx:ProcDSLParser.EmitAuditStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#actorType.
    def enterActorType(self, ctx:ProcDSLParser.ActorTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#actorType.
    def exitActorType(self, ctx:ProcDSLParser.ActorTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#deduplicateStatement.
    def enterDeduplicateStatement(self, ctx:ProcDSLParser.DeduplicateStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#deduplicateStatement.
    def exitDeduplicateStatement(self, ctx:ProcDSLParser.DeduplicateStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#validateInputStatement.
    def enterValidateInputStatement(self, ctx:ProcDSLParser.ValidateInputStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#validateInputStatement.
    def exitValidateInputStatement(self, ctx:ProcDSLParser.ValidateInputStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#validationRule.
    def enterValidationRule(self, ctx:ProcDSLParser.ValidationRuleContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#validationRule.
    def exitValidationRule(self, ctx:ProcDSLParser.ValidationRuleContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#foreachStatement.
    def enterForeachStatement(self, ctx:ProcDSLParser.ForeachStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#foreachStatement.
    def exitForeachStatement(self, ctx:ProcDSLParser.ForeachStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#foreachBody.
    def enterForeachBody(self, ctx:ProcDSLParser.ForeachBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#foreachBody.
    def exitForeachBody(self, ctx:ProcDSLParser.ForeachBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#callStatement.
    def enterCallStatement(self, ctx:ProcDSLParser.CallStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#callStatement.
    def exitCallStatement(self, ctx:ProcDSLParser.CallStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#callType.
    def enterCallType(self, ctx:ProcDSLParser.CallTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#callType.
    def exitCallType(self, ctx:ProcDSLParser.CallTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#callOptions.
    def enterCallOptions(self, ctx:ProcDSLParser.CallOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#callOptions.
    def exitCallOptions(self, ctx:ProcDSLParser.CallOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#callOption.
    def enterCallOption(self, ctx:ProcDSLParser.CallOptionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#callOption.
    def exitCallOption(self, ctx:ProcDSLParser.CallOptionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#circuitBreakerClause.
    def enterCircuitBreakerClause(self, ctx:ProcDSLParser.CircuitBreakerClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#circuitBreakerClause.
    def exitCircuitBreakerClause(self, ctx:ProcDSLParser.CircuitBreakerClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#scheduleStatement.
    def enterScheduleStatement(self, ctx:ProcDSLParser.ScheduleStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#scheduleStatement.
    def exitScheduleStatement(self, ctx:ProcDSLParser.ScheduleStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#scheduleDuration.
    def enterScheduleDuration(self, ctx:ProcDSLParser.ScheduleDurationContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#scheduleDuration.
    def exitScheduleDuration(self, ctx:ProcDSLParser.ScheduleDurationContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#setStatement.
    def enterSetStatement(self, ctx:ProcDSLParser.SetStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#setStatement.
    def exitSetStatement(self, ctx:ProcDSLParser.SetStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#letStatement.
    def enterLetStatement(self, ctx:ProcDSLParser.LetStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#letStatement.
    def exitLetStatement(self, ctx:ProcDSLParser.LetStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#ifStatement.
    def enterIfStatement(self, ctx:ProcDSLParser.IfStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#ifStatement.
    def exitIfStatement(self, ctx:ProcDSLParser.IfStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#ifBody.
    def enterIfBody(self, ctx:ProcDSLParser.IfBodyContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#ifBody.
    def exitIfBody(self, ctx:ProcDSLParser.IfBodyContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#emitDecl.
    def enterEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#emitDecl.
    def exitEmitDecl(self, ctx:ProcDSLParser.EmitDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#sinkName.
    def enterSinkName(self, ctx:ProcDSLParser.SinkNameContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#sinkName.
    def exitSinkName(self, ctx:ProcDSLParser.SinkNameContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#emitClause.
    def enterEmitClause(self, ctx:ProcDSLParser.EmitClauseContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#emitClause.
    def exitEmitClause(self, ctx:ProcDSLParser.EmitClauseContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#fanoutDecl.
    def enterFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#fanoutDecl.
    def exitFanoutDecl(self, ctx:ProcDSLParser.FanoutDeclContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#emitOptions.
    def enterEmitOptions(self, ctx:ProcDSLParser.EmitOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#emitOptions.
    def exitEmitOptions(self, ctx:ProcDSLParser.EmitOptionsContext):
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


    # Enter a parse tree produced by ProcDSLParser#metricsBlock.
    def enterMetricsBlock(self, ctx:ProcDSLParser.MetricsBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#metricsBlock.
    def exitMetricsBlock(self, ctx:ProcDSLParser.MetricsBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#metricDecl.
    def enterMetricDecl(self, ctx:ProcDSLParser.MetricDeclContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#metricDecl.
    def exitMetricDecl(self, ctx:ProcDSLParser.MetricDeclContext):
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


    # Enter a parse tree produced by ProcDSLParser#simpleErrorHandler.
    def enterSimpleErrorHandler(self, ctx:ProcDSLParser.SimpleErrorHandlerContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#simpleErrorHandler.
    def exitSimpleErrorHandler(self, ctx:ProcDSLParser.SimpleErrorHandlerContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#errorHandlerStatement.
    def enterErrorHandlerStatement(self, ctx:ProcDSLParser.ErrorHandlerStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#errorHandlerStatement.
    def exitErrorHandlerStatement(self, ctx:ProcDSLParser.ErrorHandlerStatementContext):
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


    # Enter a parse tree produced by ProcDSLParser#logErrorStatement.
    def enterLogErrorStatement(self, ctx:ProcDSLParser.LogErrorStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#logErrorStatement.
    def exitLogErrorStatement(self, ctx:ProcDSLParser.LogErrorStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#logInfoStatement.
    def enterLogInfoStatement(self, ctx:ProcDSLParser.LogInfoStatementContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#logInfoStatement.
    def exitLogInfoStatement(self, ctx:ProcDSLParser.LogInfoStatementContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#retryBlock.
    def enterRetryBlock(self, ctx:ProcDSLParser.RetryBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#retryBlock.
    def exitRetryBlock(self, ctx:ProcDSLParser.RetryBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#retryOptions.
    def enterRetryOptions(self, ctx:ProcDSLParser.RetryOptionsContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#retryOptions.
    def exitRetryOptions(self, ctx:ProcDSLParser.RetryOptionsContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#backoffType.
    def enterBackoffType(self, ctx:ProcDSLParser.BackoffTypeContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#backoffType.
    def exitBackoffType(self, ctx:ProcDSLParser.BackoffTypeContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#thenBlock.
    def enterThenBlock(self, ctx:ProcDSLParser.ThenBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#thenBlock.
    def exitThenBlock(self, ctx:ProcDSLParser.ThenBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#thenContent.
    def enterThenContent(self, ctx:ProcDSLParser.ThenContentContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#thenContent.
    def exitThenContent(self, ctx:ProcDSLParser.ThenContentContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#expression.
    def enterExpression(self, ctx:ProcDSLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#expression.
    def exitExpression(self, ctx:ProcDSLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#orExpression.
    def enterOrExpression(self, ctx:ProcDSLParser.OrExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#orExpression.
    def exitOrExpression(self, ctx:ProcDSLParser.OrExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#andExpression.
    def enterAndExpression(self, ctx:ProcDSLParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#andExpression.
    def exitAndExpression(self, ctx:ProcDSLParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#notExpression.
    def enterNotExpression(self, ctx:ProcDSLParser.NotExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#notExpression.
    def exitNotExpression(self, ctx:ProcDSLParser.NotExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#comparisonExpression.
    def enterComparisonExpression(self, ctx:ProcDSLParser.ComparisonExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#comparisonExpression.
    def exitComparisonExpression(self, ctx:ProcDSLParser.ComparisonExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#comparisonOp.
    def enterComparisonOp(self, ctx:ProcDSLParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#comparisonOp.
    def exitComparisonOp(self, ctx:ProcDSLParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:ProcDSLParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:ProcDSLParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:ProcDSLParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:ProcDSLParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#unaryExpression.
    def enterUnaryExpression(self, ctx:ProcDSLParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#unaryExpression.
    def exitUnaryExpression(self, ctx:ProcDSLParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:ProcDSLParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:ProcDSLParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#ternaryExpression.
    def enterTernaryExpression(self, ctx:ProcDSLParser.TernaryExpressionContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#ternaryExpression.
    def exitTernaryExpression(self, ctx:ProcDSLParser.TernaryExpressionContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#functionCall.
    def enterFunctionCall(self, ctx:ProcDSLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#functionCall.
    def exitFunctionCall(self, ctx:ProcDSLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#functionName.
    def enterFunctionName(self, ctx:ProcDSLParser.FunctionNameContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#functionName.
    def exitFunctionName(self, ctx:ProcDSLParser.FunctionNameContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#interpolatedString.
    def enterInterpolatedString(self, ctx:ProcDSLParser.InterpolatedStringContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#interpolatedString.
    def exitInterpolatedString(self, ctx:ProcDSLParser.InterpolatedStringContext):
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


    # Enter a parse tree produced by ProcDSLParser#identifierList.
    def enterIdentifierList(self, ctx:ProcDSLParser.IdentifierListContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#identifierList.
    def exitIdentifierList(self, ctx:ProcDSLParser.IdentifierListContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#valueList.
    def enterValueList(self, ctx:ProcDSLParser.ValueListContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#valueList.
    def exitValueList(self, ctx:ProcDSLParser.ValueListContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#duration.
    def enterDuration(self, ctx:ProcDSLParser.DurationContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#duration.
    def exitDuration(self, ctx:ProcDSLParser.DurationContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#durationLiteral.
    def enterDurationLiteral(self, ctx:ProcDSLParser.DurationLiteralContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#durationLiteral.
    def exitDurationLiteral(self, ctx:ProcDSLParser.DurationLiteralContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#timeUnit.
    def enterTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#timeUnit.
    def exitTimeUnit(self, ctx:ProcDSLParser.TimeUnitContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#literal.
    def enterLiteral(self, ctx:ProcDSLParser.LiteralContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#literal.
    def exitLiteral(self, ctx:ProcDSLParser.LiteralContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:ProcDSLParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:ProcDSLParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#objectLiteral.
    def enterObjectLiteral(self, ctx:ProcDSLParser.ObjectLiteralContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#objectLiteral.
    def exitObjectLiteral(self, ctx:ProcDSLParser.ObjectLiteralContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#objectField.
    def enterObjectField(self, ctx:ProcDSLParser.ObjectFieldContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#objectField.
    def exitObjectField(self, ctx:ProcDSLParser.ObjectFieldContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#arrayLiteral.
    def enterArrayLiteral(self, ctx:ProcDSLParser.ArrayLiteralContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#arrayLiteral.
    def exitArrayLiteral(self, ctx:ProcDSLParser.ArrayLiteralContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#paramBlock.
    def enterParamBlock(self, ctx:ProcDSLParser.ParamBlockContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#paramBlock.
    def exitParamBlock(self, ctx:ProcDSLParser.ParamBlockContext):
        pass


    # Enter a parse tree produced by ProcDSLParser#paramField.
    def enterParamField(self, ctx:ProcDSLParser.ParamFieldContext):
        pass

    # Exit a parse tree produced by ProcDSLParser#paramField.
    def exitParamField(self, ctx:ProcDSLParser.ParamFieldContext):
        pass



del ProcDSLParser