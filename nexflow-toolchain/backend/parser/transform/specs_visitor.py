# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Input/Output Specification Visitor Mixin for Transform Parser

Handles parsing of input and output specifications and field declarations.
"""

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformSpecsVisitorMixin:
    """Mixin for input/output specification visitor methods."""

    def visitInputSpec(self, ctx: TransformDSLParser.InputSpecContext) -> ast.InputSpec:
        if ctx.fieldType() and not ctx.inputFieldDecl():
            single_type = self.visitFieldType(ctx.fieldType())
            qualifiers = []
            if ctx.qualifiers():
                qualifiers = self.visitQualifiers(ctx.qualifiers())
            return ast.InputSpec(
                single_type=single_type,
                single_qualifiers=qualifiers,
                location=self._get_location(ctx)
            )
        else:
            fields = []
            for field_ctx in ctx.inputFieldDecl():
                fields.append(self.visitInputFieldDecl(field_ctx))
            return ast.InputSpec(
                fields=fields,
                location=self._get_location(ctx)
            )

    def visitInputFieldDecl(self, ctx: TransformDSLParser.InputFieldDeclContext) -> ast.InputFieldDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())

        qualifiers = []
        if ctx.qualifiers():
            qualifiers = self.visitQualifiers(ctx.qualifiers())

        return ast.InputFieldDecl(
            name=name,
            field_type=field_type,
            qualifiers=qualifiers,
            location=self._get_location(ctx)
        )

    def visitOutputSpec(self, ctx: TransformDSLParser.OutputSpecContext) -> ast.OutputSpec:
        if ctx.fieldType() and not ctx.outputFieldDecl():
            single_type = self.visitFieldType(ctx.fieldType())
            qualifiers = []
            if ctx.qualifiers():
                qualifiers = self.visitQualifiers(ctx.qualifiers())
            return ast.OutputSpec(
                single_type=single_type,
                single_qualifiers=qualifiers,
                location=self._get_location(ctx)
            )
        else:
            fields = []
            for field_ctx in ctx.outputFieldDecl():
                fields.append(self.visitOutputFieldDecl(field_ctx))
            return ast.OutputSpec(
                fields=fields,
                location=self._get_location(ctx)
            )

    def visitOutputFieldDecl(self, ctx: TransformDSLParser.OutputFieldDeclContext) -> ast.OutputFieldDecl:
        name = self._get_text(ctx.fieldName())
        field_type = self.visitFieldType(ctx.fieldType())

        qualifiers = []
        if ctx.qualifiers():
            qualifiers = self.visitQualifiers(ctx.qualifiers())

        return ast.OutputFieldDecl(
            name=name,
            field_type=field_type,
            qualifiers=qualifiers,
            location=self._get_location(ctx)
        )
