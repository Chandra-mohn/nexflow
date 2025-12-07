"""
Expression Visitor Mixin for Rules Parser

Handles parsing of boolean expressions, comparisons, value expressions, and terms.
"""

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesExpressionVisitorMixin:
    """Mixin for expression visitor methods."""

    def visitBooleanExpr(self, ctx: RulesDSLParser.BooleanExprContext) -> ast.BooleanExpr:
        terms = []
        operators = []

        for term_ctx in ctx.booleanTerm():
            terms.append(self.visitBooleanTerm(term_ctx))

        for i, child in enumerate(ctx.getChildren()):
            text = self._get_text(child).lower()
            if text == 'and':
                operators.append(ast.LogicalOp.AND)
            elif text == 'or':
                operators.append(ast.LogicalOp.OR)

        return ast.BooleanExpr(
            terms=terms,
            operators=operators,
            location=self._get_location(ctx)
        )

    def visitBooleanTerm(self, ctx: RulesDSLParser.BooleanTermContext) -> ast.BooleanTerm:
        negated = ctx.NOT() is not None
        factor = self.visitBooleanFactor(ctx.booleanFactor())
        return ast.BooleanTerm(
            factor=factor,
            negated=negated,
            location=self._get_location(ctx)
        )

    def visitBooleanFactor(self, ctx: RulesDSLParser.BooleanFactorContext) -> ast.BooleanFactor:
        if ctx.comparisonExpr():
            return ast.BooleanFactor(
                comparison=self.visitComparisonExpr(ctx.comparisonExpr()),
                location=self._get_location(ctx)
            )
        elif ctx.booleanExpr():
            return ast.BooleanFactor(
                nested_expr=self.visitBooleanExpr(ctx.booleanExpr()),
                location=self._get_location(ctx)
            )
        elif ctx.functionCall():
            return ast.BooleanFactor(
                function_call=self.visitFunctionCall(ctx.functionCall()),
                location=self._get_location(ctx)
            )

        return ast.BooleanFactor(location=self._get_location(ctx))

    def visitComparisonExpr(self, ctx: RulesDSLParser.ComparisonExprContext) -> ast.ComparisonExpr:
        left = self.visitValueExpr(ctx.valueExpr()[0])

        if ctx.comparisonOp():
            op = self.visitComparisonOp(ctx.comparisonOp())
            right = self.visitValueExpr(ctx.valueExpr()[1])
            return ast.ComparisonExpr(
                left=left,
                operator=op,
                right=right,
                location=self._get_location(ctx)
            )
        elif ctx.IN():
            values = []
            if ctx.valueList():
                for val_ctx in ctx.valueList().valueExpr():
                    values.append(self.visitValueExpr(val_ctx))
            return ast.ComparisonExpr(
                left=left,
                in_values=values,
                is_not_in=ctx.NOT() is not None,
                location=self._get_location(ctx)
            )
        elif ctx.IS_NULL() or (ctx.IS() and ctx.NULL() and not ctx.NOT()):
            return ast.ComparisonExpr(
                left=left,
                is_null_check=True,
                location=self._get_location(ctx)
            )
        elif ctx.IS_NOT_NULL() or (ctx.IS() and ctx.NOT() and ctx.NULL()):
            return ast.ComparisonExpr(
                left=left,
                is_not_null_check=True,
                location=self._get_location(ctx)
            )

        return ast.ComparisonExpr(left=left, location=self._get_location(ctx))

    def visitComparisonOp(self, ctx: RulesDSLParser.ComparisonOpContext) -> ast.ComparisonOp:
        if ctx.EQ():
            return ast.ComparisonOp.EQ
        elif ctx.NE():
            return ast.ComparisonOp.NE
        elif ctx.LT():
            return ast.ComparisonOp.LT
        elif ctx.GT():
            return ast.ComparisonOp.GT
        elif ctx.LE():
            return ast.ComparisonOp.LE
        elif ctx.GE():
            return ast.ComparisonOp.GE
        return ast.ComparisonOp.EQ

    def visitValueExpr(self, ctx: RulesDSLParser.ValueExprContext) -> ast.ValueExpr:
        terms = list(ctx.term())
        if len(terms) == 1:
            return self.visitTerm(terms[0])

        left = self.visitTerm(terms[0])
        for i in range(1, len(terms)):
            right = self.visitTerm(terms[i])
            op = '+'
            for j, child in enumerate(ctx.getChildren()):
                text = self._get_text(child)
                if text == '+' or text == '-':
                    if j > 0:
                        op = text
                        break

            left = ast.BinaryExpr(left=left, operator=op, right=right, location=self._get_location(ctx))

        return left

    def visitTerm(self, ctx: RulesDSLParser.TermContext) -> ast.ValueExpr:
        factors = list(ctx.factor())
        if len(factors) == 1:
            return self.visitFactor(factors[0])

        left = self.visitFactor(factors[0])
        for i in range(1, len(factors)):
            right = self.visitFactor(factors[i])
            op = '*'
            left = ast.BinaryExpr(left=left, operator=op, right=right, location=self._get_location(ctx))

        return left

    def visitFactor(self, ctx: RulesDSLParser.FactorContext) -> ast.ValueExpr:
        atom = self.visitAtom(ctx.atom())
        if ctx.MINUS():
            return ast.UnaryExpr(operand=atom, location=self._get_location(ctx))
        return atom

    def visitAtom(self, ctx: RulesDSLParser.AtomContext) -> ast.ValueExpr:
        if ctx.literal():
            return self.visitLiteral(ctx.literal())
        elif ctx.fieldPath():
            return self.visitFieldPath(ctx.fieldPath())
        elif ctx.functionCall():
            return self.visitFunctionCall(ctx.functionCall())
        elif ctx.listLiteral():
            return self.visitListLiteral(ctx.listLiteral())
        elif ctx.valueExpr():
            inner = self.visitValueExpr(ctx.valueExpr())
            return ast.ParenExpr(inner=inner, location=self._get_location(ctx))

        return ast.NullLiteral()

    def visitFieldPath(self, ctx: RulesDSLParser.FieldPathContext) -> ast.FieldPath:
        parts = []
        index = None

        for attr_ctx in ctx.attributeIdentifier():
            if attr_ctx.IDENTIFIER():
                parts.append(attr_ctx.IDENTIFIER().getText())
            elif attr_ctx.DQUOTED_STRING():
                parts.append(self._strip_quotes(attr_ctx.DQUOTED_STRING().getText()))

        if ctx.IDENTIFIER() and ctx.LBRACKET() and ctx.INTEGER():
            parts.insert(0, ctx.IDENTIFIER().getText())
            index = int(ctx.INTEGER().getText())

        return ast.FieldPath(parts=parts, index=index)

    def visitFunctionCall(self, ctx: RulesDSLParser.FunctionCallContext) -> ast.FunctionCall:
        name = ctx.IDENTIFIER().getText()
        arguments = []

        for val_ctx in ctx.valueExpr():
            arguments.append(self.visitValueExpr(val_ctx))

        return ast.FunctionCall(
            name=name,
            arguments=arguments,
            location=self._get_location(ctx)
        )
