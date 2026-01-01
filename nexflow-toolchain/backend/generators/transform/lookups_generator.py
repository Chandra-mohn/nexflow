# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Lookups Generator Mixin

Generates Java code for L3 Transform lookups blocks.
Provides access to external lookup tables/services within transform logic.

COVENANT REFERENCE: See docs/COVENANT-Code-Generation-Principles.md
─────────────────────────────────────────────────────────────────────
L3 Lookups Block Features:
- lookup references (name: lookup_source)
- async lookup service integration
- lookup result caching
- null-safe lookup access
─────────────────────────────────────────────────────────────────────
"""

from typing import Set

from backend.ast import transform_ast as ast


class LookupsGeneratorMixin:
    """
    Mixin for generating Java lookup service integration code.

    Generates:
    - Lookup service field declarations
    - Lookup initialization in open() method
    - Lookup accessor methods
    - Null-safe lookup result access
    """

    def generate_lookups_declarations(self, lookups: ast.LookupsBlock) -> str:
        """Generate lookup service field declarations.

        Example output:
            private transient LookupService<CustomerProfile> customerLookup;
            private transient LookupService<Account> accountLookup;
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = [
            "    // Lookup service declarations",
        ]

        for lookup_ref in lookups.lookups:
            field_name = self.to_camel_case(lookup_ref.name) + "Lookup"
            source_type = self.to_pascal_case(lookup_ref.lookup_source)
            lines.append(
                f"    private transient LookupService<{source_type}Result> {field_name};"
            )

        lines.append("")
        return '\n'.join(lines)

    def generate_lookups_init(self, lookups: ast.LookupsBlock) -> str:
        """Generate lookup service initialization code for open() method.

        Example output:
            customerLookup = LookupServiceFactory.create("customer_profile_lookup");
            accountLookup = LookupServiceFactory.create("account_lookup");
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = [
            "        // Initialize lookup services",
        ]

        for lookup_ref in lookups.lookups:
            field_name = self.to_camel_case(lookup_ref.name) + "Lookup"
            lines.append(
                f'        {field_name} = LookupServiceFactory.create("{lookup_ref.lookup_source}");'
            )

        lines.append("")
        return '\n'.join(lines)

    def generate_lookup_accessor_methods(self, lookups: ast.LookupsBlock) -> str:
        """Generate accessor methods for each lookup.

        Example output:
            protected CustomerProfileResult lookupCustomer(Object key) throws Exception {
                return customerLookup.lookup(key);
            }
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = []

        for lookup_ref in lookups.lookups:
            field_name = self.to_camel_case(lookup_ref.name) + "Lookup"
            method_name = "lookup" + self.to_pascal_case(lookup_ref.name)
            source_type = self.to_pascal_case(lookup_ref.lookup_source)
            result_type = f"{source_type}Result"

            lines.extend([
                f"    /**",
                f"     * Lookup {lookup_ref.name} from {lookup_ref.lookup_source}.",
                f"     * @param key The lookup key",
                f"     * @return The lookup result or null if not found",
                f"     */",
                f"    protected {result_type} {method_name}(Object key) throws Exception {{",
                f"        if (key == null) {{",
                f"            return null;",
                f"        }}",
                f"        return {field_name}.lookup(key);",
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def generate_lookups_object_field(self, lookups: ast.LookupsBlock) -> str:
        """Generate a 'lookups' object field for DSL-style access.

        This allows transform code to use lookups.customer.name syntax.

        Example output:
            private final LookupsAccessor lookups = new LookupsAccessor();
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = [
            "    // Lookups accessor for DSL-style access (lookups.name.field)",
            "    private final LookupsAccessor lookups = new LookupsAccessor();",
            "",
        ]

        return '\n'.join(lines)

    def generate_lookups_accessor_class(self, lookups: ast.LookupsBlock) -> str:
        """Generate inner class for DSL-style lookups access.

        Example output:
            private class LookupsAccessor {
                public CustomerProfileResult getCustomer() throws Exception {
                    return customerLookup.lookup(currentKey);
                }
            }
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = [
            "    /**",
            "     * Accessor class for DSL-style lookups access.",
            "     * Enables syntax like: lookups.customer.name",
            "     */",
            "    private class LookupsAccessor {",
        ]

        for lookup_ref in lookups.lookups:
            field_name = self.to_camel_case(lookup_ref.name) + "Lookup"
            getter_name = "get" + self.to_pascal_case(lookup_ref.name)
            source_type = self.to_pascal_case(lookup_ref.lookup_source)
            result_type = f"{source_type}Result"

            lines.extend([
                f"        public {result_type} {getter_name}() throws Exception {{",
                f"            return {field_name}.lookup(currentKey);",
                f"        }}",
                "",
            ])

        lines.append("    }")
        lines.append("")

        return '\n'.join(lines)

    def generate_async_lookup_methods(self, lookups: ast.LookupsBlock) -> str:
        """Generate async lookup methods using CompletableFuture.

        For high-throughput scenarios where async lookup is preferred.
        """
        if not lookups or not lookups.lookups:
            return ""

        lines = []

        for lookup_ref in lookups.lookups:
            field_name = self.to_camel_case(lookup_ref.name) + "Lookup"
            method_name = "lookup" + self.to_pascal_case(lookup_ref.name) + "Async"
            source_type = self.to_pascal_case(lookup_ref.lookup_source)
            result_type = f"{source_type}Result"

            lines.extend([
                f"    /**",
                f"     * Async lookup for {lookup_ref.name} from {lookup_ref.lookup_source}.",
                f"     * @param key The lookup key",
                f"     * @return CompletableFuture with the lookup result",
                f"     */",
                f"    protected CompletableFuture<{result_type}> {method_name}(Object key) {{",
                f"        if (key == null) {{",
                f"            return CompletableFuture.completedFuture(null);",
                f"        }}",
                f"        return {field_name}.lookupAsync(key);",
                f"    }}",
                "",
            ])

        return '\n'.join(lines)

    def get_lookups_imports(self) -> Set[str]:
        """Get required imports for lookups generation."""
        return {
            'com.nexflow.lookup.LookupService',
            'com.nexflow.lookup.LookupServiceFactory',
            'java.util.concurrent.CompletableFuture',
        }
