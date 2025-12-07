# Generated from grammar/RulesDSL.g4 by ANTLR 4.13.2
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


    # Visit a parse tree produced by RulesDSLParser#decisionTableDef.
    def visitDecisionTableDef(self, ctx:RulesDSLParser.DecisionTableDefContext):
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


    # Visit a parse tree produced by RulesDSLParser#proceduralRuleDef.
    def visitProceduralRuleDef(self, ctx:RulesDSLParser.ProceduralRuleDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#ruleName.
    def visitRuleName(self, ctx:RulesDSLParser.RuleNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#blockItem.
    def visitBlockItem(self, ctx:RulesDSLParser.BlockItemContext):
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


    # Visit a parse tree produced by RulesDSLParser#literal.
    def visitLiteral(self, ctx:RulesDSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RulesDSLParser#numberLiteral.
    def visitNumberLiteral(self, ctx:RulesDSLParser.NumberLiteralContext):
        return self.visitChildren(ctx)



del RulesDSLParser