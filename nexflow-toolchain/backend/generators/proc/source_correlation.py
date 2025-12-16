# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Source Correlation Mixin

Generates store and match action code for stream correlation.
"""

from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.ast import proc_ast as ast


class SourceCorrelationMixin:
    """
    Mixin for generating store and match action code.

    Generates:
    - Store action (buffer for later matching)
    - Match action (join with buffered state)
    """

    # Track streams that are stored in buffers for later matching
    _stored_streams: Dict[str, Tuple[str, str]] = {}  # buffer_name -> (stream_var, schema_class)

    def _generate_store_action(
        self,
        store_action: 'ast.StoreAction',
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> str:
        """
        Generate store action code.

        Feature 3a: store in buffer

        Stores incoming events in a named buffer (ListState) for later
        correlation with match operations.
        """
        buffer_name = store_action.state_name

        lines = [
            f"// Store: buffer events in '{buffer_name}' for later matching",
            f"// Note: Actual buffering implemented in KeyedProcessFunction",
            f"// The buffer '{buffer_name}' will be populated when processing keyed stream",
            f"// See: {self.to_java_class_name(buffer_name)}BufferFunction",
            "",
        ]

        return '\n'.join(lines)

    def _generate_match_action(
        self,
        match_action: 'ast.MatchAction',
        stream_var: str,
        schema_class: str,
        stream_alias: str
    ) -> Tuple[str, str]:
        """
        Generate match action code.

        Feature 3b: match from buffer on [fields]

        Joins incoming stream with previously buffered events based on
        specified correlation fields.
        """
        buffer_name = match_action.state_name
        on_fields = match_action.on_fields
        matched_var = f"matched{self.to_java_class_name(stream_alias)}Stream"
        function_class = f"{self.to_java_class_name(buffer_name)}MatchFunction"

        # Generate key selector for matching
        key_selector = self._generate_match_key_selector(on_fields)

        # Check if we have a stored stream for this buffer
        if buffer_name in self._stored_streams:
            return self._generate_connected_match(
                buffer_name, on_fields, stream_var, schema_class,
                stream_alias, matched_var, function_class, key_selector
            )
        else:
            return self._generate_placeholder_match(
                buffer_name, on_fields, stream_var, schema_class,
                stream_alias, matched_var, function_class, key_selector
            )

    def _generate_match_key_selector(self, on_fields) -> str:
        """Generate key selector lambda for match operation."""
        if len(on_fields) == 1:
            return f"event -> event.get{self._to_pascal_case(on_fields[0])}().toString()"
        else:
            getters = ' + \":\" + '.join(
                f"event.get{self._to_pascal_case(f)}().toString()" for f in on_fields
            )
            return f"event -> {getters}"

    def _generate_connected_match(
        self,
        buffer_name: str,
        on_fields,
        stream_var: str,
        schema_class: str,
        stream_alias: str,
        matched_var: str,
        function_class: str,
        key_selector: str
    ) -> Tuple[str, str]:
        """Generate match with connected streams."""
        buffered_stream_var, buffered_schema = self._stored_streams[buffer_name]
        # Build correlation key array outside f-string
        quoted_fields = ', '.join('"' + f + '"' for f in on_fields)
        correlation_key_array = 'new String[]{' + quoted_fields + '}'

        lines = [
            f"// Match: join with buffered '{buffer_name}' on [{', '.join(on_fields)}]",
            f"KeyedStream<{schema_class}, String> keyed{self.to_java_class_name(stream_alias)} = {stream_var}",
            f"    .keyBy({key_selector});",
            "",
            f"KeyedStream<{buffered_schema}, String> keyed{self.to_java_class_name(buffer_name)} = {buffered_stream_var}",
            f"    .keyBy(event -> event.getCorrelationKey({correlation_key_array}));",
            "",
            f"DataStream<MatchedEvent> {matched_var} = keyed{self.to_java_class_name(stream_alias)}",
            f"    .connect(keyed{self.to_java_class_name(buffer_name)})",
            f"    .process(new {function_class}())",
            f"    .name(\"match-{stream_alias}-from-{buffer_name}\");",
            "",
        ]
        return '\n'.join(lines), matched_var

    def _generate_placeholder_match(
        self,
        buffer_name: str,
        on_fields,
        stream_var: str,
        schema_class: str,
        stream_alias: str,
        matched_var: str,
        function_class: str,
        key_selector: str
    ) -> Tuple[str, str]:
        """Generate placeholder match when buffer not yet defined."""
        lines = [
            f"// Match: join with buffered '{buffer_name}' on [{', '.join(on_fields)}]",
            f"// Note: Buffer '{buffer_name}' must be defined earlier in the pipeline",
            f"KeyedStream<{schema_class}, String> keyed{self.to_java_class_name(stream_alias)} = {stream_var}",
            f"    .keyBy({key_selector});",
            "",
            f"// Connect with buffered stream and process matches",
            f"DataStream<MatchedEvent> {matched_var} = keyed{self.to_java_class_name(stream_alias)}",
            f"    .process(new {function_class}())",
            f"    .name(\"match-{stream_alias}-from-{buffer_name}\");",
            "",
        ]
        return '\n'.join(lines), matched_var

    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
