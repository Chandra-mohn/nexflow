"""
Type System Visitor Mixin for Transform Parser

Handles parsing of field types, constraints, qualifiers, and collection types.
"""

from typing import List

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformTypesVisitorMixin:
    """Mixin for type system visitor methods."""

    def visitFieldType(self, ctx: TransformDSLParser.FieldTypeContext) -> ast.FieldType:
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

    def visitBaseType(self, ctx: TransformDSLParser.BaseTypeContext) -> ast.BaseType:
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

    def visitCollectionType(self, ctx: TransformDSLParser.CollectionTypeContext) -> ast.CollectionType:
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

    def visitConstraint(self, ctx: TransformDSLParser.ConstraintContext) -> ast.Constraint:
        constraint = ast.Constraint(location=self._get_location(ctx))

        for spec_ctx in ctx.constraintSpec():
            if spec_ctx.rangeSpec():
                constraint.range_spec = self.visitRangeSpec(spec_ctx.rangeSpec())
            elif spec_ctx.lengthSpec():
                constraint.length_spec = self.visitLengthSpec(spec_ctx.lengthSpec())
            elif spec_ctx.STRING():
                constraint.pattern = self._strip_quotes(spec_ctx.STRING().getText())
            elif spec_ctx.valueList():
                constraint.values = self._get_value_list(spec_ctx.valueList())
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

    def visitRangeSpec(self, ctx: TransformDSLParser.RangeSpecContext) -> ast.RangeSpec:
        range_spec = ast.RangeSpec()
        numbers = ctx.numberLiteral()
        if len(numbers) >= 1:
            range_spec.min_value = self._parse_number(numbers[0])
        if len(numbers) >= 2:
            range_spec.max_value = self._parse_number(numbers[1])
        return range_spec

    def visitLengthSpec(self, ctx: TransformDSLParser.LengthSpecContext) -> ast.LengthSpec:
        length_spec = ast.LengthSpec()
        integers = ctx.INTEGER()
        if len(integers) >= 1:
            length_spec.min_length = int(integers[0].getText())
        if len(integers) >= 2:
            length_spec.max_length = int(integers[1].getText())
        return length_spec

    def visitQualifiers(self, ctx: TransformDSLParser.QualifiersContext) -> List[ast.Qualifier]:
        qualifiers = []
        for qual_ctx in ctx.qualifier():
            qualifiers.append(self.visitQualifier(qual_ctx))
        return qualifiers

    def visitQualifier(self, ctx: TransformDSLParser.QualifierContext) -> ast.Qualifier:
        qualifier_text = self._get_text(ctx).lower()

        if 'nullable' in qualifier_text:
            return ast.Qualifier(
                qualifier_type=ast.QualifierType.NULLABLE,
                location=self._get_location(ctx)
            )
        elif 'required' in qualifier_text:
            return ast.Qualifier(
                qualifier_type=ast.QualifierType.REQUIRED,
                location=self._get_location(ctx)
            )
        elif 'default' in qualifier_text:
            default_value = None
            if ctx.expression():
                default_value = self.visitExpression(ctx.expression())
            return ast.Qualifier(
                qualifier_type=ast.QualifierType.DEFAULT,
                default_value=default_value,
                location=self._get_location(ctx)
            )

        return ast.Qualifier(
            qualifier_type=ast.QualifierType.NULLABLE,
            location=self._get_location(ctx)
        )
