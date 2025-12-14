# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Build Command Implementation

Full pipeline: parse → validate → generate → verify (optional).

L6 INTEGRATION:
When .infra files are present, uses L6 MasterCompiler for infrastructure-aware
compilation that resolves logical stream names to physical Kafka topics and
generates MongoDB async sinks for persist clauses.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from ..project import Project
from .types import BuildResult


def build_project(project: Project, target: str, output: Optional[str],
                  dry_run: bool, verbose: bool, verify: bool = False) -> BuildResult:
    """
    Build project - full pipeline: parse → validate → generate.

    If .infra files are present, uses L6 MasterCompiler for infrastructure-aware
    code generation. Otherwise uses the standard pipeline.
    """
    from ...parser import parse as parse_dsl, PARSERS
    from ..project import DSL_EXTENSIONS

    # Check if we should use L6 MasterCompiler (when .infra files exist)
    infra_files = list(project.src_dir.rglob("*.infra"))
    if infra_files and not dry_run:
        return _build_with_l6_compiler(project, target, output, verbose, verify)

    result = BuildResult(success=True)
    all_files = project.get_all_source_files()

    # Determine targets to build
    targets_to_build = [target] if target != "all" else project.targets

    # Phase 1: Parse and validate all DSL files
    parsed_asts: Dict[str, Dict[Path, Any]] = {lang: {} for lang in DSL_EXTENSIONS.values()}

    for lang, files in all_files.items():
        if lang not in PARSERS:
            if files and verbose:
                print(f"  Parser for '{lang}' not yet implemented, skipping {len(files)} files")
            continue

        for file_path in files:
            if verbose:
                print(f"  Parsing {file_path.relative_to(project.root_dir)}...")

            try:
                content = file_path.read_text()
                parse_result = parse_dsl(content, lang)

                if not parse_result.success:
                    for error in parse_result.errors:
                        loc = f"{file_path}:{error.location.line}" if error.location else str(file_path)
                        result.errors.append(f"{loc}: {error.message}")
                    result.success = False
                else:
                    parsed_asts[lang][file_path] = parse_result.ast

            except Exception as e:
                result.errors.append(f"{file_path}: {e}")
                result.success = False

    if not result.success:
        return result

    # Phase 2: Semantic validation (cross-file references, imports)
    if verbose:
        print("  Running semantic validation...")

    from ...validators import validate_project_asts

    validation_result = validate_project_asts(parsed_asts, verbose, return_context=True)

    # Add validation errors to result
    for error in validation_result.errors:
        result.errors.append(str(error))

    # Add warnings (don't fail build)
    for warning in validation_result.warnings:
        if verbose:
            print(f"  ⚠ {warning}")

    if not validation_result.success:
        result.success = False
        return result

    if verbose:
        print(f"  ✓ Validation passed ({validation_result.warning_count} warnings)")

    # Store context for type flow in code generation
    validation_context = getattr(validation_result, 'context', None)

    # Phase 3: Code generation
    if dry_run:
        # Just show what would be generated
        for target_name in targets_to_build:
            output_path = Path(output) if output else project.get_output_path(target_name)
            for lang, asts in parsed_asts.items():
                for file_path, ast in asts.items():
                    # Generate expected output file names
                    rel_path = file_path.relative_to(project.root_dir)
                    gen_file = output_path / f"{rel_path.stem}_{target_name}.java"
                    result.files.append(str(gen_file))
    else:
        # Actually generate code
        for target_name in targets_to_build:
            output_path = Path(output) if output else project.get_output_path(target_name)
            output_path.mkdir(parents=True, exist_ok=True)

            gen_result = generate_code(
                parsed_asts, target_name, output_path, project, verbose,
                validation_context=validation_context
            )
            result.files.extend(gen_result.files)
            result.errors.extend(gen_result.errors)
            if not gen_result.success:
                result.success = False
                return result

            # Generate pom.xml for Maven builds
            if gen_result.files:  # Only if we generated code
                pom_result = generate_pom_file(output_path, project, target_name, verbose)
                if pom_result:
                    result.files.append(pom_result)

            # Phase 4: Maven verification (optional)
            if verify and result.success:
                if verbose:
                    print("  Running Maven compilation verification...")
                verify_result = verify_maven_compilation(output_path, verbose)
                result.errors.extend(verify_result.errors)
                if not verify_result.success:
                    result.success = False

    return result


