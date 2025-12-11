# Generated from grammar/TransformDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TransformDSLParser import TransformDSLParser
else:
    from TransformDSLParser import TransformDSLParser

# This class defines a complete generic visitor for a parse tree produced by TransformDSLParser.

class TransformDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TransformDSLParser#program.
    def visitProgram(self, ctx:TransformDSLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#transformDef.
    def visitTransformDef(self, ctx:TransformDSLParser.TransformDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#idempotentDecl.
    def visitIdempotentDecl(self, ctx:TransformDSLParser.IdempotentDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#lookupDecl.
    def visitLookupDecl(self, ctx:TransformDSLParser.LookupDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#lookupsBlock.
    def visitLookupsBlock(self, ctx:TransformDSLParser.LookupsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#lookupFieldDecl.
    def visitLookupFieldDecl(self, ctx:TransformDSLParser.LookupFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#stateDecl.
    def visitStateDecl(self, ctx:TransformDSLParser.StateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#paramsBlock.
    def visitParamsBlock(self, ctx:TransformDSLParser.ParamsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#paramDecl.
    def visitParamDecl(self, ctx:TransformDSLParser.ParamDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#paramQualifiers.
    def visitParamQualifiers(self, ctx:TransformDSLParser.ParamQualifiersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#paramDefault.
    def visitParamDefault(self, ctx:TransformDSLParser.ParamDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#transformName.
    def visitTransformName(self, ctx:TransformDSLParser.TransformNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#transformMetadata.
    def visitTransformMetadata(self, ctx:TransformDSLParser.TransformMetadataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#versionDecl.
    def visitVersionDecl(self, ctx:TransformDSLParser.VersionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#descriptionDecl.
    def visitDescriptionDecl(self, ctx:TransformDSLParser.DescriptionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#previousVersionDecl.
    def visitPreviousVersionDecl(self, ctx:TransformDSLParser.PreviousVersionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#compatibilityDecl.
    def visitCompatibilityDecl(self, ctx:TransformDSLParser.CompatibilityDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#compatibilityMode.
    def visitCompatibilityMode(self, ctx:TransformDSLParser.CompatibilityModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#purityDecl.
    def visitPurityDecl(self, ctx:TransformDSLParser.PurityDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#cacheDecl.
    def visitCacheDecl(self, ctx:TransformDSLParser.CacheDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#cacheTtl.
    def visitCacheTtl(self, ctx:TransformDSLParser.CacheTtlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#cacheKey.
    def visitCacheKey(self, ctx:TransformDSLParser.CacheKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#transformBlockDef.
    def visitTransformBlockDef(self, ctx:TransformDSLParser.TransformBlockDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#useBlock.
    def visitUseBlock(self, ctx:TransformDSLParser.UseBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#inputSpec.
    def visitInputSpec(self, ctx:TransformDSLParser.InputSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#inputFieldDecl.
    def visitInputFieldDecl(self, ctx:TransformDSLParser.InputFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#outputSpec.
    def visitOutputSpec(self, ctx:TransformDSLParser.OutputSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#outputFieldDecl.
    def visitOutputFieldDecl(self, ctx:TransformDSLParser.OutputFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#fieldType.
    def visitFieldType(self, ctx:TransformDSLParser.FieldTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#baseType.
    def visitBaseType(self, ctx:TransformDSLParser.BaseTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#collectionType.
    def visitCollectionType(self, ctx:TransformDSLParser.CollectionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#constraint.
    def visitConstraint(self, ctx:TransformDSLParser.ConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#constraintSpec.
    def visitConstraintSpec(self, ctx:TransformDSLParser.ConstraintSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#rangeSpec.
    def visitRangeSpec(self, ctx:TransformDSLParser.RangeSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#lengthSpec.
    def visitLengthSpec(self, ctx:TransformDSLParser.LengthSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#valueList.
    def visitValueList(self, ctx:TransformDSLParser.ValueListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#qualifiers.
    def visitQualifiers(self, ctx:TransformDSLParser.QualifiersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#qualifier.
    def visitQualifier(self, ctx:TransformDSLParser.QualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#applyBlock.
    def visitApplyBlock(self, ctx:TransformDSLParser.ApplyBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#statement.
    def visitStatement(self, ctx:TransformDSLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#assignment.
    def visitAssignment(self, ctx:TransformDSLParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#letAssignment.
    def visitLetAssignment(self, ctx:TransformDSLParser.LetAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#mappingsBlock.
    def visitMappingsBlock(self, ctx:TransformDSLParser.MappingsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#mapping.
    def visitMapping(self, ctx:TransformDSLParser.MappingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#composeBlock.
    def visitComposeBlock(self, ctx:TransformDSLParser.ComposeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#composeType.
    def visitComposeType(self, ctx:TransformDSLParser.ComposeTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#composeRef.
    def visitComposeRef(self, ctx:TransformDSLParser.ComposeRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#thenBlock.
    def visitThenBlock(self, ctx:TransformDSLParser.ThenBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#validateInputBlock.
    def visitValidateInputBlock(self, ctx:TransformDSLParser.ValidateInputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#validateOutputBlock.
    def visitValidateOutputBlock(self, ctx:TransformDSLParser.ValidateOutputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#validationRule.
    def visitValidationRule(self, ctx:TransformDSLParser.ValidationRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#validationMessage.
    def visitValidationMessage(self, ctx:TransformDSLParser.ValidationMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#validationMessageObject.
    def visitValidationMessageObject(self, ctx:TransformDSLParser.ValidationMessageObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#severityLevel.
    def visitSeverityLevel(self, ctx:TransformDSLParser.SeverityLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#invariantBlock.
    def visitInvariantBlock(self, ctx:TransformDSLParser.InvariantBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#onErrorBlock.
    def visitOnErrorBlock(self, ctx:TransformDSLParser.OnErrorBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#errorStatement.
    def visitErrorStatement(self, ctx:TransformDSLParser.ErrorStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#errorAction.
    def visitErrorAction(self, ctx:TransformDSLParser.ErrorActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#logErrorCall.
    def visitLogErrorCall(self, ctx:TransformDSLParser.LogErrorCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#emitStatement.
    def visitEmitStatement(self, ctx:TransformDSLParser.EmitStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#emitMode.
    def visitEmitMode(self, ctx:TransformDSLParser.EmitModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#rejectStatement.
    def visitRejectStatement(self, ctx:TransformDSLParser.RejectStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#rejectArg.
    def visitRejectArg(self, ctx:TransformDSLParser.RejectArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#errorActionType.
    def visitErrorActionType(self, ctx:TransformDSLParser.ErrorActionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#logLevel.
    def visitLogLevel(self, ctx:TransformDSLParser.LogLevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#onInvalidBlock.
    def visitOnInvalidBlock(self, ctx:TransformDSLParser.OnInvalidBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#invalidAction.
    def visitInvalidAction(self, ctx:TransformDSLParser.InvalidActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#onChangeBlock.
    def visitOnChangeBlock(self, ctx:TransformDSLParser.OnChangeBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#recalculateBlock.
    def visitRecalculateBlock(self, ctx:TransformDSLParser.RecalculateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#expression.
    def visitExpression(self, ctx:TransformDSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:TransformDSLParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#objectLiteral.
    def visitObjectLiteral(self, ctx:TransformDSLParser.ObjectLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#objectField.
    def visitObjectField(self, ctx:TransformDSLParser.ObjectFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#objectFieldName.
    def visitObjectFieldName(self, ctx:TransformDSLParser.ObjectFieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#lambdaExpression.
    def visitLambdaExpression(self, ctx:TransformDSLParser.LambdaExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#listElements.
    def visitListElements(self, ctx:TransformDSLParser.ListElementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#whenExpression.
    def visitWhenExpression(self, ctx:TransformDSLParser.WhenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#indexExpression.
    def visitIndexExpression(self, ctx:TransformDSLParser.IndexExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#optionalChainExpression.
    def visitOptionalChainExpression(self, ctx:TransformDSLParser.OptionalChainExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#binaryOp.
    def visitBinaryOp(self, ctx:TransformDSLParser.BinaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#arithmeticOp.
    def visitArithmeticOp(self, ctx:TransformDSLParser.ArithmeticOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#comparisonOp.
    def visitComparisonOp(self, ctx:TransformDSLParser.ComparisonOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#logicalOp.
    def visitLogicalOp(self, ctx:TransformDSLParser.LogicalOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#unaryOp.
    def visitUnaryOp(self, ctx:TransformDSLParser.UnaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#functionCall.
    def visitFunctionCall(self, ctx:TransformDSLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#functionName.
    def visitFunctionName(self, ctx:TransformDSLParser.FunctionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#listLiteral.
    def visitListLiteral(self, ctx:TransformDSLParser.ListLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#fieldPath.
    def visitFieldPath(self, ctx:TransformDSLParser.FieldPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#fieldOrKeyword.
    def visitFieldOrKeyword(self, ctx:TransformDSLParser.FieldOrKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#fieldArray.
    def visitFieldArray(self, ctx:TransformDSLParser.FieldArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#fieldName.
    def visitFieldName(self, ctx:TransformDSLParser.FieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#duration.
    def visitDuration(self, ctx:TransformDSLParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#timeUnit.
    def visitTimeUnit(self, ctx:TransformDSLParser.TimeUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#literal.
    def visitLiteral(self, ctx:TransformDSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TransformDSLParser#numberLiteral.
    def visitNumberLiteral(self, ctx:TransformDSLParser.NumberLiteralContext):
        return self.visitChildren(ctx)



del TransformDSLParser