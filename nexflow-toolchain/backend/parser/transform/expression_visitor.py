# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Expression Visitor Mixin for Transform Parser

Handles parsing of expressions, literals, function calls, and all expression types
including binary, unary, when, index, and optional chain expressions.
"""


from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformExpressionVisitorMixin:
    """Mixin for expression visitor methods."""

    def visitExpression(self, ctx: TransformDSLParser.ExpressionContext) -> ast.Expression:
        """Visit expression based on grammar alternatives."""
        expressions = ctx.expression()

        # Handle unary operations: unaryOp expression
        if ctx.unaryOp() and len(expressions) == 1:
            operator = self._parse_unary_op(ctx.unaryOp())
            operand = self.visitExpression(expressions[0])
            return ast.UnaryExpression(
                operator=operator,
                operand=operand,
                location=self._get_location(ctx)
            )

        # Handle arithmetic operations: expression arithmeticOp expression
        if ctx.arithmeticOp() and len(expressions) >= 2:
            left = self.visitExpression(expressions[0])
            operator = self._get_text(ctx.arithmeticOp())
            right = self.visitExpression(expressions[1])
            return ast.BinaryExpression(
                left=left,
                operator=operator,
                right=right,
                location=self._get_location(ctx)
            )

        # Handle comparison operations: expression comparisonOp expression
        if ctx.comparisonOp() and len(expressions) >= 2:
            left = self.visitExpression(expressions[0])
            operator = self._get_text(ctx.comparisonOp())
            right = self.visitExpression(expressions[1])
            return ast.BinaryExpression(
                left=left,
                operator=operator,
                right=right,
                location=self._get_location(ctx)
            )

        # Handle logical operations: expression logicalOp expression
        if ctx.logicalOp() and len(expressions) >= 2:
            left = self.visitExpression(expressions[0])
            operator = self._get_text(ctx.logicalOp())
            right = self.visitExpression(expressions[1])
            return ast.BinaryExpression(
                left=left,
                operator=operator,
                right=right,
                location=self._get_location(ctx)
            )

        # Handle null coalescing: expression (DEFAULT_KW | '??') expression
        # Check for DEFAULT_KW token or COALESCE (??) token
        has_default = ctx.DEFAULT_KW() is not None
        has_coalesce = ctx.COALESCE() is not None
        if (has_default or has_coalesce) and len(expressions) >= 2:
            left = self.visitExpression(expressions[0])
            right = self.visitExpression(expressions[1])
            return ast.BinaryExpression(
                left=left,
                operator='??',  # Normalize to ?? internally
                right=right,
                location=self._get_location(ctx)
            )

        # Handle between: expression 'between' expression 'and' expression
        text = self._get_text(ctx)
        if 'between' in text.lower() and len(expressions) >= 3:
            value = self.visitExpression(expressions[0])
            low = self.visitExpression(expressions[1])
            high = self.visitExpression(expressions[2])
            return ast.BetweenExpression(
                value=value,
                low=low,
                high=high,
                negated='not' in text.lower() and 'between' in text.lower(),
                location=self._get_location(ctx)
            )

        # Handle in: expression 'in' listLiteral
        if ctx.listLiteral() and len(expressions) >= 1:
            value = self.visitExpression(expressions[0])
            list_values = self.visitListLiteral(ctx.listLiteral())
            return ast.InExpression(
                value=value,
                values=list_values,
                negated='not' in text.lower(),
                location=self._get_location(ctx)
            )

        # Handle is null: expression 'is' 'null'
        if 'is' in text.lower() and 'null' in text.lower() and len(expressions) >= 1:
            value = self.visitExpression(expressions[0])
            return ast.IsNullExpression(
                value=value,
                negated='not' in text.lower(),
                location=self._get_location(ctx)
            )

        # Handle primary expressions
        if ctx.primaryExpression():
            return self.visitPrimaryExpression(ctx.primaryExpression())

        # Fallback
        return ast.FieldPath(parts=[self._get_text(ctx)])

    def visitPrimaryExpression(self, ctx: TransformDSLParser.PrimaryExpressionContext) -> ast.Expression:
        """Visit primary expression."""
        if ctx.literal():
            return self.visitLiteral(ctx.literal())
        elif ctx.fieldPath():
            return self.visitFieldPath(ctx.fieldPath())
        elif ctx.functionCall():
            return self.visitFunctionCall(ctx.functionCall())
        elif ctx.expression():
            return self.visitExpression(ctx.expression())
        elif ctx.whenExpression():
            return self.visitWhenExpression(ctx.whenExpression())
        elif ctx.indexExpression():
            return self.visitIndexExpression(ctx.indexExpression())
        elif ctx.optionalChainExpression():
            return self.visitOptionalChainExpression(ctx.optionalChainExpression())
        elif ctx.objectLiteral():
            return self.visitObjectLiteral(ctx.objectLiteral())
        elif ctx.lambdaExpression():
            return self.visitLambdaExpression(ctx.lambdaExpression())
        elif ctx.listLiteral():
            return self.visitListLiteral(ctx.listLiteral())

        return ast.FieldPath(parts=[self._get_text(ctx)])

    def visitWhenExpression(self, ctx: TransformDSLParser.WhenExpressionContext) -> ast.WhenExpression:
        branches = []
        otherwise = None

        expressions = ctx.expression()
        for i in range(0, len(expressions) - 1, 2):
            condition = self.visitExpression(expressions[i])
            result = self.visitExpression(expressions[i + 1])
            branches.append(ast.WhenBranch(
                condition=condition,
                result=result,
                location=self._get_location(ctx)
            ))

        if len(expressions) % 2 == 1:
            otherwise = self.visitExpression(expressions[-1])
        else:
            otherwise = ast.NullLiteral()

        return ast.WhenExpression(
            branches=branches,
            otherwise=otherwise,
            location=self._get_location(ctx)
        )

    def visitIndexExpression(self, ctx: TransformDSLParser.IndexExpressionContext) -> ast.IndexExpression:
        base = self.visitFieldPath(ctx.fieldPath())
        index = self.visitExpression(ctx.expression())
        return ast.IndexExpression(
            base=base,
            index=index,
            location=self._get_location(ctx)
        )

    def visitOptionalChainExpression(self, ctx: TransformDSLParser.OptionalChainExpressionContext) -> ast.OptionalChainExpression:
        base = self.visitFieldPath(ctx.fieldPath())
        # Optional chain now uses fieldOrKeyword instead of IDENTIFIER
        chain = [self._get_text(fok) for fok in ctx.fieldOrKeyword()]
        return ast.OptionalChainExpression(
            base=base,
            chain=chain,
            location=self._get_location(ctx)
        )

    def visitFunctionCall(self, ctx: TransformDSLParser.FunctionCallContext) -> ast.FunctionCall:
        # functionCall can be: functionName(...) or fieldPath.functionName(...)
        name = ""
        object_ref = None

        if ctx.functionName():
            name = self._get_text(ctx.functionName())

        if ctx.fieldPath():
            # This is a method call like state.get_window(...)
            object_ref = self.visitFieldPath(ctx.fieldPath())

        arguments = []
        for expr_ctx in ctx.expression():
            arguments.append(self.visitExpression(expr_ctx))

        return ast.FunctionCall(
            name=name,
            arguments=arguments,
            object_ref=object_ref,
            location=self._get_location(ctx)
        )

    def _parse_unary_op(self, ctx: TransformDSLParser.UnaryOpContext) -> ast.UnaryOp:
        op_text = self._get_text(ctx).lower()
        if 'not' in op_text:
            return ast.UnaryOp.NOT
        return ast.UnaryOp.MINUS

    # =========================================================================
    # Literals
    # =========================================================================

    def visitLiteral(self, ctx: TransformDSLParser.LiteralContext) -> ast.Literal:
        if ctx.STRING():
            return ast.StringLiteral(value=self._strip_quotes(ctx.STRING().getText()))
        elif ctx.numberLiteral():
            num = self._parse_number(ctx.numberLiteral())
            if isinstance(num, float):
                return ast.DecimalLiteral(value=num)
            return ast.IntegerLiteral(value=num)
        elif ctx.getText().lower() == 'true':
            return ast.BooleanLiteral(value=True)
        elif ctx.getText().lower() == 'false':
            return ast.BooleanLiteral(value=False)
        elif ctx.getText().lower() == 'null':
            return ast.NullLiteral()

        return ast.StringLiteral(value=ctx.getText())

    def visitListLiteral(self, ctx: TransformDSLParser.ListLiteralContext) -> ast.ListLiteral:
        values = []
        for expr_ctx in ctx.expression():
            values.append(self.visitExpression(expr_ctx))
        return ast.ListLiteral(values=values)

    # =========================================================================
    # Lambda Expressions (RFC: Collection Operations Instead of Loops)
    # =========================================================================

    def visitLambdaExpression(self, ctx: TransformDSLParser.LambdaExpressionContext) -> ast.LambdaExpression:
        """Parse lambda expression: x -> expr or (x, y) -> expr."""
        parameters = []
        for id_token in ctx.IDENTIFIER():
            parameters.append(id_token.getText())

        body = self.visitExpression(ctx.expression())

        return ast.LambdaExpression(
            parameters=parameters,
            body=body,
            location=self._get_location(ctx)
        )

    # =========================================================================
    # Object Literals
    # =========================================================================

    def visitObjectLiteral(self, ctx: TransformDSLParser.ObjectLiteralContext) -> ast.ObjectLiteral:
        """Parse object literal: { field: value, ... }."""
        fields = []
        for field_ctx in ctx.objectField():
            fields.append(self.visitObjectField(field_ctx))

        return ast.ObjectLiteral(
            fields=fields,
            location=self._get_location(ctx)
        )

    def visitObjectField(self, ctx: TransformDSLParser.ObjectFieldContext) -> ast.ObjectLiteralField:
        """Parse object literal field: name: value."""
        name = self._get_text(ctx.objectFieldName())
        value = self.visitExpression(ctx.expression())

        return ast.ObjectLiteralField(
            name=name,
            value=value,
            location=self._get_location(ctx)
        )
