# Generated from grammar/RulesDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .RulesDSLParser import RulesDSLParser
else:
    from RulesDSLParser import RulesDSLParser

# This class defines a complete listener for a parse tree produced by RulesDSLParser.
class RulesDSLListener(ParseTreeListener):

    # Enter a parse tree produced by RulesDSLParser#program.
    def enterProgram(self, ctx:RulesDSLParser.ProgramContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#program.
    def exitProgram(self, ctx:RulesDSLParser.ProgramContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#servicesBlock.
    def enterServicesBlock(self, ctx:RulesDSLParser.ServicesBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#servicesBlock.
    def exitServicesBlock(self, ctx:RulesDSLParser.ServicesBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceDecl.
    def enterServiceDecl(self, ctx:RulesDSLParser.ServiceDeclContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceDecl.
    def exitServiceDecl(self, ctx:RulesDSLParser.ServiceDeclContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceName.
    def enterServiceName(self, ctx:RulesDSLParser.ServiceNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceName.
    def exitServiceName(self, ctx:RulesDSLParser.ServiceNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceClassName.
    def enterServiceClassName(self, ctx:RulesDSLParser.ServiceClassNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceClassName.
    def exitServiceClassName(self, ctx:RulesDSLParser.ServiceClassNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceMethodName.
    def enterServiceMethodName(self, ctx:RulesDSLParser.ServiceMethodNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceMethodName.
    def exitServiceMethodName(self, ctx:RulesDSLParser.ServiceMethodNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceType.
    def enterServiceType(self, ctx:RulesDSLParser.ServiceTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceType.
    def exitServiceType(self, ctx:RulesDSLParser.ServiceTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceParamList.
    def enterServiceParamList(self, ctx:RulesDSLParser.ServiceParamListContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceParamList.
    def exitServiceParamList(self, ctx:RulesDSLParser.ServiceParamListContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceParam.
    def enterServiceParam(self, ctx:RulesDSLParser.ServiceParamContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceParam.
    def exitServiceParam(self, ctx:RulesDSLParser.ServiceParamContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceReturnType.
    def enterServiceReturnType(self, ctx:RulesDSLParser.ServiceReturnTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceReturnType.
    def exitServiceReturnType(self, ctx:RulesDSLParser.ServiceReturnTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceOptions.
    def enterServiceOptions(self, ctx:RulesDSLParser.ServiceOptionsContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceOptions.
    def exitServiceOptions(self, ctx:RulesDSLParser.ServiceOptionsContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#serviceOption.
    def enterServiceOption(self, ctx:RulesDSLParser.ServiceOptionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#serviceOption.
    def exitServiceOption(self, ctx:RulesDSLParser.ServiceOptionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#duration.
    def enterDuration(self, ctx:RulesDSLParser.DurationContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#duration.
    def exitDuration(self, ctx:RulesDSLParser.DurationContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#durationUnit.
    def enterDurationUnit(self, ctx:RulesDSLParser.DurationUnitContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#durationUnit.
    def exitDurationUnit(self, ctx:RulesDSLParser.DurationUnitContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionsBlock.
    def enterActionsBlock(self, ctx:RulesDSLParser.ActionsBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionsBlock.
    def exitActionsBlock(self, ctx:RulesDSLParser.ActionsBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionDecl.
    def enterActionDecl(self, ctx:RulesDSLParser.ActionDeclContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionDecl.
    def exitActionDecl(self, ctx:RulesDSLParser.ActionDeclContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionDeclName.
    def enterActionDeclName(self, ctx:RulesDSLParser.ActionDeclNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionDeclName.
    def exitActionDeclName(self, ctx:RulesDSLParser.ActionDeclNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionParamList.
    def enterActionParamList(self, ctx:RulesDSLParser.ActionParamListContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionParamList.
    def exitActionParamList(self, ctx:RulesDSLParser.ActionParamListContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionParam.
    def enterActionParam(self, ctx:RulesDSLParser.ActionParamContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionParam.
    def exitActionParam(self, ctx:RulesDSLParser.ActionParamContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionTarget.
    def enterActionTarget(self, ctx:RulesDSLParser.ActionTargetContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionTarget.
    def exitActionTarget(self, ctx:RulesDSLParser.ActionTargetContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#emitTarget.
    def enterEmitTarget(self, ctx:RulesDSLParser.EmitTargetContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#emitTarget.
    def exitEmitTarget(self, ctx:RulesDSLParser.EmitTargetContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#stateTarget.
    def enterStateTarget(self, ctx:RulesDSLParser.StateTargetContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#stateTarget.
    def exitStateTarget(self, ctx:RulesDSLParser.StateTargetContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#stateOperation.
    def enterStateOperation(self, ctx:RulesDSLParser.StateOperationContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#stateOperation.
    def exitStateOperation(self, ctx:RulesDSLParser.StateOperationContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#stateOperationArg.
    def enterStateOperationArg(self, ctx:RulesDSLParser.StateOperationArgContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#stateOperationArg.
    def exitStateOperationArg(self, ctx:RulesDSLParser.StateOperationArgContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#auditTarget.
    def enterAuditTarget(self, ctx:RulesDSLParser.AuditTargetContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#auditTarget.
    def exitAuditTarget(self, ctx:RulesDSLParser.AuditTargetContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#callTarget.
    def enterCallTarget(self, ctx:RulesDSLParser.CallTargetContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#callTarget.
    def exitCallTarget(self, ctx:RulesDSLParser.CallTargetContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#decisionTableDef.
    def enterDecisionTableDef(self, ctx:RulesDSLParser.DecisionTableDefContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#decisionTableDef.
    def exitDecisionTableDef(self, ctx:RulesDSLParser.DecisionTableDefContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#versionDecl.
    def enterVersionDecl(self, ctx:RulesDSLParser.VersionDeclContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#versionDecl.
    def exitVersionDecl(self, ctx:RulesDSLParser.VersionDeclContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#tableName.
    def enterTableName(self, ctx:RulesDSLParser.TableNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#tableName.
    def exitTableName(self, ctx:RulesDSLParser.TableNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#hitPolicyDecl.
    def enterHitPolicyDecl(self, ctx:RulesDSLParser.HitPolicyDeclContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#hitPolicyDecl.
    def exitHitPolicyDecl(self, ctx:RulesDSLParser.HitPolicyDeclContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#hitPolicyType.
    def enterHitPolicyType(self, ctx:RulesDSLParser.HitPolicyTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#hitPolicyType.
    def exitHitPolicyType(self, ctx:RulesDSLParser.HitPolicyTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#descriptionDecl.
    def enterDescriptionDecl(self, ctx:RulesDSLParser.DescriptionDeclContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#descriptionDecl.
    def exitDescriptionDecl(self, ctx:RulesDSLParser.DescriptionDeclContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#stringLiteral.
    def enterStringLiteral(self, ctx:RulesDSLParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#stringLiteral.
    def exitStringLiteral(self, ctx:RulesDSLParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#givenBlock.
    def enterGivenBlock(self, ctx:RulesDSLParser.GivenBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#givenBlock.
    def exitGivenBlock(self, ctx:RulesDSLParser.GivenBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#inputParam.
    def enterInputParam(self, ctx:RulesDSLParser.InputParamContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#inputParam.
    def exitInputParam(self, ctx:RulesDSLParser.InputParamContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#paramName.
    def enterParamName(self, ctx:RulesDSLParser.ParamNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#paramName.
    def exitParamName(self, ctx:RulesDSLParser.ParamNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#paramType.
    def enterParamType(self, ctx:RulesDSLParser.ParamTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#paramType.
    def exitParamType(self, ctx:RulesDSLParser.ParamTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#baseType.
    def enterBaseType(self, ctx:RulesDSLParser.BaseTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#baseType.
    def exitBaseType(self, ctx:RulesDSLParser.BaseTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#inlineComment.
    def enterInlineComment(self, ctx:RulesDSLParser.InlineCommentContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#inlineComment.
    def exitInlineComment(self, ctx:RulesDSLParser.InlineCommentContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#decideBlock.
    def enterDecideBlock(self, ctx:RulesDSLParser.DecideBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#decideBlock.
    def exitDecideBlock(self, ctx:RulesDSLParser.DecideBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#tableMatrix.
    def enterTableMatrix(self, ctx:RulesDSLParser.TableMatrixContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#tableMatrix.
    def exitTableMatrix(self, ctx:RulesDSLParser.TableMatrixContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#tableHeader.
    def enterTableHeader(self, ctx:RulesDSLParser.TableHeaderContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#tableHeader.
    def exitTableHeader(self, ctx:RulesDSLParser.TableHeaderContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#priorityHeader.
    def enterPriorityHeader(self, ctx:RulesDSLParser.PriorityHeaderContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#priorityHeader.
    def exitPriorityHeader(self, ctx:RulesDSLParser.PriorityHeaderContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#columnHeader.
    def enterColumnHeader(self, ctx:RulesDSLParser.ColumnHeaderContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#columnHeader.
    def exitColumnHeader(self, ctx:RulesDSLParser.ColumnHeaderContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#columnName.
    def enterColumnName(self, ctx:RulesDSLParser.ColumnNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#columnName.
    def exitColumnName(self, ctx:RulesDSLParser.ColumnNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#tableSeparator.
    def enterTableSeparator(self, ctx:RulesDSLParser.TableSeparatorContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#tableSeparator.
    def exitTableSeparator(self, ctx:RulesDSLParser.TableSeparatorContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#tableRow.
    def enterTableRow(self, ctx:RulesDSLParser.TableRowContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#tableRow.
    def exitTableRow(self, ctx:RulesDSLParser.TableRowContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#priorityCell.
    def enterPriorityCell(self, ctx:RulesDSLParser.PriorityCellContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#priorityCell.
    def exitPriorityCell(self, ctx:RulesDSLParser.PriorityCellContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#cell.
    def enterCell(self, ctx:RulesDSLParser.CellContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#cell.
    def exitCell(self, ctx:RulesDSLParser.CellContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#cellContent.
    def enterCellContent(self, ctx:RulesDSLParser.CellContentContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#cellContent.
    def exitCellContent(self, ctx:RulesDSLParser.CellContentContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#condition.
    def enterCondition(self, ctx:RulesDSLParser.ConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#condition.
    def exitCondition(self, ctx:RulesDSLParser.ConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#exactMatch.
    def enterExactMatch(self, ctx:RulesDSLParser.ExactMatchContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#exactMatch.
    def exitExactMatch(self, ctx:RulesDSLParser.ExactMatchContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#rangeCondition.
    def enterRangeCondition(self, ctx:RulesDSLParser.RangeConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#rangeCondition.
    def exitRangeCondition(self, ctx:RulesDSLParser.RangeConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#setCondition.
    def enterSetCondition(self, ctx:RulesDSLParser.SetConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#setCondition.
    def exitSetCondition(self, ctx:RulesDSLParser.SetConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#patternCondition.
    def enterPatternCondition(self, ctx:RulesDSLParser.PatternConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#patternCondition.
    def exitPatternCondition(self, ctx:RulesDSLParser.PatternConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#nullCondition.
    def enterNullCondition(self, ctx:RulesDSLParser.NullConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#nullCondition.
    def exitNullCondition(self, ctx:RulesDSLParser.NullConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#comparisonCondition.
    def enterComparisonCondition(self, ctx:RulesDSLParser.ComparisonConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#comparisonCondition.
    def exitComparisonCondition(self, ctx:RulesDSLParser.ComparisonConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#expressionCondition.
    def enterExpressionCondition(self, ctx:RulesDSLParser.ExpressionConditionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#expressionCondition.
    def exitExpressionCondition(self, ctx:RulesDSLParser.ExpressionConditionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#action.
    def enterAction(self, ctx:RulesDSLParser.ActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#action.
    def exitAction(self, ctx:RulesDSLParser.ActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#assignAction.
    def enterAssignAction(self, ctx:RulesDSLParser.AssignActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#assignAction.
    def exitAssignAction(self, ctx:RulesDSLParser.AssignActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#calculateAction.
    def enterCalculateAction(self, ctx:RulesDSLParser.CalculateActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#calculateAction.
    def exitCalculateAction(self, ctx:RulesDSLParser.CalculateActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#lookupAction.
    def enterLookupAction(self, ctx:RulesDSLParser.LookupActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#lookupAction.
    def exitLookupAction(self, ctx:RulesDSLParser.LookupActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#callAction.
    def enterCallAction(self, ctx:RulesDSLParser.CallActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#callAction.
    def exitCallAction(self, ctx:RulesDSLParser.CallActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionArg.
    def enterActionArg(self, ctx:RulesDSLParser.ActionArgContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionArg.
    def exitActionArg(self, ctx:RulesDSLParser.ActionArgContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#emitAction.
    def enterEmitAction(self, ctx:RulesDSLParser.EmitActionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#emitAction.
    def exitEmitAction(self, ctx:RulesDSLParser.EmitActionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#returnSpec.
    def enterReturnSpec(self, ctx:RulesDSLParser.ReturnSpecContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#returnSpec.
    def exitReturnSpec(self, ctx:RulesDSLParser.ReturnSpecContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#returnParam.
    def enterReturnParam(self, ctx:RulesDSLParser.ReturnParamContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#returnParam.
    def exitReturnParam(self, ctx:RulesDSLParser.ReturnParamContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#executeSpec.
    def enterExecuteSpec(self, ctx:RulesDSLParser.ExecuteSpecContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#executeSpec.
    def exitExecuteSpec(self, ctx:RulesDSLParser.ExecuteSpecContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#executeType.
    def enterExecuteType(self, ctx:RulesDSLParser.ExecuteTypeContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#executeType.
    def exitExecuteType(self, ctx:RulesDSLParser.ExecuteTypeContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#hybridSpec.
    def enterHybridSpec(self, ctx:RulesDSLParser.HybridSpecContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#hybridSpec.
    def exitHybridSpec(self, ctx:RulesDSLParser.HybridSpecContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#postCalculateBlock.
    def enterPostCalculateBlock(self, ctx:RulesDSLParser.PostCalculateBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#postCalculateBlock.
    def exitPostCalculateBlock(self, ctx:RulesDSLParser.PostCalculateBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#postCalculateStatement.
    def enterPostCalculateStatement(self, ctx:RulesDSLParser.PostCalculateStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#postCalculateStatement.
    def exitPostCalculateStatement(self, ctx:RulesDSLParser.PostCalculateStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#assignmentStatement.
    def enterAssignmentStatement(self, ctx:RulesDSLParser.AssignmentStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#assignmentStatement.
    def exitAssignmentStatement(self, ctx:RulesDSLParser.AssignmentStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#aggregateBlock.
    def enterAggregateBlock(self, ctx:RulesDSLParser.AggregateBlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#aggregateBlock.
    def exitAggregateBlock(self, ctx:RulesDSLParser.AggregateBlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#aggregateStatement.
    def enterAggregateStatement(self, ctx:RulesDSLParser.AggregateStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#aggregateStatement.
    def exitAggregateStatement(self, ctx:RulesDSLParser.AggregateStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#whenExpression.
    def enterWhenExpression(self, ctx:RulesDSLParser.WhenExpressionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#whenExpression.
    def exitWhenExpression(self, ctx:RulesDSLParser.WhenExpressionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#proceduralRuleDef.
    def enterProceduralRuleDef(self, ctx:RulesDSLParser.ProceduralRuleDefContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#proceduralRuleDef.
    def exitProceduralRuleDef(self, ctx:RulesDSLParser.ProceduralRuleDefContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#ruleName.
    def enterRuleName(self, ctx:RulesDSLParser.RuleNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#ruleName.
    def exitRuleName(self, ctx:RulesDSLParser.RuleNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#blockItem.
    def enterBlockItem(self, ctx:RulesDSLParser.BlockItemContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#blockItem.
    def exitBlockItem(self, ctx:RulesDSLParser.BlockItemContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#setStatement.
    def enterSetStatement(self, ctx:RulesDSLParser.SetStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#setStatement.
    def exitSetStatement(self, ctx:RulesDSLParser.SetStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#letStatement.
    def enterLetStatement(self, ctx:RulesDSLParser.LetStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#letStatement.
    def exitLetStatement(self, ctx:RulesDSLParser.LetStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#ruleStep.
    def enterRuleStep(self, ctx:RulesDSLParser.RuleStepContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#ruleStep.
    def exitRuleStep(self, ctx:RulesDSLParser.RuleStepContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#block.
    def enterBlock(self, ctx:RulesDSLParser.BlockContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#block.
    def exitBlock(self, ctx:RulesDSLParser.BlockContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionSequence.
    def enterActionSequence(self, ctx:RulesDSLParser.ActionSequenceContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionSequence.
    def exitActionSequence(self, ctx:RulesDSLParser.ActionSequenceContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#actionCall.
    def enterActionCall(self, ctx:RulesDSLParser.ActionCallContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#actionCall.
    def exitActionCall(self, ctx:RulesDSLParser.ActionCallContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#parameterList.
    def enterParameterList(self, ctx:RulesDSLParser.ParameterListContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#parameterList.
    def exitParameterList(self, ctx:RulesDSLParser.ParameterListContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#parameter.
    def enterParameter(self, ctx:RulesDSLParser.ParameterContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#parameter.
    def exitParameter(self, ctx:RulesDSLParser.ParameterContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#returnStatement.
    def enterReturnStatement(self, ctx:RulesDSLParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#returnStatement.
    def exitReturnStatement(self, ctx:RulesDSLParser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#booleanExpr.
    def enterBooleanExpr(self, ctx:RulesDSLParser.BooleanExprContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#booleanExpr.
    def exitBooleanExpr(self, ctx:RulesDSLParser.BooleanExprContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#booleanTerm.
    def enterBooleanTerm(self, ctx:RulesDSLParser.BooleanTermContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#booleanTerm.
    def exitBooleanTerm(self, ctx:RulesDSLParser.BooleanTermContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#booleanFactor.
    def enterBooleanFactor(self, ctx:RulesDSLParser.BooleanFactorContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#booleanFactor.
    def exitBooleanFactor(self, ctx:RulesDSLParser.BooleanFactorContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#comparisonExpr.
    def enterComparisonExpr(self, ctx:RulesDSLParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#comparisonExpr.
    def exitComparisonExpr(self, ctx:RulesDSLParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#comparisonOp.
    def enterComparisonOp(self, ctx:RulesDSLParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#comparisonOp.
    def exitComparisonOp(self, ctx:RulesDSLParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#valueExpr.
    def enterValueExpr(self, ctx:RulesDSLParser.ValueExprContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#valueExpr.
    def exitValueExpr(self, ctx:RulesDSLParser.ValueExprContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#term.
    def enterTerm(self, ctx:RulesDSLParser.TermContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#term.
    def exitTerm(self, ctx:RulesDSLParser.TermContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#factor.
    def enterFactor(self, ctx:RulesDSLParser.FactorContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#factor.
    def exitFactor(self, ctx:RulesDSLParser.FactorContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#atom.
    def enterAtom(self, ctx:RulesDSLParser.AtomContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#atom.
    def exitAtom(self, ctx:RulesDSLParser.AtomContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#collectionExpr.
    def enterCollectionExpr(self, ctx:RulesDSLParser.CollectionExprContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#collectionExpr.
    def exitCollectionExpr(self, ctx:RulesDSLParser.CollectionExprContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#predicateFunction.
    def enterPredicateFunction(self, ctx:RulesDSLParser.PredicateFunctionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#predicateFunction.
    def exitPredicateFunction(self, ctx:RulesDSLParser.PredicateFunctionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#aggregateFunction.
    def enterAggregateFunction(self, ctx:RulesDSLParser.AggregateFunctionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#aggregateFunction.
    def exitAggregateFunction(self, ctx:RulesDSLParser.AggregateFunctionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#transformFunction.
    def enterTransformFunction(self, ctx:RulesDSLParser.TransformFunctionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#transformFunction.
    def exitTransformFunction(self, ctx:RulesDSLParser.TransformFunctionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#collectionPredicate.
    def enterCollectionPredicate(self, ctx:RulesDSLParser.CollectionPredicateContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#collectionPredicate.
    def exitCollectionPredicate(self, ctx:RulesDSLParser.CollectionPredicateContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#collectionPredicateOr.
    def enterCollectionPredicateOr(self, ctx:RulesDSLParser.CollectionPredicateOrContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#collectionPredicateOr.
    def exitCollectionPredicateOr(self, ctx:RulesDSLParser.CollectionPredicateOrContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#collectionPredicateAnd.
    def enterCollectionPredicateAnd(self, ctx:RulesDSLParser.CollectionPredicateAndContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#collectionPredicateAnd.
    def exitCollectionPredicateAnd(self, ctx:RulesDSLParser.CollectionPredicateAndContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#collectionPredicateAtom.
    def enterCollectionPredicateAtom(self, ctx:RulesDSLParser.CollectionPredicateAtomContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#collectionPredicateAtom.
    def exitCollectionPredicateAtom(self, ctx:RulesDSLParser.CollectionPredicateAtomContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#lambdaExpression.
    def enterLambdaExpression(self, ctx:RulesDSLParser.LambdaExpressionContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#lambdaExpression.
    def exitLambdaExpression(self, ctx:RulesDSLParser.LambdaExpressionContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#arithmeticExpr.
    def enterArithmeticExpr(self, ctx:RulesDSLParser.ArithmeticExprContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#arithmeticExpr.
    def exitArithmeticExpr(self, ctx:RulesDSLParser.ArithmeticExprContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#functionCall.
    def enterFunctionCall(self, ctx:RulesDSLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#functionCall.
    def exitFunctionCall(self, ctx:RulesDSLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#fieldPath.
    def enterFieldPath(self, ctx:RulesDSLParser.FieldPathContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#fieldPath.
    def exitFieldPath(self, ctx:RulesDSLParser.FieldPathContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#attributeIdentifier.
    def enterAttributeIdentifier(self, ctx:RulesDSLParser.AttributeIdentifierContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#attributeIdentifier.
    def exitAttributeIdentifier(self, ctx:RulesDSLParser.AttributeIdentifierContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#valueList.
    def enterValueList(self, ctx:RulesDSLParser.ValueListContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#valueList.
    def exitValueList(self, ctx:RulesDSLParser.ValueListContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#listLiteral.
    def enterListLiteral(self, ctx:RulesDSLParser.ListLiteralContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#listLiteral.
    def exitListLiteral(self, ctx:RulesDSLParser.ListLiteralContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#objectLiteral.
    def enterObjectLiteral(self, ctx:RulesDSLParser.ObjectLiteralContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#objectLiteral.
    def exitObjectLiteral(self, ctx:RulesDSLParser.ObjectLiteralContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#objectField.
    def enterObjectField(self, ctx:RulesDSLParser.ObjectFieldContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#objectField.
    def exitObjectField(self, ctx:RulesDSLParser.ObjectFieldContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#objectFieldName.
    def enterObjectFieldName(self, ctx:RulesDSLParser.ObjectFieldNameContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#objectFieldName.
    def exitObjectFieldName(self, ctx:RulesDSLParser.ObjectFieldNameContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#literal.
    def enterLiteral(self, ctx:RulesDSLParser.LiteralContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#literal.
    def exitLiteral(self, ctx:RulesDSLParser.LiteralContext):
        pass


    # Enter a parse tree produced by RulesDSLParser#numberLiteral.
    def enterNumberLiteral(self, ctx:RulesDSLParser.NumberLiteralContext):
        pass

    # Exit a parse tree produced by RulesDSLParser#numberLiteral.
    def exitNumberLiteral(self, ctx:RulesDSLParser.NumberLiteralContext):
        pass



del RulesDSLParser