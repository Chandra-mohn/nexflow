"""
Decision Table Visitor Mixin for Rules Parser

Handles parsing of decision tables, given blocks, decide blocks, and table matrices.
"""

from typing import Union

from backend.ast import rules_ast as ast
from backend.parser.generated.rules import RulesDSLParser


class RulesDecisionTableVisitorMixin:
    """Mixin for decision table visitor methods."""

    def visitDecisionTableDef(self, ctx: RulesDSLParser.DecisionTableDefContext) -> ast.DecisionTableDef:
        name = self._get_text(ctx.tableName())

        hit_policy = None
        if ctx.hitPolicyDecl():
            hit_policy = self.visitHitPolicyDecl(ctx.hitPolicyDecl())

        description = None
        if ctx.descriptionDecl():
            desc_ctx = ctx.descriptionDecl()
            string_lit = desc_ctx.stringLiteral()
            if string_lit:
                if string_lit.DQUOTED_STRING():
                    description = self._strip_quotes(string_lit.DQUOTED_STRING().getText())
                elif string_lit.SQUOTED_STRING():
                    description = self._strip_quotes(string_lit.SQUOTED_STRING().getText())

        given = None
        if ctx.givenBlock():
            given = self.visitGivenBlock(ctx.givenBlock())

        decide = None
        if ctx.decideBlock():
            decide = self.visitDecideBlock(ctx.decideBlock())

        return_spec = None
        if ctx.returnSpec():
            return_spec = self.visitReturnSpec(ctx.returnSpec())

        execute_spec = None
        if ctx.executeSpec():
            execute_spec = self.visitExecuteSpec(ctx.executeSpec())

        return ast.DecisionTableDef(
            name=name,
            hit_policy=hit_policy,
            description=description,
            given=given,
            decide=decide,
            return_spec=return_spec,
            execute_spec=execute_spec,
            location=self._get_location(ctx)
        )

    def visitHitPolicyDecl(self, ctx: RulesDSLParser.HitPolicyDeclContext) -> ast.HitPolicyType:
        policy_ctx = ctx.hitPolicyType()
        if policy_ctx.FIRST_MATCH():
            return ast.HitPolicyType.FIRST_MATCH
        elif policy_ctx.SINGLE_HIT():
            return ast.HitPolicyType.SINGLE_HIT
        elif policy_ctx.MULTI_HIT():
            return ast.HitPolicyType.MULTI_HIT
        return ast.HitPolicyType.FIRST_MATCH

    def visitGivenBlock(self, ctx: RulesDSLParser.GivenBlockContext) -> ast.GivenBlock:
        params = []
        for param_ctx in ctx.inputParam():
            params.append(self.visitInputParam(param_ctx))
        return ast.GivenBlock(params=params, location=self._get_location(ctx))

    def visitInputParam(self, ctx: RulesDSLParser.InputParamContext) -> ast.InputParam:
        name = self._get_text(ctx.paramName())
        param_type = self.visitParamType(ctx.paramType())
        comment = None
        if ctx.inlineComment():
            comment = self._get_text(ctx.inlineComment())
        return ast.InputParam(
            name=name,
            param_type=param_type,
            comment=comment,
            location=self._get_location(ctx)
        )

    def visitParamType(self, ctx: RulesDSLParser.ParamTypeContext) -> Union[ast.BaseType, str]:
        if ctx.baseType():
            return self.visitBaseType(ctx.baseType())
        elif ctx.MONEY_TYPE():
            return ast.BaseType.MONEY
        elif ctx.PERCENTAGE_TYPE():
            return ast.BaseType.PERCENTAGE
        elif ctx.IDENTIFIER():
            return ctx.IDENTIFIER().getText()
        return ast.BaseType.TEXT

    def visitBaseType(self, ctx: RulesDSLParser.BaseTypeContext) -> ast.BaseType:
        if ctx.TEXT_TYPE():
            return ast.BaseType.TEXT
        elif ctx.NUMBER_TYPE():
            return ast.BaseType.NUMBER
        elif ctx.BOOLEAN_TYPE():
            return ast.BaseType.BOOLEAN
        elif ctx.DATE_TYPE():
            return ast.BaseType.DATE
        elif ctx.TIMESTAMP_TYPE():
            return ast.BaseType.TIMESTAMP
        return ast.BaseType.TEXT

    def visitDecideBlock(self, ctx: RulesDSLParser.DecideBlockContext) -> ast.DecideBlock:
        matrix = self.visitTableMatrix(ctx.tableMatrix())
        return ast.DecideBlock(matrix=matrix, location=self._get_location(ctx))

    def visitTableMatrix(self, ctx: RulesDSLParser.TableMatrixContext) -> ast.TableMatrix:
        header_ctx = ctx.tableHeader()
        headers = []
        has_priority = False

        if header_ctx.priorityHeader():
            has_priority = True

        for col_ctx in header_ctx.columnHeader():
            headers.append(ast.ColumnHeader(
                name=col_ctx.IDENTIFIER().getText(),
                location=self._get_location(col_ctx)
            ))

        rows = []
        for row_ctx in ctx.tableRow():
            rows.append(self.visitTableRow(row_ctx))

        return ast.TableMatrix(
            headers=headers,
            has_priority=has_priority,
            rows=rows,
            location=self._get_location(ctx)
        )

    def visitTableRow(self, ctx: RulesDSLParser.TableRowContext) -> ast.TableRow:
        priority = None
        if ctx.priorityCell():
            priority = int(ctx.priorityCell().INTEGER().getText())

        cells = []
        for cell_ctx in ctx.cell():
            cells.append(self.visitCell(cell_ctx))

        return ast.TableRow(
            priority=priority,
            cells=cells,
            location=self._get_location(ctx)
        )

    def visitCell(self, ctx: RulesDSLParser.CellContext) -> ast.TableCell:
        content_ctx = ctx.cellContent()
        content = None

        if content_ctx.condition():
            content = self.visitCondition(content_ctx.condition())
        elif content_ctx.action():
            content = self.visitAction(content_ctx.action())

        return ast.TableCell(content=content, location=self._get_location(ctx))

    def visitReturnSpec(self, ctx: RulesDSLParser.ReturnSpecContext) -> ast.ReturnSpec:
        params = []
        for param_ctx in ctx.returnParam():
            params.append(self.visitReturnParam(param_ctx))
        return ast.ReturnSpec(params=params, location=self._get_location(ctx))

    def visitReturnParam(self, ctx: RulesDSLParser.ReturnParamContext) -> ast.ReturnParam:
        name = self._get_text(ctx.paramName())
        param_type = self.visitParamType(ctx.paramType())
        return ast.ReturnParam(name=name, param_type=param_type, location=self._get_location(ctx))

    def visitExecuteSpec(self, ctx: RulesDSLParser.ExecuteSpecContext) -> ast.ExecuteSpec:
        exec_ctx = ctx.executeType()

        if exec_ctx.YES():
            return ast.ExecuteSpec(execute_type=ast.ExecuteType.YES, location=self._get_location(ctx))
        elif exec_ctx.MULTI():
            return ast.ExecuteSpec(execute_type=ast.ExecuteType.MULTI, location=self._get_location(ctx))
        elif exec_ctx.IDENTIFIER():
            return ast.ExecuteSpec(
                execute_type=ast.ExecuteType.CUSTOM,
                custom_name=exec_ctx.IDENTIFIER().getText(),
                location=self._get_location(ctx)
            )

        return ast.ExecuteSpec(execute_type=ast.ExecuteType.YES, location=self._get_location(ctx))
