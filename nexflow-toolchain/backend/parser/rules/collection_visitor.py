# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Collection Expression Visitor Mixin for Rules Parser

Handles parsing of collection expressions in L4 Rules DSL.
RFC: Collection Operations Instead of Loops in L4
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesCollectionVisitorMixin:
    """Mixin for parsing collection expression visitor methods."""

    def visitCollectionExpr(self, ctx: RulesDSLParser.CollectionExprContext) -> ast.CollectionExpr:
        """Parse a collection expression."""
        if ctx.predicateFunction():
            # any(items, predicate), all(items, predicate), none(items, predicate)
            func_type = self._parse_predicate_function(ctx.predicateFunction())
            collection = self.visitValueExpr(ctx.valueExpr())
            predicate = self.visitCollectionPredicate(ctx.collectionPredicate())
            return ast.CollectionExpr(
                function_type=func_type,
                collection=collection,
                predicate=predicate,
                location=self._get_location(ctx)
            )
        elif ctx.aggregateFunction():
            # sum(items, field), count(items), avg(items, field), max(items, field), min(items, field)
            func_type = self._parse_aggregate_function(ctx.aggregateFunction())
            collection = self.visitValueExpr(ctx.valueExpr())
            field_extractor = None
            if ctx.fieldPath():
                field_extractor = self.visitFieldPath(ctx.fieldPath())
            return ast.CollectionExpr(
                function_type=func_type,
                collection=collection,
                field_extractor=field_extractor,
                location=self._get_location(ctx)
            )
        elif ctx.transformFunction():
            # filter(items, predicate), find(items, predicate), distinct(items)
            func_type = self._parse_transform_function(ctx.transformFunction())
            collection = self.visitValueExpr(ctx.valueExpr())
            predicate = None
            if ctx.collectionPredicate():
                predicate = self.visitCollectionPredicate(ctx.collectionPredicate())
            return ast.CollectionExpr(
                function_type=func_type,
                collection=collection,
                predicate=predicate,
                location=self._get_location(ctx)
            )
        else:
            raise ValueError(f"Unknown collection expression type at {ctx.getText()}")

    def _parse_predicate_function(self, ctx: RulesDSLParser.PredicateFunctionContext) -> ast.CollectionFunctionType:
        """Parse predicate function type."""
        if ctx.ANY():
            return ast.CollectionFunctionType.ANY
        elif ctx.ALL():
            return ast.CollectionFunctionType.ALL
        elif ctx.NONE():
            return ast.CollectionFunctionType.NONE
        else:
            raise ValueError(f"Unknown predicate function: {ctx.getText()}")

    def _parse_aggregate_function(self, ctx: RulesDSLParser.AggregateFunctionContext) -> ast.CollectionFunctionType:
        """Parse aggregate function type."""
        if ctx.SUM():
            return ast.CollectionFunctionType.SUM
        elif ctx.COUNT():
            return ast.CollectionFunctionType.COUNT
        elif ctx.AVG():
            return ast.CollectionFunctionType.AVG
        elif ctx.MAX_FN():
            return ast.CollectionFunctionType.MAX
        elif ctx.MIN_FN():
            return ast.CollectionFunctionType.MIN
        else:
            raise ValueError(f"Unknown aggregate function: {ctx.getText()}")

    def _parse_transform_function(self, ctx: RulesDSLParser.TransformFunctionContext) -> ast.CollectionFunctionType:
        """Parse transform function type."""
        if ctx.FILTER():
            return ast.CollectionFunctionType.FILTER
        elif ctx.FIND():
            return ast.CollectionFunctionType.FIND
        elif ctx.DISTINCT():
            return ast.CollectionFunctionType.DISTINCT
        else:
            raise ValueError(f"Unknown transform function: {ctx.getText()}")

    def visitCollectionPredicate(self, ctx: RulesDSLParser.CollectionPredicateContext) -> ast.CollectionPredicate:
        """Parse a collection predicate (lambda or inline condition)."""
        if ctx.lambdaExpression():
            return self.visitLambdaExpression(ctx.lambdaExpression())
        elif ctx.collectionPredicateOr():
            return self.visitCollectionPredicateOr(ctx.collectionPredicateOr())
        else:
            raise ValueError(f"Unknown collection predicate type at {ctx.getText()}")

    def visitCollectionPredicateOr(self, ctx: RulesDSLParser.CollectionPredicateOrContext) -> ast.CollectionPredicate:
        """Parse OR-connected predicate terms."""
        terms = [self.visitCollectionPredicateAnd(child) for child in ctx.collectionPredicateAnd()]

        if len(terms) == 1:
            return terms[0]

        operators = [ast.LogicalOp.OR] * (len(terms) - 1)
        return ast.CollectionPredicateCompound(
            predicates=terms,
            operators=operators,
            location=self._get_location(ctx)
        )

    def visitCollectionPredicateAnd(self, ctx: RulesDSLParser.CollectionPredicateAndContext) -> ast.CollectionPredicate:
        """Parse AND-connected predicate atoms."""
        atoms = [self.visitCollectionPredicateAtom(child) for child in ctx.collectionPredicateAtom()]

        if len(atoms) == 1:
            return atoms[0]

        operators = [ast.LogicalOp.AND] * (len(atoms) - 1)
        return ast.CollectionPredicateCompound(
            predicates=atoms,
            operators=operators,
            location=self._get_location(ctx)
        )

    def visitCollectionPredicateAtom(self, ctx: RulesDSLParser.CollectionPredicateAtomContext) -> ast.CollectionPredicateAtom:
        """Parse a single predicate atom."""
        # Check for NOT prefix
        if ctx.NOT() and ctx.collectionPredicateAtom():
            inner = self.visitCollectionPredicateAtom(ctx.collectionPredicateAtom())
            return ast.CollectionPredicateNot(
                predicate=inner,
                location=self._get_location(ctx)
            )

        # Check for parenthesized expression
        if ctx.collectionPredicateOr():
            return self.visitCollectionPredicateOr(ctx.collectionPredicateOr())

        # Get the field path
        field_path = self.visitFieldPath(ctx.fieldPath())

        # Check for null conditions
        if ctx.IS() and ctx.NULL():
            is_not_null = ctx.NOT() is not None
            return ast.CollectionPredicateNull(
                field=field_path,
                is_not_null=is_not_null,
                location=self._get_location(ctx)
            )

        # Check for IN conditions
        if ctx.IN():
            values = [self.visitValueExpr(v) for v in ctx.valueList().valueExpr()]
            negated = len([c for c in ctx.getChildren() if hasattr(c, 'getText') and c.getText() == 'not']) > 0
            return ast.CollectionPredicateIn(
                field=field_path,
                values=values,
                negated=negated,
                location=self._get_location(ctx)
            )

        # Default: comparison
        if ctx.comparisonOp() and ctx.valueExpr():
            operator = self._parse_comparison_op(ctx.comparisonOp())
            value = self.visitValueExpr(ctx.valueExpr())
            return ast.CollectionPredicateComparison(
                field=field_path,
                operator=operator,
                value=value,
                location=self._get_location(ctx)
            )

        raise ValueError(f"Unable to parse collection predicate atom: {ctx.getText()}")

    def visitLambdaExpressionForCollection(self, ctx: RulesDSLParser.LambdaExpressionContext) -> ast.CollectionPredicate:
        """Parse a lambda expression as a collection predicate."""
        if ctx.IDENTIFIER() and not ctx.LPAREN():
            # Single parameter: x -> expr
            param = ctx.IDENTIFIER().getText()
            body = self.visitValueExpr(ctx.valueExpr())
            return ast.LambdaPredicate(
                parameter=param,
                body=body,
                location=self._get_location(ctx)
            )
        else:
            # Multi-parameter: (x, y) -> expr
            params = [id.getText() for id in ctx.IDENTIFIER()]
            body = self.visitValueExpr(ctx.valueExpr())
            return ast.MultiParamLambdaPredicate(
                parameters=params,
                body=body,
                location=self._get_location(ctx)
            )