def generate_code(asts: Dict[str, Dict[Path, Any]], target: str,
                  output_path: Path, project: Project, verbose: bool,
                  validation_context: Optional[Any] = None) -> BuildResult:
    """
    Generate code for a specific target using actual generators.

    Args:
        asts: Parsed ASTs organized by DSL type
        target: Target runtime (flink, spark)
        output_path: Output directory for generated code
        project: Project configuration
        verbose: Enable verbose output
        validation_context: Cross-layer context for type flow resolution

    Returns:
        BuildResult with generated files and any errors
    """
    from ...generators import get_generator, GeneratorConfig, RuntimeGenerator

    result = BuildResult(success=True)

    # Create generator config from project settings
    package_prefix = project.get_package_prefix(target)

    # Generate L0 Runtime Library (once per project)
    runtime_config = GeneratorConfig(
        package_prefix=package_prefix,
        output_dir=output_path,
        validation_context=validation_context,
    )
    runtime_gen = RuntimeGenerator(runtime_config)
    try:
        runtime_result = runtime_gen.generate()
        for gen_file in runtime_result.files:
            full_path = output_path / gen_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(gen_file.content)
            result.files.append(str(full_path))
            if verbose:
                print(f"    → {gen_file.path} (Runtime Library)")
    except Exception as e:
        result.errors.append(f"Runtime library generation failed: {e}")
        result.success = False
        return result

    for lang, file_asts in asts.items():
        if not file_asts:
            continue

        # Create config for this DSL type with cross-layer context
        config = GeneratorConfig(
            package_prefix=package_prefix,
            output_dir=output_path,
            validation_context=validation_context,
        )

        # Get generator for this DSL type
        generator = get_generator(lang, config)
        if not generator:
            if verbose:
                print(f"  No generator for '{lang}', skipping...")
            continue

        for file_path, ast in file_asts.items():
            if ast is None:
                continue

            if verbose:
                print(f"  Generating code for {file_path.name}...")

            try:
                # Generate code using the actual generator
                gen_result = generator.generate(ast)

                # Write generated files to disk
                for gen_file in gen_result.files:
                    full_path = output_path / gen_file.path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(gen_file.content)
                    result.files.append(str(full_path))

                    if verbose:
                        print(f"    → {gen_file.path}")

            except Exception as e:
                error_msg = f"{file_path.name}: Generation failed - {e}"
                result.errors.append(error_msg)
                result.success = False
                if verbose:
                    print(f"    ✗ Error: {e}")

    return result


def generate_pom_file(output_path: Path, project: Project, target: str,
                      verbose: bool) -> Optional[str]:
    """
    Generate pom.xml for Maven compilation of generated code.

    Args:
        output_path: Output directory containing generated code
        project: Project configuration
        target: Target runtime (flink, spark)
        verbose: Enable verbose output

    Returns:
        Path to generated pom.xml or None if generation failed
    """
    from ...generators import write_pom

    try:
        # Get project settings
        package_prefix = project.get_package_prefix(target)
        project_name = project.name
        java_version = project.get_java_version(target)

        # Write pom.xml
        pom_path = write_pom(
            output_dir=output_path,
            group_id=package_prefix,
            artifact_id=f"{project_name}-{target}",
            version=project.version,
            flink_version="1.18.1",
            java_version=java_version,
            voltage_enabled=True,
            project_name=f"Nexflow {project_name} ({target})",
        )

        if verbose:
            print(f"    → pom.xml")

        return str(pom_path)

    except Exception as e:
        if verbose:
            print(f"    ⚠ Warning: Failed to generate pom.xml: {e}")
        return None


