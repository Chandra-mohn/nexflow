# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
L6 Master Compiler

Orchestrates the full Nexflow compilation pipeline with infrastructure bindings.

COMPILATION ORDER:
1. L5 Infrastructure - Parse .infra files, create BindingResolver
2. L2 Schema         - Parse .schema files, generate POJOs
3. L3 Transform      - Parse .xform files, generate transform functions
4. L4 Rules          - Parse .rules files, generate decision logic
5. L1 Process        - Parse .proc files, generate Flink jobs with L5 bindings

The L5 InfraConfig is passed to L1 ProcGenerator for infrastructure-aware generation:
- Source topics resolved from L5 streams
- Sink topics resolved from L5 streams
- MongoDB async sinks generated for persist clauses
- Parallelism and resource configs from L5 resources

IMPORT RESOLUTION (v0.7.0+):
- Each DSL file can declare imports to other DSL files
- ImportResolver resolves import paths and detects circular dependencies
- Files are processed in topological order (dependencies first)
- Resolved imports are passed to generators for type resolution
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Any

from backend.ast.infra import InfraConfig
from backend.ast.common import ImportStatement
from backend.parser.infra import InfraParser, InfraParseError
from backend.generators.infra import BindingResolver
from backend.generators.base import GeneratorConfig, GenerationResult
from backend.resolver.import_resolver import ImportResolver, ImportError as ImportResolverError


class CompilationPhase(Enum):
    """Compilation phases in order."""
    INFRA = auto()      # L5: Infrastructure binding
    SCHEMA = auto()     # L2: Schema/Type definitions
    TRANSFORM = auto()  # L3: Transform functions
    RULES = auto()      # L4: Decision rules
    PROC = auto()       # L1: Process definitions


@dataclass
class LayerResult:
    """Result of compiling a single layer."""
    phase: CompilationPhase
    success: bool = True
    files_parsed: int = 0
    files_generated: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generation_result: Optional[GenerationResult] = None


@dataclass
class CompilationResult:
    """Result of the full compilation pipeline."""
    success: bool = True
    layers: Dict[CompilationPhase, LayerResult] = field(default_factory=dict)
    total_files_generated: int = 0
    generated_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    infra_config: Optional[InfraConfig] = None
    binding_resolver: Optional[BindingResolver] = None

    def add_layer_result(self, result: LayerResult):
        """Add a layer result to the compilation."""
        self.layers[result.phase] = result
        if not result.success:
            self.success = False
        self.errors.extend(result.errors)
        self.warnings.extend(result.warnings)
        self.total_files_generated += result.files_generated
        if result.generation_result:
            for gen_file in result.generation_result.files:
                self.generated_files.append(str(gen_file.path))


