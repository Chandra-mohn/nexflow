"""
Validation Visitor Mixin for Transform Parser

Handles parsing of validation blocks (input, output, invariant), validation rules,
and validation messages.
"""

from typing import Union

from backend.ast import transform_ast as ast
from backend.parser.generated.transform import TransformDSLParser


class TransformValidationVisitorMixin:
    """Mixin for validation block visitor methods."""

    def visitValidateInputBlock(self, ctx: TransformDSLParser.ValidateInputBlockContext) -> ast.ValidateInputBlock:
        rules = []
        for rule_ctx in ctx.validationRule():
            rules.append(self.visitValidationRule(rule_ctx))
        return ast.ValidateInputBlock(
            rules=rules,
            location=self._get_location(ctx)
        )

    def visitValidateOutputBlock(self, ctx: TransformDSLParser.ValidateOutputBlockContext) -> ast.ValidateOutputBlock:
        rules = []
        for rule_ctx in ctx.validationRule():
            rules.append(self.visitValidationRule(rule_ctx))
        return ast.ValidateOutputBlock(
            rules=rules,
            location=self._get_location(ctx)
        )

    def visitInvariantBlock(self, ctx: TransformDSLParser.InvariantBlockContext) -> ast.InvariantBlock:
        rules = []
        for rule_ctx in ctx.validationRule():
            rules.append(self.visitValidationRule(rule_ctx))
        return ast.InvariantBlock(
            rules=rules,
            location=self._get_location(ctx)
        )

    def visitValidationRule(self, ctx: TransformDSLParser.ValidationRuleContext) -> ast.ValidationRule:
        condition = self.visitExpression(ctx.expression())
        message = self.visitValidationMessage(ctx.validationMessage())

        nested_rules = None
        if ctx.validationRule():
            nested_rules = [self.visitValidationRule(rule_ctx) for rule_ctx in ctx.validationRule()]

        return ast.ValidationRule(
            condition=condition,
            message=message,
            nested_rules=nested_rules,
            location=self._get_location(ctx)
        )

    def visitValidationMessage(self, ctx: TransformDSLParser.ValidationMessageContext) -> Union[str, ast.ValidationMessageObject]:
        if ctx.STRING():
            return self._strip_quotes(ctx.STRING().getText())
        elif ctx.validationMessageObject():
            return self.visitValidationMessageObject(ctx.validationMessageObject())
        return ""

    def visitValidationMessageObject(self, ctx: TransformDSLParser.ValidationMessageObjectContext) -> ast.ValidationMessageObject:
        message = ""
        code = None
        severity = None

        strings = ctx.STRING()
        if strings:
            message = self._strip_quotes(strings[0].getText())
            if len(strings) > 1:
                code = self._strip_quotes(strings[1].getText())
        if ctx.severityLevel():
            severity = self.visitSeverityLevel(ctx.severityLevel())

        return ast.ValidationMessageObject(
            message=message,
            code=code,
            severity=severity,
            location=self._get_location(ctx)
        )

    def visitSeverityLevel(self, ctx: TransformDSLParser.SeverityLevelContext) -> ast.SeverityLevel:
        level_text = self._get_text(ctx).lower()
        level_map = {
            'error': ast.SeverityLevel.ERROR,
            'warning': ast.SeverityLevel.WARNING,
            'info': ast.SeverityLevel.INFO,
        }
        return level_map.get(level_text, ast.SeverityLevel.ERROR)
