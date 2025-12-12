# Generated from grammar/SchemaDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SchemaDSLParser import SchemaDSLParser
else:
    from SchemaDSLParser import SchemaDSLParser

# This class defines a complete generic visitor for a parse tree produced by SchemaDSLParser.

class SchemaDSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SchemaDSLParser#program.
    def visitProgram(self, ctx:SchemaDSLParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#schemaDefinition.
    def visitSchemaDefinition(self, ctx:SchemaDSLParser.SchemaDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#schemaName.
    def visitSchemaName(self, ctx:SchemaDSLParser.SchemaNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#patternDecl.
    def visitPatternDecl(self, ctx:SchemaDSLParser.PatternDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#mutationPattern.
    def visitMutationPattern(self, ctx:SchemaDSLParser.MutationPatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#versionBlock.
    def visitVersionBlock(self, ctx:SchemaDSLParser.VersionBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#compatibilityDecl.
    def visitCompatibilityDecl(self, ctx:SchemaDSLParser.CompatibilityDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#compatibilityMode.
    def visitCompatibilityMode(self, ctx:SchemaDSLParser.CompatibilityModeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#previousVersionDecl.
    def visitPreviousVersionDecl(self, ctx:SchemaDSLParser.PreviousVersionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#deprecationDecl.
    def visitDeprecationDecl(self, ctx:SchemaDSLParser.DeprecationDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#migrationGuideDecl.
    def visitMigrationGuideDecl(self, ctx:SchemaDSLParser.MigrationGuideDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#retentionDecl.
    def visitRetentionDecl(self, ctx:SchemaDSLParser.RetentionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#immutableDecl.
    def visitImmutableDecl(self, ctx:SchemaDSLParser.ImmutableDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#constraintsBlock.
    def visitConstraintsBlock(self, ctx:SchemaDSLParser.ConstraintsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#constraintDecl.
    def visitConstraintDecl(self, ctx:SchemaDSLParser.ConstraintDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#identityBlock.
    def visitIdentityBlock(self, ctx:SchemaDSLParser.IdentityBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#identityField.
    def visitIdentityField(self, ctx:SchemaDSLParser.IdentityFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#streamingBlock.
    def visitStreamingBlock(self, ctx:SchemaDSLParser.StreamingBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#streamingDecl.
    def visitStreamingDecl(self, ctx:SchemaDSLParser.StreamingDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#keyFieldsDecl.
    def visitKeyFieldsDecl(self, ctx:SchemaDSLParser.KeyFieldsDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#timeFieldDecl.
    def visitTimeFieldDecl(self, ctx:SchemaDSLParser.TimeFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#timeSemanticsDecl.
    def visitTimeSemanticsDecl(self, ctx:SchemaDSLParser.TimeSemanticsDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#timeSemanticsType.
    def visitTimeSemanticsType(self, ctx:SchemaDSLParser.TimeSemanticsTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#watermarkDecl.
    def visitWatermarkDecl(self, ctx:SchemaDSLParser.WatermarkDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#watermarkStrategy.
    def visitWatermarkStrategy(self, ctx:SchemaDSLParser.WatermarkStrategyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#lateDataDecl.
    def visitLateDataDecl(self, ctx:SchemaDSLParser.LateDataDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#lateDataStrategy.
    def visitLateDataStrategy(self, ctx:SchemaDSLParser.LateDataStrategyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#allowedLatenessDecl.
    def visitAllowedLatenessDecl(self, ctx:SchemaDSLParser.AllowedLatenessDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#idleDecl.
    def visitIdleDecl(self, ctx:SchemaDSLParser.IdleDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#idleBehavior.
    def visitIdleBehavior(self, ctx:SchemaDSLParser.IdleBehaviorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#sparsityDecl.
    def visitSparsityDecl(self, ctx:SchemaDSLParser.SparsityDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#sparsityBlock.
    def visitSparsityBlock(self, ctx:SchemaDSLParser.SparsityBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#retentionBlockDecl.
    def visitRetentionBlockDecl(self, ctx:SchemaDSLParser.RetentionBlockDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#retentionOptions.
    def visitRetentionOptions(self, ctx:SchemaDSLParser.RetentionOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#retentionPolicy.
    def visitRetentionPolicy(self, ctx:SchemaDSLParser.RetentionPolicyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldsBlock.
    def visitFieldsBlock(self, ctx:SchemaDSLParser.FieldsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldDecl.
    def visitFieldDecl(self, ctx:SchemaDSLParser.FieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldName.
    def visitFieldName(self, ctx:SchemaDSLParser.FieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#nestedObjectBlock.
    def visitNestedObjectBlock(self, ctx:SchemaDSLParser.NestedObjectBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#computedBlock.
    def visitComputedBlock(self, ctx:SchemaDSLParser.ComputedBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#computedField.
    def visitComputedField(self, ctx:SchemaDSLParser.ComputedFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#computedExpression.
    def visitComputedExpression(self, ctx:SchemaDSLParser.ComputedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#computedWhenExpression.
    def visitComputedWhenExpression(self, ctx:SchemaDSLParser.ComputedWhenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#stateMachineBlock.
    def visitStateMachineBlock(self, ctx:SchemaDSLParser.StateMachineBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#initialStateDecl.
    def visitInitialStateDecl(self, ctx:SchemaDSLParser.InitialStateDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#forEntityDecl.
    def visitForEntityDecl(self, ctx:SchemaDSLParser.ForEntityDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#statesBlock.
    def visitStatesBlock(self, ctx:SchemaDSLParser.StatesBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#statesDecl.
    def visitStatesDecl(self, ctx:SchemaDSLParser.StatesDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#stateDefList.
    def visitStateDefList(self, ctx:SchemaDSLParser.StateDefListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#stateDef.
    def visitStateDef(self, ctx:SchemaDSLParser.StateDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#stateQualifier.
    def visitStateQualifier(self, ctx:SchemaDSLParser.StateQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#stateArray.
    def visitStateArray(self, ctx:SchemaDSLParser.StateArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#transitionsBlock.
    def visitTransitionsBlock(self, ctx:SchemaDSLParser.TransitionsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#transitionDecl.
    def visitTransitionDecl(self, ctx:SchemaDSLParser.TransitionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#transitionArrowDecl.
    def visitTransitionArrowDecl(self, ctx:SchemaDSLParser.TransitionArrowDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#onTransitionBlock.
    def visitOnTransitionBlock(self, ctx:SchemaDSLParser.OnTransitionBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#transitionAction.
    def visitTransitionAction(self, ctx:SchemaDSLParser.TransitionActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#actionCall.
    def visitActionCall(self, ctx:SchemaDSLParser.ActionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#parametersBlock.
    def visitParametersBlock(self, ctx:SchemaDSLParser.ParametersBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#parameterDecl.
    def visitParameterDecl(self, ctx:SchemaDSLParser.ParameterDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#parameterOption.
    def visitParameterOption(self, ctx:SchemaDSLParser.ParameterOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#entriesBlock.
    def visitEntriesBlock(self, ctx:SchemaDSLParser.EntriesBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#entryDecl.
    def visitEntryDecl(self, ctx:SchemaDSLParser.EntryDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#entryField.
    def visitEntryField(self, ctx:SchemaDSLParser.EntryFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#ruleBlock.
    def visitRuleBlock(self, ctx:SchemaDSLParser.RuleBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#givenBlock.
    def visitGivenBlock(self, ctx:SchemaDSLParser.GivenBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#ruleFieldDecl.
    def visitRuleFieldDecl(self, ctx:SchemaDSLParser.RuleFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#calculateBlock.
    def visitCalculateBlock(self, ctx:SchemaDSLParser.CalculateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#calculation.
    def visitCalculation(self, ctx:SchemaDSLParser.CalculationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#returnBlock.
    def visitReturnBlock(self, ctx:SchemaDSLParser.ReturnBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#migrationBlock.
    def visitMigrationBlock(self, ctx:SchemaDSLParser.MigrationBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#migrationStatement.
    def visitMigrationStatement(self, ctx:SchemaDSLParser.MigrationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#typeAliasBlock.
    def visitTypeAliasBlock(self, ctx:SchemaDSLParser.TypeAliasBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#typeAlias.
    def visitTypeAlias(self, ctx:SchemaDSLParser.TypeAliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#aliasName.
    def visitAliasName(self, ctx:SchemaDSLParser.AliasNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldType.
    def visitFieldType(self, ctx:SchemaDSLParser.FieldTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#inlineObjectType.
    def visitInlineObjectType(self, ctx:SchemaDSLParser.InlineObjectTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#inlineFieldDecl.
    def visitInlineFieldDecl(self, ctx:SchemaDSLParser.InlineFieldDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#baseType.
    def visitBaseType(self, ctx:SchemaDSLParser.BaseTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#collectionType.
    def visitCollectionType(self, ctx:SchemaDSLParser.CollectionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#constraint.
    def visitConstraint(self, ctx:SchemaDSLParser.ConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#constraintSpec.
    def visitConstraintSpec(self, ctx:SchemaDSLParser.ConstraintSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#rangeSpec.
    def visitRangeSpec(self, ctx:SchemaDSLParser.RangeSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#lengthSpec.
    def visitLengthSpec(self, ctx:SchemaDSLParser.LengthSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#valueList.
    def visitValueList(self, ctx:SchemaDSLParser.ValueListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldQualifier.
    def visitFieldQualifier(self, ctx:SchemaDSLParser.FieldQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#piiModifier.
    def visitPiiModifier(self, ctx:SchemaDSLParser.PiiModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#defaultClause.
    def visitDefaultClause(self, ctx:SchemaDSLParser.DefaultClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#deprecatedClause.
    def visitDeprecatedClause(self, ctx:SchemaDSLParser.DeprecatedClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#expression.
    def visitExpression(self, ctx:SchemaDSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#whenExpression.
    def visitWhenExpression(self, ctx:SchemaDSLParser.WhenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#condition.
    def visitCondition(self, ctx:SchemaDSLParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#comparisonOp.
    def visitComparisonOp(self, ctx:SchemaDSLParser.ComparisonOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#operator.
    def visitOperator(self, ctx:SchemaDSLParser.OperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#functionCall.
    def visitFunctionCall(self, ctx:SchemaDSLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldPath.
    def visitFieldPath(self, ctx:SchemaDSLParser.FieldPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldList.
    def visitFieldList(self, ctx:SchemaDSLParser.FieldListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#fieldArray.
    def visitFieldArray(self, ctx:SchemaDSLParser.FieldArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#duration.
    def visitDuration(self, ctx:SchemaDSLParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#timeUnit.
    def visitTimeUnit(self, ctx:SchemaDSLParser.TimeUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#sizeSpec.
    def visitSizeSpec(self, ctx:SchemaDSLParser.SizeSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#sizeUnit.
    def visitSizeUnit(self, ctx:SchemaDSLParser.SizeUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#literal.
    def visitLiteral(self, ctx:SchemaDSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SchemaDSLParser#numberLiteral.
    def visitNumberLiteral(self, ctx:SchemaDSLParser.NumberLiteralContext):
        return self.visitChildren(ctx)



del SchemaDSLParser