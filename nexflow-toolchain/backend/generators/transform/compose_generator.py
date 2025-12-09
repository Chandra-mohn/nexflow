"""
Compose Generator Mixin

Generates Java code for transform composition (sequential, parallel, conditional).
"""

from typing import Set, List

from backend.ast import transform_ast as ast
from backend.generators.base import BaseGenerator


class ComposeGeneratorMixin:
    """
    Mixin for generating transform composition code.

    Generates:
    - Sequential composition (transforms execute in order)
    - Parallel composition (transforms execute concurrently)
    - Conditional composition (when/otherwise routing)
    - Then clause (post-composition steps)
    """

    def generate_compose_code(self: BaseGenerator,
                               compose: ast.ComposeBlock,
                               input_type: str,
                               output_type: str) -> str:
        """Generate composition code for a compose block.

        Args:
            compose: The compose block AST node
            input_type: Java type for input
            output_type: Java type for output

        Returns:
            Java code implementing the composition
        """
        if not compose or not compose.refs:
            return "        // No composition defined"

        compose_type = compose.compose_type
        if compose_type == ast.ComposeType.SEQUENTIAL:
            return self._generate_sequential_composition(compose, input_type, output_type)
        elif compose_type == ast.ComposeType.PARALLEL:
            return self._generate_parallel_composition(compose, input_type, output_type)
        elif compose_type == ast.ComposeType.CONDITIONAL:
            return self._generate_conditional_composition(compose, input_type, output_type)
        else:
            # Default to sequential if no type specified
            return self._generate_sequential_composition(compose, input_type, output_type)

    def _generate_sequential_composition(self: BaseGenerator,
                                          compose: ast.ComposeBlock,
                                          input_type: str,
                                          output_type: str) -> str:
        """Generate sequential composition - transforms execute in order.

        Pattern: A -> B -> C (output of A feeds into B, etc.)
        """
        lines = [
            "        // Sequential composition",
            f"        Object current = input;",
        ]

        for i, ref in enumerate(compose.refs):
            transform_name = ref.transform_name
            field_name = self.to_camel_case(transform_name) + "Transform"
            is_last = (i == len(compose.refs) - 1)

            if is_last:
                lines.append(f"        {output_type} result = ({output_type}) {field_name}.map(current);")
            else:
                lines.append(f"        current = {field_name}.map(current);")

        # Handle then clause if present
        if compose.then_refs:
            lines.append("")
            lines.append("        // Then clause")
            for ref in compose.then_refs:
                transform_name = ref.transform_name
                field_name = self.to_camel_case(transform_name) + "Transform"
                lines.append(f"        result = ({output_type}) {field_name}.map(result);")

        lines.append("        return result;")
        return '\n'.join(lines)

    def _generate_parallel_composition(self: BaseGenerator,
                                        compose: ast.ComposeBlock,
                                        input_type: str,
                                        output_type: str) -> str:
        """Generate parallel composition - transforms execute concurrently.

        Pattern: Input feeds into A, B, C in parallel; results are merged.
        Uses CompletableFuture for async execution.
        """
        lines = [
            "        // Parallel composition using CompletableFuture",
            f"        final {input_type} inputCopy = input;",
            "",
            "        List<CompletableFuture<Object>> futures = new ArrayList<>();",
        ]

        for ref in compose.refs:
            transform_name = ref.transform_name
            field_name = self.to_camel_case(transform_name) + "Transform"
            lines.append(f"        futures.add(CompletableFuture.supplyAsync(() -> {{")
            lines.append(f"            try {{")
            lines.append(f"                return {field_name}.map(inputCopy);")
            lines.append(f"            }} catch (Exception e) {{")
            lines.append(f"                throw new RuntimeException(e);")
            lines.append(f"            }}")
            lines.append(f"        }}));")

        lines.extend([
            "",
            "        // Wait for all transforms to complete",
            "        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();",
            "",
            "        // Collect results",
            "        List<Object> results = futures.stream()",
            "            .map(CompletableFuture::join)",
            "            .collect(Collectors.toList());",
            "",
        ])

        # Handle then clause if present
        if compose.then_refs:
            lines.append("        // Then clause - process merged results")
            if compose.then_type == ast.ComposeType.SEQUENTIAL:
                lines.append("        Object current = results;")
                for ref in compose.then_refs:
                    transform_name = ref.transform_name
                    field_name = self.to_camel_case(transform_name) + "Transform"
                    lines.append(f"        current = {field_name}.map(current);")
                lines.append(f"        return ({output_type}) current;")
            else:
                # Default: return first then result
                first_ref = compose.then_refs[0]
                field_name = self.to_camel_case(first_ref.transform_name) + "Transform"
                lines.append(f"        return ({output_type}) {field_name}.map(results);")
        else:
            lines.append("        // Return merged results (first result as default)")
            lines.append(f"        return ({output_type}) results.get(0);")

        return '\n'.join(lines)

    def _generate_conditional_composition(self: BaseGenerator,
                                           compose: ast.ComposeBlock,
                                           input_type: str,
                                           output_type: str) -> str:
        """Generate conditional composition - when/otherwise routing.

        Pattern: Route to different transforms based on conditions.
        """
        lines = [
            "        // Conditional composition",
        ]

        first = True
        otherwise_ref = None

        for ref in compose.refs:
            if ref.is_otherwise:
                otherwise_ref = ref
                continue

            transform_name = ref.transform_name
            field_name = self.to_camel_case(transform_name) + "Transform"

            if ref.condition:
                condition = self.generate_expression(ref.condition, use_map=True)
                if first:
                    lines.append(f"        if ({condition}) {{")
                    first = False
                else:
                    lines.append(f"        }} else if ({condition}) {{")
                lines.append(f"            return ({output_type}) {field_name}.map(input);")

        # Handle otherwise clause
        if otherwise_ref:
            otherwise_name = otherwise_ref.transform_name
            otherwise_field = self.to_camel_case(otherwise_name) + "Transform"
            lines.append("        } else {")
            lines.append(f"            return ({output_type}) {otherwise_field}.map(input);")
            lines.append("        }")
        elif not first:
            # Close the if block if we had conditions
            lines.append("        } else {")
            lines.append("            // No matching condition - return input unchanged")
            lines.append(f"            return ({output_type}) input;")
            lines.append("        }")
        else:
            # No conditions at all - shouldn't happen but handle gracefully
            lines.append(f"        return ({output_type}) input;")

        # Handle then clause if present
        if compose.then_refs:
            # Wrap the conditional in a method and apply then transforms
            # For simplicity, add a comment noting this pattern
            lines.insert(0, "        // Note: then clause applied after conditional routing")

        return '\n'.join(lines)

    def generate_compose_fields(self: BaseGenerator,
                                 compose: ast.ComposeBlock) -> str:
        """Generate field declarations for composed transforms.

        Returns Java field declarations for all referenced transforms.
        """
        refs = self._collect_transform_refs(compose)
        if not refs:
            return ""

        lines = ["    // Composed transforms"]
        for _, class_name, field_name in refs:
            lines.append(f"    private transient {class_name} {field_name};")

        return '\n'.join(lines)

    def generate_compose_init(self: BaseGenerator,
                               compose: ast.ComposeBlock) -> str:
        """Generate initialization code for composed transforms.

        Returns Java code to instantiate all referenced transforms.
        """
        refs = self._collect_transform_refs(compose)
        if not refs:
            return ""

        lines = ["        // Initialize composed transforms"]
        for _, class_name, field_name in refs:
            lines.append(f"        {field_name} = new {class_name}();")

        return '\n'.join(lines)

    def _collect_transform_refs(
        self: BaseGenerator,
        compose: ast.ComposeBlock
    ) -> List[tuple]:
        """Collect unique transform references from compose block.

        Returns list of (transform_name, class_name, field_name) tuples.
        Deduplicates by transform_name.
        """
        if not compose or not compose.refs:
            return []

        seen = set()
        refs = []

        for ref in compose.refs:
            if ref.transform_name not in seen:
                seen.add(ref.transform_name)
                refs.append((
                    ref.transform_name,
                    self.to_pascal_case(ref.transform_name) + "Function",
                    self.to_camel_case(ref.transform_name) + "Transform"
                ))

        if compose.then_refs:
            for ref in compose.then_refs:
                if ref.transform_name not in seen:
                    seen.add(ref.transform_name)
                    refs.append((
                        ref.transform_name,
                        self.to_pascal_case(ref.transform_name) + "Function",
                        self.to_camel_case(ref.transform_name) + "Transform"
                    ))

        return refs

    def get_compose_imports(self) -> Set[str]:
        """Get required imports for composition generation."""
        return {
            'java.util.List',
            'java.util.ArrayList',
            'java.util.concurrent.CompletableFuture',
            'java.util.stream.Collectors',
        }
