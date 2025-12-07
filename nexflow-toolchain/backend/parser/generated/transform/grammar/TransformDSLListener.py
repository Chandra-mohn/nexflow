# Generated from grammar/TransformDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TransformDSLParser import TransformDSLParser
else:
    from TransformDSLParser import TransformDSLParser

# This class defines a complete listener for a parse tree produced by TransformDSLParser.
class TransformDSLListener(ParseTreeListener):

    # Enter a parse tree produced by TransformDSLParser#program.
    def enterProgram(self, ctx:TransformDSLParser.ProgramContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#program.
    def exitProgram(self, ctx:TransformDSLParser.ProgramContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#transformDef.
    def enterTransformDef(self, ctx:TransformDSLParser.TransformDefContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#transformDef.
    def exitTransformDef(self, ctx:TransformDSLParser.TransformDefContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#transformName.
    def enterTransformName(self, ctx:TransformDSLParser.TransformNameContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#transformName.
    def exitTransformName(self, ctx:TransformDSLParser.TransformNameContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#transformMetadata.
    def enterTransformMetadata(self, ctx:TransformDSLParser.TransformMetadataContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#transformMetadata.
    def exitTransformMetadata(self, ctx:TransformDSLParser.TransformMetadataContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#versionDecl.
    def enterVersionDecl(self, ctx:TransformDSLParser.VersionDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#versionDecl.
    def exitVersionDecl(self, ctx:TransformDSLParser.VersionDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#descriptionDecl.
    def enterDescriptionDecl(self, ctx:TransformDSLParser.DescriptionDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#descriptionDecl.
    def exitDescriptionDecl(self, ctx:TransformDSLParser.DescriptionDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#previousVersionDecl.
    def enterPreviousVersionDecl(self, ctx:TransformDSLParser.PreviousVersionDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#previousVersionDecl.
    def exitPreviousVersionDecl(self, ctx:TransformDSLParser.PreviousVersionDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#compatibilityDecl.
    def enterCompatibilityDecl(self, ctx:TransformDSLParser.CompatibilityDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#compatibilityDecl.
    def exitCompatibilityDecl(self, ctx:TransformDSLParser.CompatibilityDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#compatibilityMode.
    def enterCompatibilityMode(self, ctx:TransformDSLParser.CompatibilityModeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#compatibilityMode.
    def exitCompatibilityMode(self, ctx:TransformDSLParser.CompatibilityModeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#purityDecl.
    def enterPurityDecl(self, ctx:TransformDSLParser.PurityDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#purityDecl.
    def exitPurityDecl(self, ctx:TransformDSLParser.PurityDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#cacheDecl.
    def enterCacheDecl(self, ctx:TransformDSLParser.CacheDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#cacheDecl.
    def exitCacheDecl(self, ctx:TransformDSLParser.CacheDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#cacheTtl.
    def enterCacheTtl(self, ctx:TransformDSLParser.CacheTtlContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#cacheTtl.
    def exitCacheTtl(self, ctx:TransformDSLParser.CacheTtlContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#cacheKey.
    def enterCacheKey(self, ctx:TransformDSLParser.CacheKeyContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#cacheKey.
    def exitCacheKey(self, ctx:TransformDSLParser.CacheKeyContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#transformBlockDef.
    def enterTransformBlockDef(self, ctx:TransformDSLParser.TransformBlockDefContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#transformBlockDef.
    def exitTransformBlockDef(self, ctx:TransformDSLParser.TransformBlockDefContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#useBlock.
    def enterUseBlock(self, ctx:TransformDSLParser.UseBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#useBlock.
    def exitUseBlock(self, ctx:TransformDSLParser.UseBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#inputSpec.
    def enterInputSpec(self, ctx:TransformDSLParser.InputSpecContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#inputSpec.
    def exitInputSpec(self, ctx:TransformDSLParser.InputSpecContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#inputFieldDecl.
    def enterInputFieldDecl(self, ctx:TransformDSLParser.InputFieldDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#inputFieldDecl.
    def exitInputFieldDecl(self, ctx:TransformDSLParser.InputFieldDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#outputSpec.
    def enterOutputSpec(self, ctx:TransformDSLParser.OutputSpecContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#outputSpec.
    def exitOutputSpec(self, ctx:TransformDSLParser.OutputSpecContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#outputFieldDecl.
    def enterOutputFieldDecl(self, ctx:TransformDSLParser.OutputFieldDeclContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#outputFieldDecl.
    def exitOutputFieldDecl(self, ctx:TransformDSLParser.OutputFieldDeclContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#fieldType.
    def enterFieldType(self, ctx:TransformDSLParser.FieldTypeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#fieldType.
    def exitFieldType(self, ctx:TransformDSLParser.FieldTypeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#baseType.
    def enterBaseType(self, ctx:TransformDSLParser.BaseTypeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#baseType.
    def exitBaseType(self, ctx:TransformDSLParser.BaseTypeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#collectionType.
    def enterCollectionType(self, ctx:TransformDSLParser.CollectionTypeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#collectionType.
    def exitCollectionType(self, ctx:TransformDSLParser.CollectionTypeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#constraint.
    def enterConstraint(self, ctx:TransformDSLParser.ConstraintContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#constraint.
    def exitConstraint(self, ctx:TransformDSLParser.ConstraintContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#constraintSpec.
    def enterConstraintSpec(self, ctx:TransformDSLParser.ConstraintSpecContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#constraintSpec.
    def exitConstraintSpec(self, ctx:TransformDSLParser.ConstraintSpecContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#rangeSpec.
    def enterRangeSpec(self, ctx:TransformDSLParser.RangeSpecContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#rangeSpec.
    def exitRangeSpec(self, ctx:TransformDSLParser.RangeSpecContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#lengthSpec.
    def enterLengthSpec(self, ctx:TransformDSLParser.LengthSpecContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#lengthSpec.
    def exitLengthSpec(self, ctx:TransformDSLParser.LengthSpecContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#valueList.
    def enterValueList(self, ctx:TransformDSLParser.ValueListContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#valueList.
    def exitValueList(self, ctx:TransformDSLParser.ValueListContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#qualifiers.
    def enterQualifiers(self, ctx:TransformDSLParser.QualifiersContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#qualifiers.
    def exitQualifiers(self, ctx:TransformDSLParser.QualifiersContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#qualifier.
    def enterQualifier(self, ctx:TransformDSLParser.QualifierContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#qualifier.
    def exitQualifier(self, ctx:TransformDSLParser.QualifierContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#applyBlock.
    def enterApplyBlock(self, ctx:TransformDSLParser.ApplyBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#applyBlock.
    def exitApplyBlock(self, ctx:TransformDSLParser.ApplyBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#statement.
    def enterStatement(self, ctx:TransformDSLParser.StatementContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#statement.
    def exitStatement(self, ctx:TransformDSLParser.StatementContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#assignment.
    def enterAssignment(self, ctx:TransformDSLParser.AssignmentContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#assignment.
    def exitAssignment(self, ctx:TransformDSLParser.AssignmentContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#localAssignment.
    def enterLocalAssignment(self, ctx:TransformDSLParser.LocalAssignmentContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#localAssignment.
    def exitLocalAssignment(self, ctx:TransformDSLParser.LocalAssignmentContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#mappingsBlock.
    def enterMappingsBlock(self, ctx:TransformDSLParser.MappingsBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#mappingsBlock.
    def exitMappingsBlock(self, ctx:TransformDSLParser.MappingsBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#mapping.
    def enterMapping(self, ctx:TransformDSLParser.MappingContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#mapping.
    def exitMapping(self, ctx:TransformDSLParser.MappingContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#composeBlock.
    def enterComposeBlock(self, ctx:TransformDSLParser.ComposeBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#composeBlock.
    def exitComposeBlock(self, ctx:TransformDSLParser.ComposeBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#composeType.
    def enterComposeType(self, ctx:TransformDSLParser.ComposeTypeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#composeType.
    def exitComposeType(self, ctx:TransformDSLParser.ComposeTypeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#composeRef.
    def enterComposeRef(self, ctx:TransformDSLParser.ComposeRefContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#composeRef.
    def exitComposeRef(self, ctx:TransformDSLParser.ComposeRefContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#thenBlock.
    def enterThenBlock(self, ctx:TransformDSLParser.ThenBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#thenBlock.
    def exitThenBlock(self, ctx:TransformDSLParser.ThenBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#validateInputBlock.
    def enterValidateInputBlock(self, ctx:TransformDSLParser.ValidateInputBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#validateInputBlock.
    def exitValidateInputBlock(self, ctx:TransformDSLParser.ValidateInputBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#validateOutputBlock.
    def enterValidateOutputBlock(self, ctx:TransformDSLParser.ValidateOutputBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#validateOutputBlock.
    def exitValidateOutputBlock(self, ctx:TransformDSLParser.ValidateOutputBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#validationRule.
    def enterValidationRule(self, ctx:TransformDSLParser.ValidationRuleContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#validationRule.
    def exitValidationRule(self, ctx:TransformDSLParser.ValidationRuleContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#validationMessage.
    def enterValidationMessage(self, ctx:TransformDSLParser.ValidationMessageContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#validationMessage.
    def exitValidationMessage(self, ctx:TransformDSLParser.ValidationMessageContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#validationMessageObject.
    def enterValidationMessageObject(self, ctx:TransformDSLParser.ValidationMessageObjectContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#validationMessageObject.
    def exitValidationMessageObject(self, ctx:TransformDSLParser.ValidationMessageObjectContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#severityLevel.
    def enterSeverityLevel(self, ctx:TransformDSLParser.SeverityLevelContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#severityLevel.
    def exitSeverityLevel(self, ctx:TransformDSLParser.SeverityLevelContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#invariantBlock.
    def enterInvariantBlock(self, ctx:TransformDSLParser.InvariantBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#invariantBlock.
    def exitInvariantBlock(self, ctx:TransformDSLParser.InvariantBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#onErrorBlock.
    def enterOnErrorBlock(self, ctx:TransformDSLParser.OnErrorBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#onErrorBlock.
    def exitOnErrorBlock(self, ctx:TransformDSLParser.OnErrorBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#errorAction.
    def enterErrorAction(self, ctx:TransformDSLParser.ErrorActionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#errorAction.
    def exitErrorAction(self, ctx:TransformDSLParser.ErrorActionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#errorActionType.
    def enterErrorActionType(self, ctx:TransformDSLParser.ErrorActionTypeContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#errorActionType.
    def exitErrorActionType(self, ctx:TransformDSLParser.ErrorActionTypeContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#logLevel.
    def enterLogLevel(self, ctx:TransformDSLParser.LogLevelContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#logLevel.
    def exitLogLevel(self, ctx:TransformDSLParser.LogLevelContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#onInvalidBlock.
    def enterOnInvalidBlock(self, ctx:TransformDSLParser.OnInvalidBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#onInvalidBlock.
    def exitOnInvalidBlock(self, ctx:TransformDSLParser.OnInvalidBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#invalidAction.
    def enterInvalidAction(self, ctx:TransformDSLParser.InvalidActionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#invalidAction.
    def exitInvalidAction(self, ctx:TransformDSLParser.InvalidActionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#onChangeBlock.
    def enterOnChangeBlock(self, ctx:TransformDSLParser.OnChangeBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#onChangeBlock.
    def exitOnChangeBlock(self, ctx:TransformDSLParser.OnChangeBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#recalculateBlock.
    def enterRecalculateBlock(self, ctx:TransformDSLParser.RecalculateBlockContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#recalculateBlock.
    def exitRecalculateBlock(self, ctx:TransformDSLParser.RecalculateBlockContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#expression.
    def enterExpression(self, ctx:TransformDSLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#expression.
    def exitExpression(self, ctx:TransformDSLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:TransformDSLParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:TransformDSLParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#whenExpression.
    def enterWhenExpression(self, ctx:TransformDSLParser.WhenExpressionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#whenExpression.
    def exitWhenExpression(self, ctx:TransformDSLParser.WhenExpressionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#indexExpression.
    def enterIndexExpression(self, ctx:TransformDSLParser.IndexExpressionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#indexExpression.
    def exitIndexExpression(self, ctx:TransformDSLParser.IndexExpressionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#optionalChainExpression.
    def enterOptionalChainExpression(self, ctx:TransformDSLParser.OptionalChainExpressionContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#optionalChainExpression.
    def exitOptionalChainExpression(self, ctx:TransformDSLParser.OptionalChainExpressionContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#binaryOp.
    def enterBinaryOp(self, ctx:TransformDSLParser.BinaryOpContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#binaryOp.
    def exitBinaryOp(self, ctx:TransformDSLParser.BinaryOpContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#arithmeticOp.
    def enterArithmeticOp(self, ctx:TransformDSLParser.ArithmeticOpContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#arithmeticOp.
    def exitArithmeticOp(self, ctx:TransformDSLParser.ArithmeticOpContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#comparisonOp.
    def enterComparisonOp(self, ctx:TransformDSLParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#comparisonOp.
    def exitComparisonOp(self, ctx:TransformDSLParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#logicalOp.
    def enterLogicalOp(self, ctx:TransformDSLParser.LogicalOpContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#logicalOp.
    def exitLogicalOp(self, ctx:TransformDSLParser.LogicalOpContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#unaryOp.
    def enterUnaryOp(self, ctx:TransformDSLParser.UnaryOpContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#unaryOp.
    def exitUnaryOp(self, ctx:TransformDSLParser.UnaryOpContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#functionCall.
    def enterFunctionCall(self, ctx:TransformDSLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#functionCall.
    def exitFunctionCall(self, ctx:TransformDSLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#listLiteral.
    def enterListLiteral(self, ctx:TransformDSLParser.ListLiteralContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#listLiteral.
    def exitListLiteral(self, ctx:TransformDSLParser.ListLiteralContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#fieldPath.
    def enterFieldPath(self, ctx:TransformDSLParser.FieldPathContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#fieldPath.
    def exitFieldPath(self, ctx:TransformDSLParser.FieldPathContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#fieldArray.
    def enterFieldArray(self, ctx:TransformDSLParser.FieldArrayContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#fieldArray.
    def exitFieldArray(self, ctx:TransformDSLParser.FieldArrayContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#fieldName.
    def enterFieldName(self, ctx:TransformDSLParser.FieldNameContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#fieldName.
    def exitFieldName(self, ctx:TransformDSLParser.FieldNameContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#duration.
    def enterDuration(self, ctx:TransformDSLParser.DurationContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#duration.
    def exitDuration(self, ctx:TransformDSLParser.DurationContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#timeUnit.
    def enterTimeUnit(self, ctx:TransformDSLParser.TimeUnitContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#timeUnit.
    def exitTimeUnit(self, ctx:TransformDSLParser.TimeUnitContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#literal.
    def enterLiteral(self, ctx:TransformDSLParser.LiteralContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#literal.
    def exitLiteral(self, ctx:TransformDSLParser.LiteralContext):
        pass


    # Enter a parse tree produced by TransformDSLParser#numberLiteral.
    def enterNumberLiteral(self, ctx:TransformDSLParser.NumberLiteralContext):
        pass

    # Exit a parse tree produced by TransformDSLParser#numberLiteral.
    def exitNumberLiteral(self, ctx:TransformDSLParser.NumberLiteralContext):
        pass



del TransformDSLParser