def verify_maven_compilation(output_path: Path, verbose: bool) -> BuildResult:
    """
    Verify generated code compiles with Maven.

    Args:
        output_path: Directory containing pom.xml and generated code
        verbose: Enable verbose output

    Returns:
        BuildResult with compilation status and any errors
    """
    result = BuildResult(success=True)

    # Check if Maven is available
    mvn_cmd = shutil.which("mvn")
    if not mvn_cmd:
        result.errors.append("Maven (mvn) not found in PATH. Install Maven or skip verification.")
        result.success = False
        return result

    # Check if pom.xml exists
    pom_path = output_path / "pom.xml"
    if not pom_path.exists():
        result.errors.append(f"pom.xml not found in {output_path}")
        result.success = False
        return result

    try:
        # Run Maven compile
        cmd = [mvn_cmd, "compile", "-f", str(pom_path), "-q"]
        if verbose:
            cmd.remove("-q")  # Show Maven output in verbose mode

        proc = subprocess.run(
            cmd,
            cwd=str(output_path),
            capture_output=not verbose,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if proc.returncode != 0:
            result.success = False
            if proc.stderr:
                # Extract key compilation errors
                errors = extract_compilation_errors(proc.stderr)
                result.errors.extend(errors)
            elif proc.stdout:
                errors = extract_compilation_errors(proc.stdout)
                result.errors.extend(errors)

            if not result.errors:
                result.errors.append("Maven compilation failed (run with --verbose for details)")
        else:
            if verbose:
                print("  ✓ Maven compilation successful")

    except subprocess.TimeoutExpired:
        result.errors.append("Maven compilation timed out (5 minutes)")
        result.success = False
    except Exception as e:
        result.errors.append(f"Maven execution failed: {e}")
        result.success = False

    return result


def extract_compilation_errors(output: str) -> list:
    """Extract compilation errors from Maven output."""
    errors = []
    lines = output.split('\n')

    for i, line in enumerate(lines):
        # Look for [ERROR] lines with file references
        if '[ERROR]' in line:
            # Skip generic Maven error header lines
            if 'Failed to execute goal' in line:
                continue
            if 'Compilation failure' in line:
                continue
            if 'BUILD FAILURE' in line:
                continue

            # Extract meaningful error messages
            error_line = line.replace('[ERROR]', '').strip()
            if error_line and '.java' in error_line:
                errors.append(error_line)

    # Limit to first 10 errors
    return errors[:10]


def _build_with_l6_compiler(
    project: Project,
    target: str,
    output: Optional[str],
    verbose: bool,
    verify: bool
) -> BuildResult:
    """
    Build using L6 MasterCompiler for infrastructure-aware compilation.

    This is used when .infra files are present in the project.
    The L6 compiler properly orders compilation phases and passes
    infrastructure bindings to the L1 FlowGenerator.
    """
    from ...compiler import MasterCompiler, CompilationPhase

    result = BuildResult(success=True)

    # Determine output path
    output_path = Path(output) if output else project.get_output_path(target)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get package prefix for target
    package_prefix = project.get_package_prefix(target)

    # Determine environment from project config or target
    environment = getattr(project, 'environment', None) or target

    if verbose:
        print(f"  Using L6 MasterCompiler (infrastructure-aware compilation)")
        print(f"  Environment: {environment}")

    # Create and run L6 compiler
    compiler = MasterCompiler(
        src_dir=project.src_dir,
        output_dir=output_path,
        package_prefix=package_prefix,
        environment=environment,
        verbose=verbose,
    )

    compilation_result = compiler.compile()

    # Convert L6 result to BuildResult
    result.success = compilation_result.success
    result.files = compilation_result.generated_files
    result.errors = compilation_result.errors

    # Show phase summary in verbose mode
    if verbose:
        print("\n  Compilation Summary:")
        for phase, layer_result in compilation_result.layers.items():
            status = "✓" if layer_result.success else "✗"
            print(f"    {status} {phase.name}: {layer_result.files_parsed} parsed, "
                  f"{layer_result.files_generated} generated")

    # Generate pom.xml
    if result.success and result.files:
        pom_result = generate_pom_file(output_path, project, target, verbose)
        if pom_result:
            result.files.append(pom_result)

    # Maven verification
    if verify and result.success:
        if verbose:
            print("  Running Maven compilation verification...")
        verify_result = verify_maven_compilation(output_path, verbose)
        result.errors.extend(verify_result.errors)
        if not verify_result.success:
            result.success = False

    return result
