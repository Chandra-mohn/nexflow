"""
Core Visitor Mixin

Handles parsing of core schema elements: program, schema definition,
patterns, versions, identity blocks, fields blocks, and nested objects.
"""

from typing import List, Optional, Union

from backend.ast import schema_ast as ast
from backend.ast.common import ImportStatement
from backend.parser.base import SourceLocation
from backend.parser.generated.schema import SchemaDSLParser


class CoreVisitorMixin:
    """Mixin for core schema visitor methods."""

    def _get_location(self, ctx) -> Optional[SourceLocation]:
        """Extract source location from parser context."""
        if ctx is None:
            return None
        start = ctx.start if hasattr(ctx, 'start') else None
        stop = ctx.stop if hasattr(ctx, 'stop') else None
        if start:
            return SourceLocation(
                line=start.line,
                column=start.column,
                start_index=start.start if hasattr(start, 'start') else 0,
                stop_index=stop.stop if stop and hasattr(stop, 'stop') else 0
            )
        return None

    def _get_text(self, ctx) -> str:
        """Get text content from context."""
        return ctx.getText() if ctx else ""

    def _strip_quotes(self, text: str) -> str:
        """Strip quotes from string literal."""
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text

    def visitProgram(self, ctx: SchemaDSLParser.ProgramContext) -> ast.Program:
        schemas = []
        type_aliases = []
        imports = []

        for child in ctx.getChildren():
            if isinstance(child, SchemaDSLParser.SchemaDefinitionContext):
                schemas.append(self.visitSchemaDefinition(child))
            elif isinstance(child, SchemaDSLParser.TypeAliasBlockContext):
                type_aliases.append(self.visitTypeAliasBlock(child))
            elif isinstance(child, SchemaDSLParser.ImportStatementContext):
                imports.append(self.visitImportStatement(child))

        return ast.Program(
            schemas=schemas,
            type_aliases=type_aliases,
            imports=imports,
            location=self._get_location(ctx)
        )

    def visitImportStatement(self, ctx: SchemaDSLParser.ImportStatementContext) -> ImportStatement:
        """Parse an import statement."""
        path = ctx.importPath().getText()
        line = ctx.start.line if ctx.start else 0
        column = ctx.start.column if ctx.start else 0
        return ImportStatement(path=path, line=line, column=column)

    def visitImportPath(self, ctx: SchemaDSLParser.ImportPathContext) -> str:
        """Parse an import path."""
        return ctx.getText()

    def visitSchemaDefinition(self, ctx: SchemaDSLParser.SchemaDefinitionContext) -> ast.SchemaDefinition:
        # v0.5.0+: schemaName can be IDENTIFIER, mutationPattern, or timeSemanticsType
        name = self._get_text(ctx.schemaName())

        patterns = []
        if ctx.patternDecl():
            patterns = self.visitPatternDecl(ctx.patternDecl())

        version = None
        if ctx.versionBlock():
            version = self.visitVersionBlock(ctx.versionBlock())

        retention = None
        if ctx.retentionDecl():
            retention = self.visitRetentionDecl(ctx.retentionDecl())

        identity = None
        if ctx.identityBlock():
            identity = self.visitIdentityBlock(ctx.identityBlock())

        streaming = None
        if ctx.streamingBlock():
            streaming = self.visitStreamingBlock(ctx.streamingBlock())

        fields = None
        if ctx.fieldsBlock():
            fields = self.visitFieldsBlock(ctx.fieldsBlock())

        nested_objects = []
        for nested_ctx in ctx.nestedObjectBlock():
            nested_objects.append(self.visitNestedObjectBlock(nested_ctx))

        computed = None
        if ctx.computedBlock():
            computed = self.visitComputedBlock(ctx.computedBlock())

        state_machine = None
        if ctx.stateMachineBlock():
            state_machine = self.visitStateMachineBlock(ctx.stateMachineBlock())

        parameters = None
        if ctx.parametersBlock():
            parameters = self.visitParametersBlock(ctx.parametersBlock())

        entries = None
        if ctx.entriesBlock():
            entries = self.visitEntriesBlock(ctx.entriesBlock())

        rules = []
        for rule_ctx in ctx.ruleBlock():
            rules.append(self.visitRuleBlock(rule_ctx))

        # v0.5.0+: Handle standalone compatibilityDecl (evolution keyword)
        # Note: Version block may also have compatibilityDecl, handle both
        if ctx.compatibilityDecl() and version is None:
            # Standalone evolution/compatibility - no version block
            version = ast.VersionBlock(
                version="1.0.0",  # Default version when only compatibility is specified
                compatibility=self.visitCompatibilityDecl(ctx.compatibilityDecl()),
                location=self._get_location(ctx.compatibilityDecl())
            )

        # v0.5.0+: Handle constraintsBlock
        constraints = None
        if ctx.constraintsBlock():
            constraints = self.visitConstraintsBlock(ctx.constraintsBlock())

        # v0.5.0+: Handle immutableDecl
        immutable = None
        if ctx.immutableDecl():
            immutable = self.visitImmutableDecl(ctx.immutableDecl())

        migration = None
        if ctx.migrationBlock():
            migration = self.visitMigrationBlock(ctx.migrationBlock())

        return ast.SchemaDefinition(
            name=name,
            patterns=patterns,
            version=version,
            retention=retention,
            identity=identity,
            streaming=streaming,
            fields=fields,
            nested_objects=nested_objects,
            computed=computed,
            constraints=constraints,
            immutable=immutable,
            state_machine=state_machine,
            parameters=parameters,
            entries=entries,
            rules=rules,
            migration=migration,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Pattern Declaration
    # =========================================================================

    def visitPatternDecl(self, ctx: SchemaDSLParser.PatternDeclContext) -> List[ast.MutationPattern]:
        patterns = []
        for pattern_ctx in ctx.mutationPattern():
            patterns.append(self.visitMutationPattern(pattern_ctx))
        return patterns

    def visitMutationPattern(self, ctx: SchemaDSLParser.MutationPatternContext) -> ast.MutationPattern:
        pattern_text = self._get_text(ctx).lower()
        pattern_map = {
            'master_data': ast.MutationPattern.MASTER_DATA,
            'immutable_ledger': ast.MutationPattern.IMMUTABLE_LEDGER,
            'versioned_configuration': ast.MutationPattern.VERSIONED_CONFIGURATION,
            'operational_parameters': ast.MutationPattern.OPERATIONAL_PARAMETERS,
            'event_log': ast.MutationPattern.EVENT_LOG,
            'state_machine': ast.MutationPattern.STATE_MACHINE,
            'temporal_data': ast.MutationPattern.TEMPORAL_DATA,
            'reference_data': ast.MutationPattern.REFERENCE_DATA,
            'business_logic': ast.MutationPattern.BUSINESS_LOGIC,
            # v0.5.0+: Additional patterns
            'command': ast.MutationPattern.COMMAND,
            'response': ast.MutationPattern.RESPONSE,
            'aggregate': ast.MutationPattern.AGGREGATE,
            'document': ast.MutationPattern.DOCUMENT,
            'audit_event': ast.MutationPattern.AUDIT_EVENT,
        }
        return pattern_map.get(pattern_text, ast.MutationPattern.MASTER_DATA)

    # =========================================================================
    # Version Block
    # =========================================================================

    def visitVersionBlock(self, ctx: SchemaDSLParser.VersionBlockContext) -> ast.VersionBlock:
        version = ctx.VERSION_NUMBER().getText() if ctx.VERSION_NUMBER() else "1.0.0"

        compatibility = None
        if ctx.compatibilityDecl():
            compatibility = self.visitCompatibilityDecl(ctx.compatibilityDecl())

        previous_version = None
        if ctx.previousVersionDecl():
            previous_version = self.visitPreviousVersionDecl(ctx.previousVersionDecl())

        deprecation = None
        if ctx.deprecationDecl():
            deprecation = self.visitDeprecationDecl(ctx.deprecationDecl())

        migration_guide = None
        if ctx.migrationGuideDecl():
            migration_guide = self.visitMigrationGuideDecl(ctx.migrationGuideDecl())

        return ast.VersionBlock(
            version=version,
            compatibility=compatibility,
            previous_version=previous_version,
            deprecation=deprecation,
            migration_guide=migration_guide,
            location=self._get_location(ctx)
        )

    def visitCompatibilityDecl(self, ctx: SchemaDSLParser.CompatibilityDeclContext) -> ast.CompatibilityMode:
        mode_text = self._get_text(ctx.compatibilityMode()).lower()
        mode_map = {
            'backward': ast.CompatibilityMode.BACKWARD,
            'forward': ast.CompatibilityMode.FORWARD,
            'full': ast.CompatibilityMode.FULL,
            'none': ast.CompatibilityMode.NONE,
            # v0.5.0+: Additional compatibility modes (aliases)
            'backward_compatible': ast.CompatibilityMode.BACKWARD,
            'forward_compatible': ast.CompatibilityMode.FORWARD,
        }
        return mode_map.get(mode_text, ast.CompatibilityMode.BACKWARD)

    def visitPreviousVersionDecl(self, ctx: SchemaDSLParser.PreviousVersionDeclContext) -> str:
        return ctx.VERSION_NUMBER().getText() if ctx.VERSION_NUMBER() else None

    def visitDeprecationDecl(self, ctx: SchemaDSLParser.DeprecationDeclContext) -> ast.DeprecationDecl:
        message = self._strip_quotes(ctx.STRING().getText()) if ctx.STRING() else ""
        return ast.DeprecationDecl(message=message, location=self._get_location(ctx))

    def visitMigrationGuideDecl(self, ctx: SchemaDSLParser.MigrationGuideDeclContext) -> str:
        return self._strip_quotes(ctx.STRING().getText()) if ctx.STRING() else None

    def visitRetentionDecl(self, ctx: SchemaDSLParser.RetentionDeclContext) -> ast.Duration:
        return self.visitDuration(ctx.duration())

    # =========================================================================
    # Identity and Fields Blocks
    # =========================================================================

    def visitIdentityBlock(self, ctx: SchemaDSLParser.IdentityBlockContext) -> ast.IdentityBlock:
        fields = []
        for field_ctx in ctx.identityField():
            fields.append(self.visitIdentityField(field_ctx))
        return ast.IdentityBlock(fields=fields, location=self._get_location(ctx))

    def visitIdentityField(self, ctx: SchemaDSLParser.IdentityFieldContext) -> ast.FieldDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())

        qualifiers = []
        for qual_ctx in ctx.fieldQualifier():
            qualifiers.append(self.visitFieldQualifier(qual_ctx))

        return ast.FieldDecl(
            name=name,
            field_type=field_type,
            qualifiers=qualifiers,
            location=self._get_location(ctx)
        )

    def visitFieldsBlock(self, ctx: SchemaDSLParser.FieldsBlockContext) -> ast.FieldsBlock:
        fields = []
        for field_ctx in ctx.fieldDecl():
            fields.append(self.visitFieldDecl(field_ctx))
        return ast.FieldsBlock(fields=fields, location=self._get_location(ctx))

    def visitFieldDecl(self, ctx: SchemaDSLParser.FieldDeclContext) -> ast.FieldDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())

        qualifiers = []
        for qual_ctx in ctx.fieldQualifier():
            qualifiers.append(self.visitFieldQualifier(qual_ctx))

        return ast.FieldDecl(
            name=name,
            field_type=field_type,
            qualifiers=qualifiers,
            location=self._get_location(ctx)
        )

    def visitNestedObjectBlock(self, ctx: SchemaDSLParser.NestedObjectBlockContext) -> ast.NestedObjectBlock:
        name = self._get_text(ctx.fieldName())
        is_list = 'list' in self._get_text(ctx).lower()

        fields = []
        for field_ctx in ctx.fieldDecl():
            fields.append(self.visitFieldDecl(field_ctx))

        nested = []
        for nested_ctx in ctx.nestedObjectBlock():
            nested.append(self.visitNestedObjectBlock(nested_ctx))

        return ast.NestedObjectBlock(
            name=name,
            is_list=is_list,
            fields=fields,
            nested_objects=nested,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Constraints Block (v0.5.0+)
    # =========================================================================

    def visitConstraintsBlock(self, ctx: SchemaDSLParser.ConstraintsBlockContext) -> ast.ConstraintsBlock:
        """Visit constraints block for business rule validation."""
        constraints = []
        for constraint_ctx in ctx.constraintDecl():
            constraints.append(self.visitConstraintDecl(constraint_ctx))
        return ast.ConstraintsBlock(
            constraints=constraints,
            location=self._get_location(ctx)
        )

    def visitConstraintDecl(self, ctx: SchemaDSLParser.ConstraintDeclContext) -> ast.ConstraintDecl:
        """Visit constraint declaration: condition as "message"."""
        # Get the condition text (everything before 'as')
        condition_ctx = ctx.condition()
        condition = self._get_text(condition_ctx) if condition_ctx else ""

        # Get the message string
        message = ""
        if ctx.STRING():
            message = self._strip_quotes(ctx.STRING().getText())

        return ast.ConstraintDecl(
            condition=condition,
            message=message,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Immutable Declaration (v0.5.0+)
    # =========================================================================

    def visitImmutableDecl(self, ctx: SchemaDSLParser.ImmutableDeclContext) -> bool:
        """Visit immutable declaration: immutable true/false."""
        if ctx.BOOLEAN():
            return ctx.BOOLEAN().getText().lower() == 'true'
        return False

    # =========================================================================
    # Computed Block (Derived Fields)
    # =========================================================================

    def visitComputedBlock(self, ctx: SchemaDSLParser.ComputedBlockContext) -> ast.ComputedBlock:
        """Visit computed block containing derived field definitions."""
        fields = []
        for field_ctx in ctx.computedField():
            fields.append(self.visitComputedField(field_ctx))
        return ast.ComputedBlock(
            fields=fields,
            location=self._get_location(ctx)
        )

    def visitComputedField(self, ctx: SchemaDSLParser.ComputedFieldContext) -> ast.ComputedFieldDecl:
        """Visit computed field: field_name = expression."""
        name = self._get_text(ctx.fieldName())
        expression = self.visitComputedExpression(ctx.computedExpression())
        return ast.ComputedFieldDecl(
            name=name,
            expression=expression,
            location=self._get_location(ctx)
        )

    def visitComputedExpression(self, ctx: SchemaDSLParser.ComputedExpressionContext) -> ast.ComputedExpression:
        """Visit computed expression - handles all expression types."""
        # Handle when/then/else expression
        if ctx.computedWhenExpression():
            return self.visitComputedWhenExpression(ctx.computedWhenExpression())

        # Handle parenthesized expression
        if ctx.getChildCount() >= 3:
            first_child = ctx.getChild(0)
            if hasattr(first_child, 'getText') and first_child.getText() == '(':
                # Parenthesized: ( expression )
                return self.visitComputedExpression(ctx.computedExpression(0))

        # Handle unary NOT expression
        if ctx.getChildCount() >= 2:
            first_child = ctx.getChild(0)
            if hasattr(first_child, 'getText') and first_child.getText() == 'not':
                operand = self.visitComputedExpression(ctx.computedExpression(0))
                return ast.UnaryExpression(
                    operator='not',
                    operand=operand,
                    location=self._get_location(ctx)
                )

        # Handle binary expressions (arithmetic, logical, comparison)
        if ctx.getChildCount() == 3 and len(ctx.computedExpression()) == 2:
            left = self.visitComputedExpression(ctx.computedExpression(0))
            right = self.visitComputedExpression(ctx.computedExpression(1))

            # Determine operator
            operator_ctx = ctx.getChild(1)
            operator = operator_ctx.getText() if hasattr(operator_ctx, 'getText') else str(operator_ctx)

            # Handle comparison operators from comparisonOp rule
            if ctx.comparisonOp():
                operator = self._get_text(ctx.comparisonOp())

            return ast.BinaryExpression(
                left=left,
                operator=operator,
                right=right,
                location=self._get_location(ctx)
            )

        # Handle function call
        if ctx.functionCall():
            return self.visitComputedFunctionCall(ctx.functionCall())

        # Handle field path reference
        if ctx.fieldPath():
            field_path = self.visitFieldPath(ctx.fieldPath())
            return ast.FieldRefExpression(
                field_path=field_path,
                location=self._get_location(ctx)
            )

        # Handle literal
        if ctx.literal():
            literal = self.visitLiteral(ctx.literal())
            return ast.LiteralExpression(
                value=literal,
                location=self._get_location(ctx)
            )

        # Fallback: treat as field reference
        return ast.FieldRefExpression(
            field_path=ast.FieldPath(parts=[self._get_text(ctx)]),
            location=self._get_location(ctx)
        )

    def visitComputedWhenExpression(self, ctx: SchemaDSLParser.ComputedWhenExpressionContext) -> ast.WhenExpression:
        """Visit when/then/else expression."""
        branches = []
        expressions = ctx.computedExpression()

        # Process when/then pairs
        # Grammar: 'when' expr 'then' expr ('when' expr 'then' expr)* 'else' expr
        # Expressions are: condition1, result1, condition2, result2, ..., else_result
        num_branches = (len(expressions) - 1) // 2

        for i in range(num_branches):
            condition = self.visitComputedExpression(expressions[i * 2])
            result = self.visitComputedExpression(expressions[i * 2 + 1])
            branches.append(ast.WhenBranch(
                condition=condition,
                result=result,
                location=self._get_location(ctx)
            ))

        # Last expression is the else result
        else_result = self.visitComputedExpression(expressions[-1])

        return ast.WhenExpression(
            branches=branches,
            else_result=else_result,
            location=self._get_location(ctx)
        )

    def visitComputedFunctionCall(self, ctx: SchemaDSLParser.FunctionCallContext) -> ast.FunctionCallExpression:
        """Visit function call in computed expression."""
        function_name = ctx.IDENTIFIER().getText()
        arguments = []

        # Visit each argument expression
        for expr_ctx in ctx.expression():
            # Convert regular expression to computed expression
            # This is a simplified conversion - for full support we'd need
            # to handle all expression types
            arg = self._expression_to_computed(expr_ctx)
            arguments.append(arg)

        return ast.FunctionCallExpression(
            function_name=function_name,
            arguments=arguments,
            location=self._get_location(ctx)
        )

    def _expression_to_computed(self, expr_ctx) -> ast.ComputedExpression:
        """Convert a regular expression context to a ComputedExpression.

        This handles the existing expression grammar used in function calls.
        """
        # Handle literal
        if hasattr(expr_ctx, 'literal') and expr_ctx.literal():
            literal = self.visitLiteral(expr_ctx.literal())
            return ast.LiteralExpression(value=literal)

        # Handle field path
        if hasattr(expr_ctx, 'fieldPath') and expr_ctx.fieldPath():
            field_path = self.visitFieldPath(expr_ctx.fieldPath())
            return ast.FieldRefExpression(field_path=field_path)

        # Handle nested function call
        if hasattr(expr_ctx, 'functionCall') and expr_ctx.functionCall():
            return self.visitComputedFunctionCall(expr_ctx.functionCall())

        # Handle binary expression
        if hasattr(expr_ctx, 'expression') and len(expr_ctx.expression()) == 2:
            left = self._expression_to_computed(expr_ctx.expression(0))
            right = self._expression_to_computed(expr_ctx.expression(1))
            operator = expr_ctx.operator().getText() if expr_ctx.operator() else '+'
            return ast.BinaryExpression(left=left, operator=operator, right=right)

        # Fallback
        return ast.FieldRefExpression(
            field_path=ast.FieldPath(parts=[self._get_text(expr_ctx)])
        )