class MasterCompiler:
    """
    L6 Master Compiler - Orchestrates the Nexflow compilation pipeline.

    Usage:
        compiler = MasterCompiler(
            src_dir=Path("src"),
            output_dir=Path("generated"),
            package_prefix="com.example.proc",
            environment="production"  # Optional: selects .infra file
        )
        result = compiler.compile()

        if result.success:
            print(f"Generated {result.total_files_generated} files")
        else:
            for error in result.errors:
                print(f"Error: {error}")
    """

    def __init__(
        self,
        src_dir: Path,
        output_dir: Path,
        package_prefix: str,
        environment: Optional[str] = None,
        infra_file: Optional[Path] = None,
        verbose: bool = False,
    ):
        """
        Initialize the master compiler.

        Args:
            src_dir: Root directory containing DSL source files
            output_dir: Target directory for generated code
            package_prefix: Java package prefix for generated classes
            environment: Environment name (dev, staging, prod) - selects .infra file
            infra_file: Explicit path to .infra file (overrides environment detection)
            verbose: Enable verbose output
        """
        self.src_dir = src_dir
        self.output_dir = output_dir
        self.package_prefix = package_prefix
        self.environment = environment
        self.infra_file = infra_file
        self.verbose = verbose

        # State managed during compilation
        self._infra_config: Optional[InfraConfig] = None
        self._binding_resolver: Optional[BindingResolver] = None
        self._validation_context: Optional[Any] = None
        self._import_resolver: Optional[ImportResolver] = None
        # Cache of parsed ASTs keyed by file path (for import resolution)
        self._parsed_asts: Dict[Path, Any] = {}

    def compile(self) -> CompilationResult:
        """
        Execute the full compilation pipeline.

        Returns:
            CompilationResult with all generated files and any errors
        """
        result = CompilationResult()

        # Initialize import resolver for dependency tracking
        self._import_resolver = ImportResolver(self.src_dir)

        # Phase 1: L5 Infrastructure
        infra_result = self._compile_infrastructure()
        result.add_layer_result(infra_result)
        if not infra_result.success:
            return result

        result.infra_config = self._infra_config
        result.binding_resolver = self._binding_resolver

        # Phase 2: L2 Schema
        schema_result = self._compile_schemas()
        result.add_layer_result(schema_result)

        # Phase 3: L3 Transform
        transform_result = self._compile_transforms()
        result.add_layer_result(transform_result)

        # Phase 4: L4 Rules
        rules_result = self._compile_rules()
        result.add_layer_result(rules_result)

        # Phase 5: L1 Process (with infrastructure bindings)
        proc_result = self._compile_procs()
        result.add_layer_result(proc_result)

        return result

    def _compile_infrastructure(self) -> LayerResult:
        """Phase 1: Parse L5 infrastructure configuration."""
        result = LayerResult(phase=CompilationPhase.INFRA)

        # Find .infra file
        infra_path = self._find_infra_file()

        if infra_path is None:
            # No infrastructure config - use defaults (development mode)
            if self.verbose:
                print("  No .infra file found - using default configuration")
            self._infra_config = None
            self._binding_resolver = BindingResolver(None)
            result.warnings.append("No infrastructure config found - using development defaults")
            return result

        if self.verbose:
            print(f"  Parsing infrastructure config: {infra_path.name}")

        try:
            parser = InfraParser(resolve_env_vars=True)
            self._infra_config = parser.parse_file(infra_path)
            self._binding_resolver = BindingResolver(self._infra_config)
            result.files_parsed = 1

            if self.verbose:
                env = self._infra_config.environment or "unknown"
                streams = len(self._infra_config.streams)
                persistence = len(self._infra_config.persistence)
                print(f"    Environment: {env}")
                print(f"    Streams: {streams}, Persistence targets: {persistence}")

        except InfraParseError as e:
            result.success = False
            result.errors.append(f"Infrastructure parse error: {e}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to load infrastructure config: {e}")

        return result

    def _find_infra_file(self) -> Optional[Path]:
        """Find the appropriate .infra file."""
        # 1. Explicit file takes precedence
        if self.infra_file:
            if self.infra_file.exists():
                return self.infra_file
            return None

        # 2. Look in src/infra directory
        infra_dir = self.src_dir / "infra"
        if not infra_dir.exists():
            # Also check root level
            infra_dir = self.src_dir

        # 3. Environment-specific file
        if self.environment:
            env_file = infra_dir / f"{self.environment}.infra"
            if env_file.exists():
                return env_file

        # 4. Default files in priority order
        for name in ["default.infra", "local.infra", "dev.infra"]:
            default_file = infra_dir / name
            if default_file.exists():
                return default_file

        # 5. Any .infra file
        infra_files = list(infra_dir.glob("*.infra"))
        if infra_files:
            return infra_files[0]

        return None

    def _compile_schemas(self) -> LayerResult:
        """Phase 2: Parse and generate L2 schemas."""
        return self._compile_layer(
            phase=CompilationPhase.SCHEMA,
            extensions=[".schema"],
            generator_type="schema"
        )

    def _compile_transforms(self) -> LayerResult:
        """Phase 3: Parse and generate L3 transforms."""
        return self._compile_layer(
            phase=CompilationPhase.TRANSFORM,
            extensions=[".xform", ".transform"],
            generator_type="transform"
        )

    def _compile_rules(self) -> LayerResult:
        """Phase 4: Parse and generate L4 rules."""
        return self._compile_layer(
            phase=CompilationPhase.RULES,
            extensions=[".rules"],
            generator_type="rules"
        )

    def _compile_procs(self) -> LayerResult:
        """Phase 5: Parse and generate L1 processes with infrastructure bindings."""
        return self._compile_layer(
            phase=CompilationPhase.PROC,
            extensions=[".proc"],
            generator_type="proc",
            with_infrastructure=True
        )

    def _compile_layer(
        self,
        phase: CompilationPhase,
        extensions: List[str],
        generator_type: str,
        with_infrastructure: bool = False
    ) -> LayerResult:
        """Compile a single layer (schema, transform, rules, or proc)."""
        from backend.parser import parse as parse_dsl
        from backend.generators import get_generator

        result = LayerResult(phase=phase)

        # Find all files with matching extensions
        files = []
        for ext in extensions:
            files.extend(self.src_dir.rglob(f"*{ext}"))

        if not files:
            if self.verbose:
                print(f"  No {generator_type} files found")
            return result

        # Parse files
        parsed_asts = {}
        lang = generator_type

        for file_path in files:
            if self.verbose:
                print(f"  Parsing {file_path.relative_to(self.src_dir)}...")

            try:
                content = file_path.read_text()
                parse_result = parse_dsl(content, lang)

                if not parse_result.success:
                    for error in parse_result.errors:
                        loc = f"{file_path}:{error.location.line}" if error.location else str(file_path)
                        result.errors.append(f"{loc}: {error.message}")
                    result.success = False
                else:
                    parsed_asts[file_path] = parse_result.ast
                    self._parsed_asts[file_path] = parse_result.ast  # Cache for import resolution
                    result.files_parsed += 1

                    # Process imports from this file (v0.7.0+)
                    self._process_file_imports(file_path, parse_result.ast, result)

            except Exception as e:
                result.errors.append(f"{file_path}: {e}")
                result.success = False

        if not result.success or not parsed_asts:
            return result

        # Generate code
        config = GeneratorConfig(
            package_prefix=self.package_prefix,
            output_dir=self.output_dir,
            validation_context=self._validation_context,
        )

        # Get generator - for procs, pass infrastructure config
        if with_infrastructure:
            generator = self._get_proc_generator(config)
        else:
            generator = get_generator(generator_type, config)

        if not generator:
            result.warnings.append(f"No generator available for {generator_type}")
            return result

        # Generate code for each AST in topological order (dependencies first)
        all_files = GenerationResult(success=True)

        # Get topological order from import resolver if available
        if self._import_resolver:
            topo_order = self._import_resolver.get_processing_order()
            # Filter to only include files in parsed_asts and maintain order
            ordered_files = [f for f in topo_order if f in parsed_asts]
            # Add any files not in the topological order (no imports)
            remaining = [f for f in parsed_asts.keys() if f not in ordered_files]
            ordered_files.extend(remaining)
        else:
            ordered_files = list(parsed_asts.keys())

        for file_path in ordered_files:
            ast = parsed_asts.get(file_path)
            if ast is None:
                continue

            if self.verbose:
                print(f"  Generating {generator_type} code for {file_path.name}...")

            try:
                gen_result = generator.generate(ast)
                for gen_file in gen_result.files:
                    all_files.add_file(gen_file.path, gen_file.content, gen_file.file_type)
                    result.files_generated += 1

            except Exception as e:
                result.errors.append(f"{file_path.name}: Generation failed - {e}")
                result.success = False

        # Write generated files to disk
        for gen_file in all_files.files:
            full_path = self.output_dir / gen_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(gen_file.content)

            if self.verbose:
                print(f"    -> {gen_file.path}")

        result.generation_result = all_files
        return result

    def _process_file_imports(self, file_path: Path, ast: Any, result: LayerResult) -> None:
        """Process and resolve imports from a parsed AST file.

        Extracts import statements from the AST and uses ImportResolver to:
        - Resolve relative/absolute import paths
        - Detect circular dependencies
        - Build dependency graph for processing order

        Args:
            file_path: Path to the source file
            ast: Parsed AST that may contain imports
            result: LayerResult to add any errors to
        """
        # Get imports from AST (different AST types store imports differently)
        imports: List[ImportStatement] = []

        # Check for imports attribute (Program-level ASTs)
        if hasattr(ast, 'imports') and ast.imports:
            imports = ast.imports

        if not imports:
            return

        if self._import_resolver is None:
            return

        # Resolve each import
        for import_stmt in imports:
            try:
                resolved_path = self._import_resolver.resolve(import_stmt.path, file_path)
                import_stmt.resolved_path = resolved_path
                import_stmt.source_file = file_path

                # Record dependency in the graph
                self._import_resolver.graph.add_dependency(file_path, resolved_path)

                if self.verbose:
                    rel_resolved = resolved_path.relative_to(self.src_dir) if resolved_path.is_relative_to(self.src_dir) else resolved_path
                    print(f"    Import resolved: {import_stmt.path} -> {rel_resolved}")

            except ImportResolverError as e:
                result.errors.append(f"{file_path}:{import_stmt.line}: {e}")
                result.success = False
            except Exception as e:
                result.warnings.append(f"{file_path}:{import_stmt.line}: Import warning - {e}")

    def _get_proc_generator(self, config: GeneratorConfig):
        """Get ProcGenerator with infrastructure bindings."""
        from backend.generators.proc import ProcGenerator

        return ProcGenerator(config, infra_config=self._infra_config)

    def validate_bindings(self) -> List[str]:
        """
        Validate that all L1 stream/persistence references have L5 bindings.

        Should be called after parsing L1 but before code generation.

        Extracts:
        - Stream sources from ReceiveDecl.source
        - Stream sinks from EmitDecl.target
        - Persistence targets from PersistDecl.target

        Returns:
            List of validation error messages (empty if valid)
        """
        if not self._binding_resolver or not self._binding_resolver.has_config:
            # No config = development mode, all references allowed
            return []

        # Collect all stream and persistence references from L1 ASTs
        stream_refs = set()
        persistence_refs = set()

        # Extract references from parsed L1 (proc) ASTs
        for file_path, ast in self._parsed_asts.items():
            # Skip non-L1 ASTs (check if it has processes attribute)
            if not hasattr(ast, 'processes'):
                continue

            for process in ast.processes:
                # Extract source stream references from receives
                for receive in process.receives:
                    stream_refs.add(receive.source)

                # Extract sink stream and persistence references from emits
                for emit in process.emits:
                    if hasattr(emit, 'target') and emit.target:
                        stream_refs.add(emit.target)
                    if hasattr(emit, 'persist') and emit.persist and emit.persist.target:
                        persistence_refs.add(emit.persist.target)

                # Extract from completion blocks
                for completion in process.completions:
                    if completion.on_commit and completion.on_commit.target:
                        stream_refs.add(completion.on_commit.target)
                    if completion.on_commit_failure and completion.on_commit_failure.target:
                        stream_refs.add(completion.on_commit_failure.target)

        return self._binding_resolver.validate_bindings(
            list(stream_refs),
            list(persistence_refs)
        )


def compile_project(
    src_dir: Path,
    output_dir: Path,
    package_prefix: str,
    environment: Optional[str] = None,
    verbose: bool = False
) -> CompilationResult:
    """
    Convenience function to compile a Nexflow project.

    Args:
        src_dir: Root directory containing DSL source files
        output_dir: Target directory for generated code
        package_prefix: Java package prefix for generated classes
        environment: Optional environment name for .infra file selection
        verbose: Enable verbose output

    Returns:
        CompilationResult with all generated files and any errors
    """
    compiler = MasterCompiler(
        src_dir=src_dir,
        output_dir=output_dir,
        package_prefix=package_prefix,
        environment=environment,
        verbose=verbose,
    )
    return compiler.compile()
