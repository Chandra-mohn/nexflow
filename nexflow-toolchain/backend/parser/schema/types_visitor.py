"""
Type System Visitor Mixin

Handles parsing of field types, collection types, constraints, qualifiers,
and the type alias blocks.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.parser.generated.schema import SchemaDSLParser


class TypesVisitorMixin:
    """Mixin for type system visitor methods."""

    def visitFieldType(self, ctx: SchemaDSLParser.FieldTypeContext) -> ast.FieldType:
        base_type = None
        collection_type = None
        custom_type = None
        constraints = []

        if ctx.baseType():
            base_type = self.visitBaseType(ctx.baseType())
        elif ctx.collectionType():
            collection_type = self.visitCollectionType(ctx.collectionType())
        elif ctx.IDENTIFIER():
            custom_type = ctx.IDENTIFIER().getText()

        for constraint_ctx in ctx.constraint():
            constraints.append(self.visitConstraint(constraint_ctx))

        return ast.FieldType(
            base_type=base_type,
            collection_type=collection_type,
            custom_type=custom_type,
            constraints=constraints,
            location=self._get_location(ctx)
        )

    def visitBaseType(self, ctx: SchemaDSLParser.BaseTypeContext) -> ast.BaseType:
        type_text = self._get_text(ctx).lower()
        type_map = {
            'string': ast.BaseType.STRING,
            'integer': ast.BaseType.INTEGER,
            'decimal': ast.BaseType.DECIMAL,
            'boolean': ast.BaseType.BOOLEAN,
            'date': ast.BaseType.DATE,
            'timestamp': ast.BaseType.TIMESTAMP,
            'uuid': ast.BaseType.UUID,
            'bytes': ast.BaseType.BYTES,
        }
        return type_map.get(type_text, ast.BaseType.STRING)

    def visitCollectionType(self, ctx: SchemaDSLParser.CollectionTypeContext) -> ast.CollectionType:
        collection_text = self._get_text(ctx).lower()

        if 'list' in collection_text:
            kind = 'list'
        elif 'set' in collection_text:
            kind = 'set'
        elif 'map' in collection_text:
            kind = 'map'
        else:
            kind = 'list'

        element_type = None
        key_type = None
        if ctx.fieldType():
            field_types = ctx.fieldType()
            if isinstance(field_types, list):
                if len(field_types) >= 1:
                    element_type = self.visitFieldType(field_types[0])
                if len(field_types) >= 2:
                    key_type = self.visitFieldType(field_types[1])
            else:
                element_type = self.visitFieldType(field_types)

        return ast.CollectionType(
            collection_kind=kind,
            element_type=element_type,
            key_type=key_type,
            location=self._get_location(ctx)
        )

    def visitConstraint(self, ctx: SchemaDSLParser.ConstraintContext) -> ast.Constraint:
        constraint = ast.Constraint(location=self._get_location(ctx))

        for spec_ctx in ctx.constraintSpec():
            if spec_ctx.rangeSpec():
                constraint.range_spec = self.visitRangeSpec(spec_ctx.rangeSpec())
            elif spec_ctx.lengthSpec():
                constraint.length_spec = self.visitLengthSpec(spec_ctx.lengthSpec())
            elif spec_ctx.STRING():
                constraint.pattern = self._strip_quotes(spec_ctx.STRING().getText())
            elif spec_ctx.valueList():
                constraint.values = self.visitValueList(spec_ctx.valueList())
            elif spec_ctx.INTEGER():
                integers = spec_ctx.INTEGER()
                spec_text = self._get_text(spec_ctx)
                if 'precision' in spec_text:
                    constraint.precision = int(integers[0].getText())
                    if len(integers) > 1:
                        constraint.scale = int(integers[1].getText())
                elif 'scale' in spec_text:
                    constraint.scale = int(integers[0].getText())

        return constraint

    def visitRangeSpec(self, ctx: SchemaDSLParser.RangeSpecContext) -> ast.RangeSpec:
        range_spec = ast.RangeSpec()
        numbers = ctx.numberLiteral()
        if len(numbers) >= 1:
            range_spec.min_value = self._parse_number(numbers[0])
        if len(numbers) >= 2:
            range_spec.max_value = self._parse_number(numbers[1])
        return range_spec

    def visitLengthSpec(self, ctx: SchemaDSLParser.LengthSpecContext) -> ast.LengthSpec:
        length_spec = ast.LengthSpec()
        integers = ctx.INTEGER()
        if len(integers) >= 1:
            length_spec.min_length = int(integers[0].getText())
        if len(integers) >= 2:
            length_spec.max_length = int(integers[1].getText())
        return length_spec

    def visitValueList(self, ctx: SchemaDSLParser.ValueListContext) -> List[str]:
        values = []
        if ctx.IDENTIFIER():
            for ident in ctx.IDENTIFIER():
                values.append(ident.getText())
        elif ctx.STRING():
            for string in ctx.STRING():
                values.append(self._strip_quotes(string.getText()))
        return values

    def visitFieldQualifier(self, ctx: SchemaDSLParser.FieldQualifierContext) -> ast.FieldQualifier:
        qualifier_text = self._get_text(ctx).lower()

        # Handle default clause
        if ctx.defaultClause():
            default_value = self.visitLiteral(ctx.defaultClause().literal())
            return ast.FieldQualifier(
                qualifier_type=ast.FieldQualifierType.DEFAULT,
                default_value=default_value,
                location=self._get_location(ctx)
            )

        # Handle pii modifier with optional profile
        if ctx.piiModifier():
            pii_ctx = ctx.piiModifier()
            pii_profile = None
            if pii_ctx.IDENTIFIER():
                pii_profile = pii_ctx.IDENTIFIER().getText()
            return ast.FieldQualifier(
                qualifier_type=ast.FieldQualifierType.PII,
                pii_profile=pii_profile,
                location=self._get_location(ctx)
            )

        qualifier_map = {
            'required': ast.FieldQualifierType.REQUIRED,
            'optional': ast.FieldQualifierType.OPTIONAL,
            'encrypted': ast.FieldQualifierType.ENCRYPTED,
            'indexed': ast.FieldQualifierType.INDEXED,
            'sensitive': ast.FieldQualifierType.SENSITIVE,
        }

        for key, value in qualifier_map.items():
            if key in qualifier_text:
                return ast.FieldQualifier(
                    qualifier_type=value,
                    location=self._get_location(ctx)
                )

        return ast.FieldQualifier(
            qualifier_type=ast.FieldQualifierType.OPTIONAL,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Type Alias Block
    # =========================================================================

    def visitTypeAliasBlock(self, ctx: SchemaDSLParser.TypeAliasBlockContext) -> ast.TypeAliasBlock:
        aliases = []
        for alias_ctx in ctx.typeAlias():
            aliases.append(self.visitTypeAlias(alias_ctx))
        return ast.TypeAliasBlock(
            aliases=aliases,
            location=self._get_location(ctx)
        )

    def visitTypeAlias(self, ctx: SchemaDSLParser.TypeAliasContext) -> ast.TypeAlias:
        name = ctx.aliasName().getText()
        field_type = self.visitFieldType(ctx.fieldType()) if ctx.fieldType() else None

        constraints = []
        for constraint_ctx in ctx.constraint():
            constraints.append(self.visitConstraint(constraint_ctx))

        # Handle object type alias
        fields = []
        for field_ctx in ctx.fieldDecl():
            fields.append(self.visitFieldDecl(field_ctx))

        return ast.TypeAlias(
            name=name,
            field_type=field_type,
            constraints=constraints,
            fields=fields,
            location=self._get_location(ctx)
        )
