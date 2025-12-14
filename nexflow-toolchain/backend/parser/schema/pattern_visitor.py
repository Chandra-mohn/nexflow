# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Pattern-Specific Block Visitor Mixin

Handles parsing of pattern-specific blocks: parameters (operational_parameters),
entries (reference_data), rules (business_logic), and migrations.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class PatternVisitorMixin:
    """Mixin for pattern-specific block visitor methods."""

    # =========================================================================
    # Parameters Block (operational_parameters pattern)
    # =========================================================================

    def visitParametersBlock(self, ctx: SchemaDSLParser.ParametersBlockContext) -> ast.ParametersBlock:
        parameters = []
        for param_ctx in ctx.parameterDecl():
            parameters.append(self.visitParameterDecl(param_ctx))
        return ast.ParametersBlock(
            parameters=parameters,
            location=self._get_location(ctx)
        )

    def visitParameterDecl(self, ctx: SchemaDSLParser.ParameterDeclContext) -> ast.ParameterDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())

        options = []
        for opt_ctx in ctx.parameterOption():
            options.append(self.visitParameterOption(opt_ctx))

        return ast.ParameterDecl(
            name=name,
            field_type=field_type,
            options=options,
            location=self._get_location(ctx)
        )

    def visitParameterOption(self, ctx: SchemaDSLParser.ParameterOptionContext) -> ast.ParameterOption:
        option = ast.ParameterOption(location=self._get_location(ctx))
        if ctx.literal():
            option.default_value = self.visitLiteral(ctx.literal())
        if ctx.rangeSpec():
            option.range_spec = self.visitRangeSpec(ctx.rangeSpec())
        return option

    # =========================================================================
    # Entries Block (reference_data pattern)
    # =========================================================================

    def visitEntriesBlock(self, ctx: SchemaDSLParser.EntriesBlockContext) -> ast.EntriesBlock:
        entries = []
        for entry_ctx in ctx.entryDecl():
            entries.append(self.visitEntryDecl(entry_ctx))
        return ast.EntriesBlock(
            entries=entries,
            location=self._get_location(ctx)
        )

    def visitEntryDecl(self, ctx: SchemaDSLParser.EntryDeclContext) -> ast.EntryDecl:
        key = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else ""

        fields = []
        for field_ctx in ctx.entryField():
            fields.append(self.visitEntryField(field_ctx))

        deprecated = False
        deprecated_reason = None
        if ctx.deprecatedClause():
            deprecated = True
            if ctx.deprecatedClause().STRING():
                deprecated_reason = self._strip_quotes(ctx.deprecatedClause().STRING().getText())

        return ast.EntryDecl(
            key=key,
            fields=fields,
            deprecated=deprecated,
            deprecated_reason=deprecated_reason,
            location=self._get_location(ctx)
        )

    def visitEntryField(self, ctx: SchemaDSLParser.EntryFieldContext) -> ast.EntryField:
        name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else ""
        value = self.visitLiteral(ctx.literal())
        return ast.EntryField(
            name=name,
            value=value,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Rule Block (business_logic pattern)
    # =========================================================================

    def visitRuleBlock(self, ctx: SchemaDSLParser.RuleBlockContext) -> ast.RuleBlock:
        name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else ""
        given = self.visitGivenBlock(ctx.givenBlock())

        calculate = None
        if ctx.calculateBlock():
            calculate = self.visitCalculateBlock(ctx.calculateBlock())

        return_block = self.visitReturnBlock(ctx.returnBlock())

        return ast.RuleBlock(
            name=name,
            given=given,
            calculate=calculate,
            return_block=return_block,
            location=self._get_location(ctx)
        )

    def visitGivenBlock(self, ctx: SchemaDSLParser.GivenBlockContext) -> ast.GivenBlock:
        fields = []
        for field_ctx in ctx.ruleFieldDecl():
            fields.append(self.visitRuleFieldDecl(field_ctx))
        return ast.GivenBlock(
            fields=fields,
            location=self._get_location(ctx)
        )

    def visitRuleFieldDecl(self, ctx: SchemaDSLParser.RuleFieldDeclContext) -> ast.RuleFieldDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())
        return ast.RuleFieldDecl(
            name=name,
            field_type=field_type,
            location=self._get_location(ctx)
        )

    def visitCalculateBlock(self, ctx: SchemaDSLParser.CalculateBlockContext) -> ast.CalculateBlock:
        calculations = []
        for calc_ctx in ctx.calculation():
            calculations.append(self.visitCalculation(calc_ctx))
        return ast.CalculateBlock(
            calculations=calculations,
            location=self._get_location(ctx)
        )

    def visitCalculation(self, ctx: SchemaDSLParser.CalculationContext) -> ast.Calculation:
        field_name = ctx.IDENTIFIER().getText() if ctx.IDENTIFIER() else ""
        expression = self.visitExpression(ctx.expression())
        return ast.Calculation(
            field_name=field_name,
            expression=expression,
            location=self._get_location(ctx)
        )

    def visitReturnBlock(self, ctx: SchemaDSLParser.ReturnBlockContext) -> ast.ReturnBlock:
        fields = []
        for field_ctx in ctx.ruleFieldDecl():
            fields.append(self.visitRuleFieldDecl(field_ctx))
        return ast.ReturnBlock(
            fields=fields,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Migration Block
    # =========================================================================

    def visitMigrationBlock(self, ctx: SchemaDSLParser.MigrationBlockContext) -> ast.MigrationBlock:
        statements = []
        for stmt_ctx in ctx.migrationStatement():
            statements.append(self.visitMigrationStatement(stmt_ctx))
        return ast.MigrationBlock(
            statements=statements,
            location=self._get_location(ctx)
        )

    def visitMigrationStatement(self, ctx: SchemaDSLParser.MigrationStatementContext) -> ast.MigrationStatement:
        if ctx.fieldPath():
            # Single field path - convert FieldPath to string
            field_path = self.visitFieldPath(ctx.fieldPath())
            # Convert FieldPath object to dot-separated string
            if hasattr(field_path, 'parts'):
                target_fields = ['.'.join(field_path.parts)]
            elif isinstance(field_path, str):
                target_fields = [field_path]
            else:
                target_fields = [str(field_path)]
        else:
            target_fields = self._get_field_list(ctx.fieldList())

        expression = self.visitExpression(ctx.expression())

        return ast.MigrationStatement(
            target_fields=target_fields if isinstance(target_fields, list) else [target_fields],
            expression=expression,
            location=self._get_location(ctx)
        )
