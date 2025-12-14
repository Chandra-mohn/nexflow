# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Import Resolver

Resolves import paths and detects circular dependencies for DSL files.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from backend.ast.common import ImportStatement


class ImportError(Exception):
    """Base exception for import-related errors."""
    pass


class CircularImportError(ImportError):
    """Raised when a circular import is detected."""

    def __init__(self, cycle: List[Path]):
        self.cycle = cycle
        cycle_str = " -> ".join(str(p) for p in cycle)
        super().__init__(f"Circular import detected: {cycle_str}")


class FileNotFoundImportError(ImportError):
    """Raised when an imported file does not exist."""

    def __init__(self, import_path: str, source_file: Path, resolved_path: Path):
        self.import_path = import_path
        self.source_file = source_file
        self.resolved_path = resolved_path
        super().__init__(
            f"Import not found: '{import_path}' from {source_file}\n"
            f"Resolved to: {resolved_path}"
        )


@dataclass
class ResolvedImport:
    """A fully resolved import with its AST."""
    import_stmt: ImportStatement
    resolved_path: Path
    ast: Optional[Any] = None  # The parsed AST of the imported file
    dsl_type: Optional[str] = None  # 'schema', 'transform', 'flow', 'rules'


@dataclass
class ImportGraph:
    """Tracks import dependencies between files."""
    # Maps file path -> list of files it imports
    dependencies: Dict[Path, List[Path]] = field(default_factory=dict)
    # Maps file path -> list of files that import it
    dependents: Dict[Path, List[Path]] = field(default_factory=dict)
    # All resolved imports
    resolved: Dict[Path, ResolvedImport] = field(default_factory=dict)

    def add_dependency(self, from_file: Path, to_file: Path):
        """Record that from_file imports to_file."""
        if from_file not in self.dependencies:
            self.dependencies[from_file] = []
        if to_file not in self.dependencies[from_file]:
            self.dependencies[from_file].append(to_file)

        if to_file not in self.dependents:
            self.dependents[to_file] = []
        if from_file not in self.dependents[to_file]:
            self.dependents[to_file].append(from_file)

    def get_topological_order(self) -> List[Path]:
        """Return files in topological order (dependencies first)."""
        visited: Set[Path] = set()
        order: List[Path] = []

        def visit(path: Path):
            if path in visited:
                return
            visited.add(path)
            for dep in self.dependencies.get(path, []):
                visit(dep)
            order.append(path)

        for path in self.dependencies:
            visit(path)

        return order


class ImportResolver:
    """Resolves import paths and manages import dependencies.

    Usage:
        resolver = ImportResolver(project_root=Path("/path/to/project"))

        # Resolve a single import
        resolved_path = resolver.resolve("../shared/Currency.schema", from_file)

        # Process all imports from a file
        imports = resolver.process_imports(file_path, import_statements)
    """

    def __init__(self, project_root: Path):
        """Initialize the resolver.

        Args:
            project_root: The root directory for absolute import resolution
        """
        self.project_root = project_root.resolve()
        self.graph = ImportGraph()
        self._resolution_stack: List[Path] = []  # For circular detection
        self._cache: Dict[Path, Any] = {}  # Cache of parsed ASTs

    def resolve(self, import_path: str, from_file: Path) -> Path:
        """Resolve an import path to an absolute file path.

        Args:
            import_path: The import path as written in DSL (e.g., ../shared/Currency.schema)
            from_file: The file containing the import statement

        Returns:
            Absolute resolved path

        Raises:
            FileNotFoundImportError: If the resolved file does not exist
        """
        from_file = from_file.resolve()

        if import_path.startswith('/'):
            # Absolute import - relative to project root
            resolved = self.project_root / import_path.lstrip('/')
        else:
            # Relative import - relative to the importing file's directory
            resolved = (from_file.parent / import_path).resolve()

        # Normalize the path
        resolved = resolved.resolve()

        # Verify file exists
        if not resolved.exists():
            raise FileNotFoundImportError(import_path, from_file, resolved)

        return resolved

    def check_circular(self, from_file: Path, to_file: Path) -> None:
        """Check for circular imports.

        Args:
            from_file: The file doing the importing
            to_file: The file being imported

        Raises:
            CircularImportError: If importing to_file would create a cycle
        """
        if to_file in self._resolution_stack:
            # Found a cycle
            cycle_start = self._resolution_stack.index(to_file)
            cycle = self._resolution_stack[cycle_start:] + [to_file]
            raise CircularImportError(cycle)

    def process_imports(
        self,
        file_path: Path,
        import_statements: List[ImportStatement],
        parser_callback=None
    ) -> List[ResolvedImport]:
        """Process all imports from a file.

        Args:
            file_path: The file containing the imports
            import_statements: List of import statements from the file
            parser_callback: Optional callback to parse imported files
                           Signature: (path: Path, dsl_type: str) -> Any

        Returns:
            List of resolved imports with their ASTs (if parser_callback provided)
        """
        file_path = file_path.resolve()
        resolved_imports: List[ResolvedImport] = []

        # Push current file onto resolution stack
        self._resolution_stack.append(file_path)

        try:
            for import_stmt in import_statements:
                # Resolve the path
                resolved_path = self.resolve(import_stmt.path, file_path)

                # Update import statement with resolved path
                import_stmt.resolved_path = resolved_path
                import_stmt.source_file = file_path

                # Check for circular imports
                self.check_circular(file_path, resolved_path)

                # Record dependency
                self.graph.add_dependency(file_path, resolved_path)

                # Determine DSL type
                dsl_type = import_stmt.dsl_type

                # Parse the imported file if callback provided
                ast = None
                if parser_callback and resolved_path not in self._cache:
                    # Push imported file onto stack for nested resolution
                    self._resolution_stack.append(resolved_path)
                    try:
                        ast = parser_callback(resolved_path, dsl_type)
                        self._cache[resolved_path] = ast
                    finally:
                        self._resolution_stack.pop()
                elif resolved_path in self._cache:
                    ast = self._cache[resolved_path]

                resolved = ResolvedImport(
                    import_stmt=import_stmt,
                    resolved_path=resolved_path,
                    ast=ast,
                    dsl_type=dsl_type
                )
                resolved_imports.append(resolved)
                self.graph.resolved[resolved_path] = resolved

        finally:
            # Pop current file from resolution stack
            self._resolution_stack.pop()

        return resolved_imports

    def get_all_dependencies(self, file_path: Path) -> Set[Path]:
        """Get all transitive dependencies of a file.

        Args:
            file_path: The file to get dependencies for

        Returns:
            Set of all files that this file depends on (directly or transitively)
        """
        file_path = file_path.resolve()
        result: Set[Path] = set()

        def collect(path: Path):
            for dep in self.graph.dependencies.get(path, []):
                if dep not in result:
                    result.add(dep)
                    collect(dep)

        collect(file_path)
        return result

    def get_processing_order(self) -> List[Path]:
        """Get all files in topological order for processing.

        Files with no dependencies come first, then files that depend only
        on already-processed files, etc.

        Returns:
            List of file paths in processing order
        """
        return self.graph.get_topological_order()

    def clear_cache(self):
        """Clear the parsed AST cache."""
        self._cache.clear()
