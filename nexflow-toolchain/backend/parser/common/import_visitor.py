"""
Import Visitor Mixin

Common mixin for parsing import statements across all DSL levels (L1-L4).
"""

from typing import List
from backend.ast.common import ImportStatement


class ImportVisitorMixin:
    """Mixin for parsing import statements.

    This mixin provides visitImportStatement and visitImportPath methods
    that work with any DSL grammar that includes the import rules.
    """

    def visitImportStatement(self, ctx) -> ImportStatement:
        """Parse an import statement.

        Grammar: importStatement: IMPORT importPath ;
        """
        path = self.visitImportPath(ctx.importPath())

        # Get source location
        line = ctx.start.line if ctx.start else 0
        column = ctx.start.column if ctx.start else 0

        return ImportStatement(
            path=path,
            line=line,
            column=column
        )

    def visitImportPath(self, ctx) -> str:
        """Parse an import path.

        Grammar: importPath: (DOT | DOTDOT | SLASH | IDENTIFIER | MINUS)+ ;

        Returns the full path as a string (e.g., "../shared/Currency.schema")
        """
        # Get the raw text of the import path
        return ctx.getText()

    def _collect_imports(self, ctx) -> List[ImportStatement]:
        """Collect all import statements from a program context.

        Args:
            ctx: The program context (must have importStatement children)

        Returns:
            List of ImportStatement AST nodes
        """
        imports = []

        # Check if the context has importStatement method
        if hasattr(ctx, 'importStatement'):
            import_ctxs = ctx.importStatement()
            if import_ctxs:
                # Handle both single and multiple returns
                if not isinstance(import_ctxs, list):
                    import_ctxs = [import_ctxs]
                for import_ctx in import_ctxs:
                    imports.append(self.visitImportStatement(import_ctx))

        return imports
