# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Rule Generator Module

Generates Java rule evaluation code from Schema AST definitions.
Supports business_logic pattern with given/calculate/return blocks.
"""

from typing import List

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator
from backend.generators.schema.rule_io_classes import RuleIOClassesMixin


class RuleGeneratorMixin(RuleIOClassesMixin):
    """Mixin providing rule code generation capabilities.

    Generates:
    - Rule evaluation methods
    - Input parameter classes (given block)
    - Output result classes (return block)
    - Calculation logic (calculate block)
    """

    def _generate_rules_class(self: BaseGenerator,
                               schema: ast.SchemaDefinition,
                               class_name: str,
                               package: str) -> str:
        """Generate rules helper class for business_logic pattern.

        Returns complete Java class for rule evaluation.
        """
        if not schema.rules:
            return ""

        header = self.generate_java_header(
            f"{class_name}Rules",
            f"Business rules for {schema.name} schema"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'java.math.BigDecimal',
            'java.util.Objects',
            'java.util.logging.Logger',
        ])

        # Generate components for each rule
        rule_classes = []
        rule_methods = []
        for rule in schema.rules:
            rule_classes.append(self._generate_rule_input_output(rule, class_name))
            rule_methods.append(self._generate_rule_evaluation_method(rule, class_name))

        rules_block = '\n\n'.join(rule_classes)
        methods_block = '\n\n'.join(rule_methods)

        return f'''{header}
{package_decl}
{imports}

/**
 * Business rules for {schema.name}.
 *
 * Pattern: business_logic
 * Purpose: Declarative rule evaluation with typed inputs/outputs
 * Rules: {len(schema.rules)}
 */
public class {class_name}Rules {{

    private static final Logger LOGGER = Logger.getLogger({class_name}Rules.class.getName());

{rules_block}

{methods_block}
}}
'''

    def _generate_rule_input_output(self: BaseGenerator,
                                     rule: ast.RuleBlock,
                                     class_name: str) -> str:
        """Generate input and output classes for a rule."""
        rule_name = self.to_pascal_case(rule.name)

        input_class = self._generate_input_class(rule, rule_name)
        output_class = self._generate_output_class(rule, rule_name)

        return f'''    // =========================================================================
    // Rule: {rule.name}
    // =========================================================================

{input_class}

{output_class}'''

    def _generate_rule_evaluation_method(self: BaseGenerator,
                                          rule: ast.RuleBlock,
                                          class_name: str) -> str:
        """Generate rule evaluation method."""
        rule_name = self.to_pascal_case(rule.name)
        method_name = self.to_java_field_name(rule.name)

        calc_block = self._generate_calculation_block(rule)
        output_construction = self._generate_output_construction(rule, rule_name)

        return f'''    /**
     * Evaluate the {rule.name} rule.
     */
    public static {rule_name}Output {method_name}({rule_name}Input input) {{
        Objects.requireNonNull(input, "Input cannot be null");
        LOGGER.fine("Evaluating rule: {rule.name}");

{calc_block}

{output_construction}
    }}'''

    def _generate_calculation_block(self: BaseGenerator,
                                     rule: ast.RuleBlock) -> str:
        """Generate calculation statements from calculate block."""
        if not rule.calculate or not rule.calculate.calculations:
            return '        // No calculations defined'

        statements = []
        statements.append('        // Calculations')

        for calc in rule.calculate.calculations:
            java_field = self.to_java_field_name(calc.field_name)
            expression = calc.expression.raw_text if calc.expression else 'null'
            java_expr = self._convert_expression_to_java(expression, rule)
            statements.append(f'        Object {java_field} = {java_expr};')

        return '\n'.join(statements)

    def _generate_output_construction(self: BaseGenerator,
                                       rule: ast.RuleBlock,
                                       rule_name: str) -> str:
        """Generate output object construction."""
        if not rule.return_block or not rule.return_block.fields:
            return f'        return new {rule_name}Output();'

        output_args = []
        for field in rule.return_block.fields:
            java_field = self.to_java_field_name(field.name)
            java_type = self._get_rule_field_type(field.field_type)

            calc_names = set()
            if rule.calculate:
                calc_names = {self.to_java_field_name(c.field_name) for c in rule.calculate.calculations}

            if java_field in calc_names:
                output_args.append(f'({java_type}) {java_field}')
            else:
                output_args.append(f'input.get{java_field[0].upper()}{java_field[1:]}()')

        args_str = ', '.join(output_args)

        return f'''        // Construct output
        return new {rule_name}Output({args_str});'''

    def _convert_expression_to_java(self: BaseGenerator,
                                     expression: str,
                                     rule: ast.RuleBlock) -> str:
        """Convert DSL expression to Java expression."""
        if not expression:
            return 'null'

        # Simple field reference
        if expression.isidentifier():
            if rule.given:
                input_fields = {f.name for f in rule.given.fields}
                if expression in input_fields:
                    java_field = self.to_java_field_name(expression)
                    return f'input.get{java_field[0].upper()}{java_field[1:]}()'

            if rule.calculate:
                calc_fields = {c.field_name for c in rule.calculate.calculations}
                if expression in calc_fields:
                    return self.to_java_field_name(expression)

        # Simple arithmetic expressions
        if any(op in expression for op in ['+', '-', '*', '/']):
            result = expression
            if rule.given:
                for field in rule.given.fields:
                    java_field = self.to_java_field_name(field.name)
                    getter = f'input.get{java_field[0].upper()}{java_field[1:]}()'
                    result = result.replace(field.name, getter)
            return result

        # String literal
        if expression.startswith('"') or expression.startswith("'"):
            return expression.replace("'", '"')

        # Numeric literal
        try:
            float(expression)
            return expression
        except ValueError:
            pass

        return f'/* Expression: {expression} */ null'
