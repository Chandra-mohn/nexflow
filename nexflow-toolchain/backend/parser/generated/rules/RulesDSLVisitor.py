# Nexflow DSL Toolchain
# Author: Chandra Mohn

# Generated from RulesDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .RulesDSLParser import RulesDSLParser
else:
    from RulesDSLParser import RulesDSLParser

# This class defines a complete generic visitor for a parse tree produced by RulesDSLParser.

class RulesDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RulesDSLParser#program.
    def visitProgram(self, ctx:RulesDSLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#importStatement.
    def visitImportStatement(self, ctx:RulesDSLParser.ImportStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#importPath.
    def visitImportPath(self, ctx:RulesDSLParser.ImportPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#importPathSegment.
    def visitImportPathSegment(self, ctx:RulesDSLParser.ImportPathSegmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#importFileExtension.
    def visitImportFileExtension(self, ctx:RulesDSLParser.ImportFileExtensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#servicesBlock.
    def visitServicesBlock(self, ctx:RulesDSLParser.ServicesBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceDecl.
    def visitServiceDecl(self, ctx:RulesDSLParser.ServiceDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceName.
    def visitServiceName(self, ctx:RulesDSLParser.ServiceNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceClassName.
    def visitServiceClassName(self, ctx:RulesDSLParser.ServiceClassNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceMethodName.
    def visitServiceMethodName(self, ctx:RulesDSLParser.ServiceMethodNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceType.
    def visitServiceType(self, ctx:RulesDSLParser.ServiceTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceParamList.
    def visitServiceParamList(self, ctx:RulesDSLParser.ServiceParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceParam.
    def visitServiceParam(self, ctx:RulesDSLParser.ServiceParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceReturnType.
    def visitServiceReturnType(self, ctx:RulesDSLParser.ServiceReturnTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceOptions.
    def visitServiceOptions(self, ctx:RulesDSLParser.ServiceOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#serviceOption.
    def visitServiceOption(self, ctx:RulesDSLParser.ServiceOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#duration.
    def visitDuration(self, ctx:RulesDSLParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#durationUnit.
    def visitDurationUnit(self, ctx:RulesDSLParser.DurationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionsBlock.
    def visitActionsBlock(self, ctx:RulesDSLParser.ActionsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionDecl.
    def visitActionDecl(self, ctx:RulesDSLParser.ActionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionDeclName.
    def visitActionDeclName(self, ctx:RulesDSLParser.ActionDeclNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionParamList.
    def visitActionParamList(self, ctx:RulesDSLParser.ActionParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionParam.
    def visitActionParam(self, ctx:RulesDSLParser.ActionParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionTarget.
    def visitActionTarget(self, ctx:RulesDSLParser.ActionTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#emitTarget.
    def visitEmitTarget(self, ctx:RulesDSLParser.EmitTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#stateTarget.
    def visitStateTarget(self, ctx:RulesDSLParser.StateTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#stateOperation.
    def visitStateOperation(self, ctx:RulesDSLParser.StateOperationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#stateOperationArg.
    def visitStateOperationArg(self, ctx:RulesDSLParser.StateOperationArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#auditTarget.
    def visitAuditTarget(self, ctx:RulesDSLParser.AuditTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#callTarget.
    def visitCallTarget(self, ctx:RulesDSLParser.CallTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#decisionTableDef.
    def visitDecisionTableDef(self, ctx:RulesDSLParser.DecisionTableDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#versionDecl.
    def visitVersionDecl(self, ctx:RulesDSLParser.VersionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#tableName.
    def visitTableName(self, ctx:RulesDSLParser.TableNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#hitPolicyDecl.
    def visitHitPolicyDecl(self, ctx:RulesDSLParser.HitPolicyDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#hitPolicyType.
    def visitHitPolicyType(self, ctx:RulesDSLParser.HitPolicyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#descriptionDecl.
    def visitDescriptionDecl(self, ctx:RulesDSLParser.DescriptionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#stringLiteral.
    def visitStringLiteral(self, ctx:RulesDSLParser.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#givenBlock.
    def visitGivenBlock(self, ctx:RulesDSLParser.GivenBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#inputParam.
    def visitInputParam(self, ctx:RulesDSLParser.InputParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#paramName.
    def visitParamName(self, ctx:RulesDSLParser.ParamNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#paramType.
    def visitParamType(self, ctx:RulesDSLParser.ParamTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#baseType.
    def visitBaseType(self, ctx:RulesDSLParser.BaseTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#inlineComment.
    def visitInlineComment(self, ctx:RulesDSLParser.InlineCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#decideBlock.
    def visitDecideBlock(self, ctx:RulesDSLParser.DecideBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#tableMatrix.
    def visitTableMatrix(self, ctx:RulesDSLParser.TableMatrixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#tableHeader.
    def visitTableHeader(self, ctx:RulesDSLParser.TableHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#priorityHeader.
    def visitPriorityHeader(self, ctx:RulesDSLParser.PriorityHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#columnHeader.
    def visitColumnHeader(self, ctx:RulesDSLParser.ColumnHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#columnName.
    def visitColumnName(self, ctx:RulesDSLParser.ColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#tableSeparator.
    def visitTableSeparator(self, ctx:RulesDSLParser.TableSeparatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#tableRow.
    def visitTableRow(self, ctx:RulesDSLParser.TableRowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#priorityCell.
    def visitPriorityCell(self, ctx:RulesDSLParser.PriorityCellContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#cell.
    def visitCell(self, ctx:RulesDSLParser.CellContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#cellContent.
    def visitCellContent(self, ctx:RulesDSLParser.CellContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#condition.
    def visitCondition(self, ctx:RulesDSLParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#exactMatch.
    def visitExactMatch(self, ctx:RulesDSLParser.ExactMatchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#rangeCondition.
    def visitRangeCondition(self, ctx:RulesDSLParser.RangeConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#setCondition.
    def visitSetCondition(self, ctx:RulesDSLParser.SetConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#patternCondition.
    def visitPatternCondition(self, ctx:RulesDSLParser.PatternConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#nullCondition.
    def visitNullCondition(self, ctx:RulesDSLParser.NullConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#comparisonCondition.
    def visitComparisonCondition(self, ctx:RulesDSLParser.ComparisonConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#expressionCondition.
    def visitExpressionCondition(self, ctx:RulesDSLParser.ExpressionConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#markerStateCondition.
    def visitMarkerStateCondition(self, ctx:RulesDSLParser.MarkerStateConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#action.
    def visitAction(self, ctx:RulesDSLParser.ActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#assignAction.
    def visitAssignAction(self, ctx:RulesDSLParser.AssignActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#calculateAction.
    def visitCalculateAction(self, ctx:RulesDSLParser.CalculateActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#lookupAction.
    def visitLookupAction(self, ctx:RulesDSLParser.LookupActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#callAction.
    def visitCallAction(self, ctx:RulesDSLParser.CallActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionArg.
    def visitActionArg(self, ctx:RulesDSLParser.ActionArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#emitAction.
    def visitEmitAction(self, ctx:RulesDSLParser.EmitActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#returnSpec.
    def visitReturnSpec(self, ctx:RulesDSLParser.ReturnSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#returnParam.
    def visitReturnParam(self, ctx:RulesDSLParser.ReturnParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#executeSpec.
    def visitExecuteSpec(self, ctx:RulesDSLParser.ExecuteSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#executeType.
    def visitExecuteType(self, ctx:RulesDSLParser.ExecuteTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#hybridSpec.
    def visitHybridSpec(self, ctx:RulesDSLParser.HybridSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#postCalculateBlock.
    def visitPostCalculateBlock(self, ctx:RulesDSLParser.PostCalculateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#postCalculateStatement.
    def visitPostCalculateStatement(self, ctx:RulesDSLParser.PostCalculateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#assignmentStatement.
    def visitAssignmentStatement(self, ctx:RulesDSLParser.AssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#aggregateBlock.
    def visitAggregateBlock(self, ctx:RulesDSLParser.AggregateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#aggregateStatement.
    def visitAggregateStatement(self, ctx:RulesDSLParser.AggregateStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#whenExpression.
    def visitWhenExpression(self, ctx:RulesDSLParser.WhenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#proceduralRuleDef.
    def visitProceduralRuleDef(self, ctx:RulesDSLParser.ProceduralRuleDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#ruleName.
    def visitRuleName(self, ctx:RulesDSLParser.RuleNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#blockItem.
    def visitBlockItem(self, ctx:RulesDSLParser.BlockItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#setStatement.
    def visitSetStatement(self, ctx:RulesDSLParser.SetStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#letStatement.
    def visitLetStatement(self, ctx:RulesDSLParser.LetStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#ruleStep.
    def visitRuleStep(self, ctx:RulesDSLParser.RuleStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#block.
    def visitBlock(self, ctx:RulesDSLParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionSequence.
    def visitActionSequence(self, ctx:RulesDSLParser.ActionSequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#actionCall.
    def visitActionCall(self, ctx:RulesDSLParser.ActionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#parameterList.
    def visitParameterList(self, ctx:RulesDSLParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#parameter.
    def visitParameter(self, ctx:RulesDSLParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#returnStatement.
    def visitReturnStatement(self, ctx:RulesDSLParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#booleanExpr.
    def visitBooleanExpr(self, ctx:RulesDSLParser.BooleanExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#booleanTerm.
    def visitBooleanTerm(self, ctx:RulesDSLParser.BooleanTermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#booleanFactor.
    def visitBooleanFactor(self, ctx:RulesDSLParser.BooleanFactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#comparisonExpr.
    def visitComparisonExpr(self, ctx:RulesDSLParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#comparisonOp.
    def visitComparisonOp(self, ctx:RulesDSLParser.ComparisonOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#valueExpr.
    def visitValueExpr(self, ctx:RulesDSLParser.ValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#term.
    def visitTerm(self, ctx:RulesDSLParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#factor.
    def visitFactor(self, ctx:RulesDSLParser.FactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#atom.
    def visitAtom(self, ctx:RulesDSLParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#collectionExpr.
    def visitCollectionExpr(self, ctx:RulesDSLParser.CollectionExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#predicateFunction.
    def visitPredicateFunction(self, ctx:RulesDSLParser.PredicateFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#aggregateFunction.
    def visitAggregateFunction(self, ctx:RulesDSLParser.AggregateFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#transformFunction.
    def visitTransformFunction(self, ctx:RulesDSLParser.TransformFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#collectionPredicate.
    def visitCollectionPredicate(self, ctx:RulesDSLParser.CollectionPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#collectionPredicateOr.
    def visitCollectionPredicateOr(self, ctx:RulesDSLParser.CollectionPredicateOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#collectionPredicateAnd.
    def visitCollectionPredicateAnd(self, ctx:RulesDSLParser.CollectionPredicateAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#collectionPredicateAtom.
    def visitCollectionPredicateAtom(self, ctx:RulesDSLParser.CollectionPredicateAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#lambdaExpression.
    def visitLambdaExpression(self, ctx:RulesDSLParser.LambdaExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#arithmeticExpr.
    def visitArithmeticExpr(self, ctx:RulesDSLParser.ArithmeticExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#functionCall.
    def visitFunctionCall(self, ctx:RulesDSLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#fieldPath.
    def visitFieldPath(self, ctx:RulesDSLParser.FieldPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#attributeIdentifier.
    def visitAttributeIdentifier(self, ctx:RulesDSLParser.AttributeIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#valueList.
    def visitValueList(self, ctx:RulesDSLParser.ValueListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#listLiteral.
    def visitListLiteral(self, ctx:RulesDSLParser.ListLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#objectLiteral.
    def visitObjectLiteral(self, ctx:RulesDSLParser.ObjectLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#objectField.
    def visitObjectField(self, ctx:RulesDSLParser.ObjectFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#objectFieldName.
    def visitObjectFieldName(self, ctx:RulesDSLParser.ObjectFieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#literal.
    def visitLiteral(self, ctx:RulesDSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#numberLiteral.
    def visitNumberLiteral(self, ctx:RulesDSLParser.NumberLiteralContext):
        return self.visitChildren(ctx)



del RulesDSLParser