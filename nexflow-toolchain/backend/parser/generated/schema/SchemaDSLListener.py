# Generated from grammar/SchemaDSL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .SchemaDSLParser import SchemaDSLParser
else:
    from SchemaDSLParser import SchemaDSLParser

# This class defines a complete listener for a parse tree produced by SchemaDSLParser.
class SchemaDSLListener(ParseTreeListener):

    # Enter a parse tree produced by SchemaDSLParser#program.
    def enterProgram(self, ctx:SchemaDSLParser.ProgramContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#program.
    def exitProgram(self, ctx:SchemaDSLParser.ProgramContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#schemaDefinition.
    def enterSchemaDefinition(self, ctx:SchemaDSLParser.SchemaDefinitionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#schemaDefinition.
    def exitSchemaDefinition(self, ctx:SchemaDSLParser.SchemaDefinitionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#schemaName.
    def enterSchemaName(self, ctx:SchemaDSLParser.SchemaNameContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#schemaName.
    def exitSchemaName(self, ctx:SchemaDSLParser.SchemaNameContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#patternDecl.
    def enterPatternDecl(self, ctx:SchemaDSLParser.PatternDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#patternDecl.
    def exitPatternDecl(self, ctx:SchemaDSLParser.PatternDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#mutationPattern.
    def enterMutationPattern(self, ctx:SchemaDSLParser.MutationPatternContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#mutationPattern.
    def exitMutationPattern(self, ctx:SchemaDSLParser.MutationPatternContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#versionBlock.
    def enterVersionBlock(self, ctx:SchemaDSLParser.VersionBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#versionBlock.
    def exitVersionBlock(self, ctx:SchemaDSLParser.VersionBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#compatibilityDecl.
    def enterCompatibilityDecl(self, ctx:SchemaDSLParser.CompatibilityDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#compatibilityDecl.
    def exitCompatibilityDecl(self, ctx:SchemaDSLParser.CompatibilityDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#compatibilityMode.
    def enterCompatibilityMode(self, ctx:SchemaDSLParser.CompatibilityModeContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#compatibilityMode.
    def exitCompatibilityMode(self, ctx:SchemaDSLParser.CompatibilityModeContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#previousVersionDecl.
    def enterPreviousVersionDecl(self, ctx:SchemaDSLParser.PreviousVersionDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#previousVersionDecl.
    def exitPreviousVersionDecl(self, ctx:SchemaDSLParser.PreviousVersionDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#deprecationDecl.
    def enterDeprecationDecl(self, ctx:SchemaDSLParser.DeprecationDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#deprecationDecl.
    def exitDeprecationDecl(self, ctx:SchemaDSLParser.DeprecationDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#migrationGuideDecl.
    def enterMigrationGuideDecl(self, ctx:SchemaDSLParser.MigrationGuideDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#migrationGuideDecl.
    def exitMigrationGuideDecl(self, ctx:SchemaDSLParser.MigrationGuideDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#retentionDecl.
    def enterRetentionDecl(self, ctx:SchemaDSLParser.RetentionDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#retentionDecl.
    def exitRetentionDecl(self, ctx:SchemaDSLParser.RetentionDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#identityBlock.
    def enterIdentityBlock(self, ctx:SchemaDSLParser.IdentityBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#identityBlock.
    def exitIdentityBlock(self, ctx:SchemaDSLParser.IdentityBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#identityField.
    def enterIdentityField(self, ctx:SchemaDSLParser.IdentityFieldContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#identityField.
    def exitIdentityField(self, ctx:SchemaDSLParser.IdentityFieldContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#streamingBlock.
    def enterStreamingBlock(self, ctx:SchemaDSLParser.StreamingBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#streamingBlock.
    def exitStreamingBlock(self, ctx:SchemaDSLParser.StreamingBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#streamingDecl.
    def enterStreamingDecl(self, ctx:SchemaDSLParser.StreamingDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#streamingDecl.
    def exitStreamingDecl(self, ctx:SchemaDSLParser.StreamingDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#keyFieldsDecl.
    def enterKeyFieldsDecl(self, ctx:SchemaDSLParser.KeyFieldsDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#keyFieldsDecl.
    def exitKeyFieldsDecl(self, ctx:SchemaDSLParser.KeyFieldsDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#timeFieldDecl.
    def enterTimeFieldDecl(self, ctx:SchemaDSLParser.TimeFieldDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#timeFieldDecl.
    def exitTimeFieldDecl(self, ctx:SchemaDSLParser.TimeFieldDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#timeSemanticsDecl.
    def enterTimeSemanticsDecl(self, ctx:SchemaDSLParser.TimeSemanticsDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#timeSemanticsDecl.
    def exitTimeSemanticsDecl(self, ctx:SchemaDSLParser.TimeSemanticsDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#timeSemanticsType.
    def enterTimeSemanticsType(self, ctx:SchemaDSLParser.TimeSemanticsTypeContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#timeSemanticsType.
    def exitTimeSemanticsType(self, ctx:SchemaDSLParser.TimeSemanticsTypeContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#watermarkDecl.
    def enterWatermarkDecl(self, ctx:SchemaDSLParser.WatermarkDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#watermarkDecl.
    def exitWatermarkDecl(self, ctx:SchemaDSLParser.WatermarkDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#watermarkStrategy.
    def enterWatermarkStrategy(self, ctx:SchemaDSLParser.WatermarkStrategyContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#watermarkStrategy.
    def exitWatermarkStrategy(self, ctx:SchemaDSLParser.WatermarkStrategyContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#lateDataDecl.
    def enterLateDataDecl(self, ctx:SchemaDSLParser.LateDataDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#lateDataDecl.
    def exitLateDataDecl(self, ctx:SchemaDSLParser.LateDataDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#lateDataStrategy.
    def enterLateDataStrategy(self, ctx:SchemaDSLParser.LateDataStrategyContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#lateDataStrategy.
    def exitLateDataStrategy(self, ctx:SchemaDSLParser.LateDataStrategyContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#allowedLatenessDecl.
    def enterAllowedLatenessDecl(self, ctx:SchemaDSLParser.AllowedLatenessDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#allowedLatenessDecl.
    def exitAllowedLatenessDecl(self, ctx:SchemaDSLParser.AllowedLatenessDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#idleDecl.
    def enterIdleDecl(self, ctx:SchemaDSLParser.IdleDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#idleDecl.
    def exitIdleDecl(self, ctx:SchemaDSLParser.IdleDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#idleBehavior.
    def enterIdleBehavior(self, ctx:SchemaDSLParser.IdleBehaviorContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#idleBehavior.
    def exitIdleBehavior(self, ctx:SchemaDSLParser.IdleBehaviorContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#sparsityDecl.
    def enterSparsityDecl(self, ctx:SchemaDSLParser.SparsityDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#sparsityDecl.
    def exitSparsityDecl(self, ctx:SchemaDSLParser.SparsityDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#sparsityBlock.
    def enterSparsityBlock(self, ctx:SchemaDSLParser.SparsityBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#sparsityBlock.
    def exitSparsityBlock(self, ctx:SchemaDSLParser.SparsityBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#retentionBlockDecl.
    def enterRetentionBlockDecl(self, ctx:SchemaDSLParser.RetentionBlockDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#retentionBlockDecl.
    def exitRetentionBlockDecl(self, ctx:SchemaDSLParser.RetentionBlockDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#retentionOptions.
    def enterRetentionOptions(self, ctx:SchemaDSLParser.RetentionOptionsContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#retentionOptions.
    def exitRetentionOptions(self, ctx:SchemaDSLParser.RetentionOptionsContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#retentionPolicy.
    def enterRetentionPolicy(self, ctx:SchemaDSLParser.RetentionPolicyContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#retentionPolicy.
    def exitRetentionPolicy(self, ctx:SchemaDSLParser.RetentionPolicyContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldsBlock.
    def enterFieldsBlock(self, ctx:SchemaDSLParser.FieldsBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldsBlock.
    def exitFieldsBlock(self, ctx:SchemaDSLParser.FieldsBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldDecl.
    def enterFieldDecl(self, ctx:SchemaDSLParser.FieldDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldDecl.
    def exitFieldDecl(self, ctx:SchemaDSLParser.FieldDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldName.
    def enterFieldName(self, ctx:SchemaDSLParser.FieldNameContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldName.
    def exitFieldName(self, ctx:SchemaDSLParser.FieldNameContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#nestedObjectBlock.
    def enterNestedObjectBlock(self, ctx:SchemaDSLParser.NestedObjectBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#nestedObjectBlock.
    def exitNestedObjectBlock(self, ctx:SchemaDSLParser.NestedObjectBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#stateMachineBlock.
    def enterStateMachineBlock(self, ctx:SchemaDSLParser.StateMachineBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#stateMachineBlock.
    def exitStateMachineBlock(self, ctx:SchemaDSLParser.StateMachineBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#forEntityDecl.
    def enterForEntityDecl(self, ctx:SchemaDSLParser.ForEntityDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#forEntityDecl.
    def exitForEntityDecl(self, ctx:SchemaDSLParser.ForEntityDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#statesDecl.
    def enterStatesDecl(self, ctx:SchemaDSLParser.StatesDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#statesDecl.
    def exitStatesDecl(self, ctx:SchemaDSLParser.StatesDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#stateArray.
    def enterStateArray(self, ctx:SchemaDSLParser.StateArrayContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#stateArray.
    def exitStateArray(self, ctx:SchemaDSLParser.StateArrayContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#initialStateDecl.
    def enterInitialStateDecl(self, ctx:SchemaDSLParser.InitialStateDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#initialStateDecl.
    def exitInitialStateDecl(self, ctx:SchemaDSLParser.InitialStateDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#transitionsBlock.
    def enterTransitionsBlock(self, ctx:SchemaDSLParser.TransitionsBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#transitionsBlock.
    def exitTransitionsBlock(self, ctx:SchemaDSLParser.TransitionsBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#transitionDecl.
    def enterTransitionDecl(self, ctx:SchemaDSLParser.TransitionDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#transitionDecl.
    def exitTransitionDecl(self, ctx:SchemaDSLParser.TransitionDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#onTransitionBlock.
    def enterOnTransitionBlock(self, ctx:SchemaDSLParser.OnTransitionBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#onTransitionBlock.
    def exitOnTransitionBlock(self, ctx:SchemaDSLParser.OnTransitionBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#transitionAction.
    def enterTransitionAction(self, ctx:SchemaDSLParser.TransitionActionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#transitionAction.
    def exitTransitionAction(self, ctx:SchemaDSLParser.TransitionActionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#actionCall.
    def enterActionCall(self, ctx:SchemaDSLParser.ActionCallContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#actionCall.
    def exitActionCall(self, ctx:SchemaDSLParser.ActionCallContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#parametersBlock.
    def enterParametersBlock(self, ctx:SchemaDSLParser.ParametersBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#parametersBlock.
    def exitParametersBlock(self, ctx:SchemaDSLParser.ParametersBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#parameterDecl.
    def enterParameterDecl(self, ctx:SchemaDSLParser.ParameterDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#parameterDecl.
    def exitParameterDecl(self, ctx:SchemaDSLParser.ParameterDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#parameterOption.
    def enterParameterOption(self, ctx:SchemaDSLParser.ParameterOptionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#parameterOption.
    def exitParameterOption(self, ctx:SchemaDSLParser.ParameterOptionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#entriesBlock.
    def enterEntriesBlock(self, ctx:SchemaDSLParser.EntriesBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#entriesBlock.
    def exitEntriesBlock(self, ctx:SchemaDSLParser.EntriesBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#entryDecl.
    def enterEntryDecl(self, ctx:SchemaDSLParser.EntryDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#entryDecl.
    def exitEntryDecl(self, ctx:SchemaDSLParser.EntryDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#entryField.
    def enterEntryField(self, ctx:SchemaDSLParser.EntryFieldContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#entryField.
    def exitEntryField(self, ctx:SchemaDSLParser.EntryFieldContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#ruleBlock.
    def enterRuleBlock(self, ctx:SchemaDSLParser.RuleBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#ruleBlock.
    def exitRuleBlock(self, ctx:SchemaDSLParser.RuleBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#givenBlock.
    def enterGivenBlock(self, ctx:SchemaDSLParser.GivenBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#givenBlock.
    def exitGivenBlock(self, ctx:SchemaDSLParser.GivenBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#ruleFieldDecl.
    def enterRuleFieldDecl(self, ctx:SchemaDSLParser.RuleFieldDeclContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#ruleFieldDecl.
    def exitRuleFieldDecl(self, ctx:SchemaDSLParser.RuleFieldDeclContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#calculateBlock.
    def enterCalculateBlock(self, ctx:SchemaDSLParser.CalculateBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#calculateBlock.
    def exitCalculateBlock(self, ctx:SchemaDSLParser.CalculateBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#calculation.
    def enterCalculation(self, ctx:SchemaDSLParser.CalculationContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#calculation.
    def exitCalculation(self, ctx:SchemaDSLParser.CalculationContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#returnBlock.
    def enterReturnBlock(self, ctx:SchemaDSLParser.ReturnBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#returnBlock.
    def exitReturnBlock(self, ctx:SchemaDSLParser.ReturnBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#migrationBlock.
    def enterMigrationBlock(self, ctx:SchemaDSLParser.MigrationBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#migrationBlock.
    def exitMigrationBlock(self, ctx:SchemaDSLParser.MigrationBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#migrationStatement.
    def enterMigrationStatement(self, ctx:SchemaDSLParser.MigrationStatementContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#migrationStatement.
    def exitMigrationStatement(self, ctx:SchemaDSLParser.MigrationStatementContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#typeAliasBlock.
    def enterTypeAliasBlock(self, ctx:SchemaDSLParser.TypeAliasBlockContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#typeAliasBlock.
    def exitTypeAliasBlock(self, ctx:SchemaDSLParser.TypeAliasBlockContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#typeAlias.
    def enterTypeAlias(self, ctx:SchemaDSLParser.TypeAliasContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#typeAlias.
    def exitTypeAlias(self, ctx:SchemaDSLParser.TypeAliasContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#aliasName.
    def enterAliasName(self, ctx:SchemaDSLParser.AliasNameContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#aliasName.
    def exitAliasName(self, ctx:SchemaDSLParser.AliasNameContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldType.
    def enterFieldType(self, ctx:SchemaDSLParser.FieldTypeContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldType.
    def exitFieldType(self, ctx:SchemaDSLParser.FieldTypeContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#baseType.
    def enterBaseType(self, ctx:SchemaDSLParser.BaseTypeContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#baseType.
    def exitBaseType(self, ctx:SchemaDSLParser.BaseTypeContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#collectionType.
    def enterCollectionType(self, ctx:SchemaDSLParser.CollectionTypeContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#collectionType.
    def exitCollectionType(self, ctx:SchemaDSLParser.CollectionTypeContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#constraint.
    def enterConstraint(self, ctx:SchemaDSLParser.ConstraintContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#constraint.
    def exitConstraint(self, ctx:SchemaDSLParser.ConstraintContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#constraintSpec.
    def enterConstraintSpec(self, ctx:SchemaDSLParser.ConstraintSpecContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#constraintSpec.
    def exitConstraintSpec(self, ctx:SchemaDSLParser.ConstraintSpecContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#rangeSpec.
    def enterRangeSpec(self, ctx:SchemaDSLParser.RangeSpecContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#rangeSpec.
    def exitRangeSpec(self, ctx:SchemaDSLParser.RangeSpecContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#lengthSpec.
    def enterLengthSpec(self, ctx:SchemaDSLParser.LengthSpecContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#lengthSpec.
    def exitLengthSpec(self, ctx:SchemaDSLParser.LengthSpecContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#valueList.
    def enterValueList(self, ctx:SchemaDSLParser.ValueListContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#valueList.
    def exitValueList(self, ctx:SchemaDSLParser.ValueListContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldQualifier.
    def enterFieldQualifier(self, ctx:SchemaDSLParser.FieldQualifierContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldQualifier.
    def exitFieldQualifier(self, ctx:SchemaDSLParser.FieldQualifierContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#piiModifier.
    def enterPiiModifier(self, ctx:SchemaDSLParser.PiiModifierContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#piiModifier.
    def exitPiiModifier(self, ctx:SchemaDSLParser.PiiModifierContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#defaultClause.
    def enterDefaultClause(self, ctx:SchemaDSLParser.DefaultClauseContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#defaultClause.
    def exitDefaultClause(self, ctx:SchemaDSLParser.DefaultClauseContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#deprecatedClause.
    def enterDeprecatedClause(self, ctx:SchemaDSLParser.DeprecatedClauseContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#deprecatedClause.
    def exitDeprecatedClause(self, ctx:SchemaDSLParser.DeprecatedClauseContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#expression.
    def enterExpression(self, ctx:SchemaDSLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#expression.
    def exitExpression(self, ctx:SchemaDSLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#whenExpression.
    def enterWhenExpression(self, ctx:SchemaDSLParser.WhenExpressionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#whenExpression.
    def exitWhenExpression(self, ctx:SchemaDSLParser.WhenExpressionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#condition.
    def enterCondition(self, ctx:SchemaDSLParser.ConditionContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#condition.
    def exitCondition(self, ctx:SchemaDSLParser.ConditionContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#comparisonOp.
    def enterComparisonOp(self, ctx:SchemaDSLParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#comparisonOp.
    def exitComparisonOp(self, ctx:SchemaDSLParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#operator.
    def enterOperator(self, ctx:SchemaDSLParser.OperatorContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#operator.
    def exitOperator(self, ctx:SchemaDSLParser.OperatorContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#functionCall.
    def enterFunctionCall(self, ctx:SchemaDSLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#functionCall.
    def exitFunctionCall(self, ctx:SchemaDSLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldPath.
    def enterFieldPath(self, ctx:SchemaDSLParser.FieldPathContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldPath.
    def exitFieldPath(self, ctx:SchemaDSLParser.FieldPathContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldList.
    def enterFieldList(self, ctx:SchemaDSLParser.FieldListContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldList.
    def exitFieldList(self, ctx:SchemaDSLParser.FieldListContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#fieldArray.
    def enterFieldArray(self, ctx:SchemaDSLParser.FieldArrayContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#fieldArray.
    def exitFieldArray(self, ctx:SchemaDSLParser.FieldArrayContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#duration.
    def enterDuration(self, ctx:SchemaDSLParser.DurationContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#duration.
    def exitDuration(self, ctx:SchemaDSLParser.DurationContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#timeUnit.
    def enterTimeUnit(self, ctx:SchemaDSLParser.TimeUnitContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#timeUnit.
    def exitTimeUnit(self, ctx:SchemaDSLParser.TimeUnitContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#sizeSpec.
    def enterSizeSpec(self, ctx:SchemaDSLParser.SizeSpecContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#sizeSpec.
    def exitSizeSpec(self, ctx:SchemaDSLParser.SizeSpecContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#sizeUnit.
    def enterSizeUnit(self, ctx:SchemaDSLParser.SizeUnitContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#sizeUnit.
    def exitSizeUnit(self, ctx:SchemaDSLParser.SizeUnitContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#literal.
    def enterLiteral(self, ctx:SchemaDSLParser.LiteralContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#literal.
    def exitLiteral(self, ctx:SchemaDSLParser.LiteralContext):
        pass


    # Enter a parse tree produced by SchemaDSLParser#numberLiteral.
    def enterNumberLiteral(self, ctx:SchemaDSLParser.NumberLiteralContext):
        pass

    # Exit a parse tree produced by SchemaDSLParser#numberLiteral.
    def exitNumberLiteral(self, ctx:SchemaDSLParser.NumberLiteralContext):
        pass



del SchemaDSLParser