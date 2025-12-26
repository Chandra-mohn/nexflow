# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Advanced Operators Mixin

Generates Flink code for: validate_input, evaluate, lookup, parallel operators.
"""

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case


class AdvancedOperatorsMixin:
    """Mixin for advanced Flink operator wiring (validate, evaluate, lookup, parallel)."""

    def _wire_validate_input(self, validate: ast.ValidateInputDecl,
                             input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a validate_input operator using ProcessFunction with side output.

        Valid records continue on main stream.
        Invalid records are emitted to a side output for error handling.
        """
        output_stream = f"validated{idx}Stream"
        invalid_tag = f"invalid{idx}Tag"
        expression = validate.expression if hasattr(validate, 'expression') and validate.expression else "true"

        java_condition = self._compile_route_condition(expression)

        code = f'''        // Validate Input: {expression[:50]}{'...' if len(expression) > 50 else ''}
        OutputTag<{input_type}> {invalid_tag} = new OutputTag<{input_type}>("invalid-records-{idx}") {{}};

        SingleOutputStreamOperator<{input_type}> {output_stream} = {input_stream}
            .process(new ProcessFunction<{input_type}, {input_type}>() {{
                @Override
                public void processElement({input_type} value, Context ctx, Collector<{input_type}> out) throws Exception {{
                    if ({java_condition}) {{
                        out.collect(value);
                    }} else {{
                        ctx.output({invalid_tag}, value);
                    }}
                }}
            }})
            .name("validate-input-{idx}");

        // Invalid records available via: {output_stream}.getSideOutput({invalid_tag})
'''
        return code, output_stream, input_type

    def _wire_evaluate(self, evaluate: ast.EvaluateDecl,
                       input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire an evaluate operator for rules or expression evaluation.

        Supports two forms:
        1. 'evaluate using <rule_name>': Wire to L4 rules evaluator class
        2. 'evaluate <expression>': Inline expression evaluation
        """
        output_stream = f"evaluated{idx}Stream"
        rule_name = getattr(evaluate, 'rule_name', None)

        if rule_name:
            evaluator_class = to_pascal_case(rule_name) + "Evaluator"
            code = f'''        // Evaluate: using {rule_name}
        DataStream<{input_type}> {output_stream} = {input_stream}
            .map(new {evaluator_class}())
            .name("evaluate-{rule_name}");
'''
        else:
            expression = evaluate.expression if hasattr(evaluate, 'expression') and evaluate.expression else "true"
            java_expr = self._compile_route_condition(expression)

            code = f'''        // Evaluate: {expression[:40]}{'...' if len(expression) > 40 else ''}
        DataStream<{input_type}> {output_stream} = {input_stream}
            .map(value -> {{
                // Evaluate expression and set result on record
                boolean evaluationResult = {java_expr};
                // Return record (evaluation result can be accessed via getEvaluationResult())
                return value;
            }})
            .name("evaluate-inline-{idx}");
'''
        return code, output_stream, input_type

    def _wire_lookup(self, lookup: ast.LookupDecl,
                     input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a lookup operator using AsyncDataStream.

        Performs async lookup against external data source.
        Returns LookupResult wrapper with found/not-found semantics.
        """
        source_name = lookup.source_name
        lookup_class = to_pascal_case(source_name) + "LookupFunction"
        output_stream = f"lookup{idx}Stream"
        output_type = f"LookupResult<{input_type}>"

        timeout_ms = getattr(lookup, 'timeout_ms', 30000) or 30000
        on_fields = getattr(lookup, 'on_fields', None) or []
        on_fields_array = ', '.join(f'"{f}"' for f in on_fields) if on_fields else ''

        code = f'''        // Lookup: {source_name}
        DataStream<{output_type}> {output_stream} = AsyncDataStream
            .unorderedWait(
                {input_stream},
                new {lookup_class}(new String[]{{{on_fields_array}}}),
                {timeout_ms}, TimeUnit.MILLISECONDS,
                100  // async capacity
            )
            .name("lookup-{source_name}");
'''
        return code, output_stream, output_type

    def _wire_parallel(self, parallel: ast.ParallelDecl,
                       input_stream: str, input_type: str, idx: int) -> tuple:
        """Wire a parallel execution block with multiple branches.

        Pattern:
        1. Create OutputTag for each branch
        2. Split stream using ProcessFunction emitting to side outputs
        3. Process each branch body recursively
        4. Merge branches at the end using union
        """
        parallel_name = parallel.name
        branches = parallel.branches if hasattr(parallel, 'branches') and parallel.branches else []

        if not branches:
            return f"        // Parallel block: {parallel_name} (no branches defined)", input_stream, input_type

        lines = [f"        // Parallel Block: {parallel_name}"]
        lines.append("")

        # Generate output tags for each branch
        branch_tags = []
        for branch in branches:
            tag_name = f"{to_camel_case(branch.branch_name)}{idx}Tag"
            branch_tags.append(tag_name)
            lines.append(f'        OutputTag<{input_type}> {tag_name} = new OutputTag<{input_type}>("{branch.branch_name}") {{}};')

        lines.append("")

        # Generate split ProcessFunction
        split_stream = f"parallel{idx}SplitStream"
        lines.append(f'''        // Split into parallel branches
        SingleOutputStreamOperator<{input_type}> {split_stream} = {input_stream}
            .process(new ProcessFunction<{input_type}, {input_type}>() {{
                @Override
                public void processElement({input_type} value, Context ctx, Collector<{input_type}> out) throws Exception {{
                    // Emit to all branches (broadcast pattern)''')

        for tag_name in branch_tags:
            lines.append(f'                    ctx.output({tag_name}, value);')

        lines.append('''                }
            })
            .name("parallel-split-''' + parallel_name + '''");
''')

        # Process each branch
        branch_streams = []
        for i, branch in enumerate(branches):
            tag_name = branch_tags[i]
            branch_stream = f"{to_camel_case(branch.branch_name)}{idx}Stream"
            branch_streams.append(branch_stream)

            lines.append(f'        // Branch: {branch.branch_name}')
            lines.append(f'        DataStream<{input_type}> {branch_stream} = {split_stream}.getSideOutput({tag_name});')

            # Wire branch body operations (recursive)
            current_branch_stream = branch_stream
            current_branch_type = input_type
            branch_body = branch.body if hasattr(branch, 'body') and branch.body else []

            for j, op in enumerate(branch_body):
                op_code, new_stream, new_type = self._wire_operator(
                    op, current_branch_stream, current_branch_type, idx * 100 + i * 10 + j
                )
                if op_code:
                    lines.append(op_code)
                    current_branch_stream = new_stream
                    current_branch_type = new_type

            branch_streams[i] = current_branch_stream
            lines.append("")

        # Merge branches
        output_stream = f"parallel{idx}MergedStream"
        if len(branch_streams) >= 2:
            first_stream = branch_streams[0]
            other_streams = ', '.join(branch_streams[1:])
            lines.append(f'''        // Merge parallel branches
        DataStream<{input_type}> {output_stream} = {first_stream}
            .union({other_streams})
            .name("parallel-merge-{parallel_name}");
''')
        elif len(branch_streams) == 1:
            output_stream = branch_streams[0]
        else:
            output_stream = input_stream

        return '\n'.join(lines), output_stream, input_type
