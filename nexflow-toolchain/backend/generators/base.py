# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Base Generator Module

Provides abstract base class and common utilities for all Nexflow code generators.
Target: Flink/Java code generation using Python f-strings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import os

from backend.generators.common.java_utils import (
    to_camel_case as _to_camel_case,
    to_pascal_case as _to_pascal_case,
    to_snake_case as _to_snake_case,
    to_getter as _to_getter,
    to_setter as _to_setter,
    to_constant as _to_constant,
    get_java_type as _get_java_type,
    duration_to_ms as _duration_to_ms,
    format_duration as _format_duration,
    duration_to_time_call as _duration_to_time_call,
)
from backend.config.org_policy import OrganizationPolicy
from backend.config.policy_validator import ValidationResult


@dataclass
class GeneratorConfig:
    """Configuration for code generators."""

    # Output settings
    output_dir: Path
    package_prefix: str = "com.nexflow.generated"

    # Schema format
    schema_format: str = "avro"  # avro, protobuf, json

    # Flink settings
    flink_version: str = "1.18"
    java_version: str = "17"

    # Voltage/PII settings
    voltage_enabled: bool = True
    voltage_profiles_path: Optional[Path] = None

    # Observability settings
    metrics_enabled: bool = True
    tracing_enabled: bool = True

    # Build settings
    generate_pom: bool = True
    generate_tests: bool = True

    # Cross-layer type resolution context
    # Contains transforms, schemas, and rules for type flow lookup
    validation_context: Optional[Any] = None  # ValidationContext from validators.base

    # Organization policy for serialization governance
    # If None, a permissive policy is used (backward compatibility)
    org_policy: Optional[OrganizationPolicy] = None

    # Callback for policy violations (warnings, info)
    # Called with ValidationResult when policy violations are detected
    violation_handler: Optional[Callable[[ValidationResult], None]] = None

    # Source file path for error messages (usually the .proc file)
    source_file: Optional[Path] = None


@dataclass
class GeneratedFile:
    """Represents a generated file."""
    path: Path
    content: str
    file_type: str  # java, xml, yaml, properties, etc.


@dataclass
class GenerationResult:
    """Result of code generation."""
    success: bool
    files: List[GeneratedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_file(self, path: Path, content: str, file_type: str = "java") -> None:
        """Add a generated file to the result."""
        self.files.append(GeneratedFile(path=path, content=content, file_type=file_type))

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


class BaseGenerator(ABC):
    """
    Abstract base class for all Nexflow code generators.

    Subclasses implement specific generators for:
    - L2 Schema: Java Records (immutable), Avro schemas, serializers
    - L1 Flow: Flink job structure, sources, sinks
    - L3 Transform: MapFunction, ProcessFunction implementations
    - L4 Rules: CEP patterns, rule evaluation logic (uses POJOs for mutability)
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.result = GenerationResult(success=True)

    @abstractmethod
    def generate(self, ast: Any) -> GenerationResult:
        """
        Generate code from the given AST.

        Args:
            ast: The parsed AST (type depends on generator)

        Returns:
            GenerationResult containing generated files and any errors/warnings
        """
        pass

    def write_files(self) -> bool:
        """
        Write all generated files to disk.

        Returns:
            True if all files were written successfully
        """
        if not self.result.success:
            return False

        for gen_file in self.result.files:
            full_path = self.config.output_dir / gen_file.path
            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(gen_file.content)
            except OSError as e:
                self.result.add_error(f"Failed to write {full_path}: {e}")
                return False

        return True

    # =========================================================================
    # Java Code Generation Utilities
    # =========================================================================

    def to_java_class_name(self, name: str) -> str:
        """Convert snake_case to PascalCase for Java class names."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def to_java_field_name(self, name: str) -> str:
        """Convert snake_case to camelCase for Java field names."""
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    def to_java_constant_name(self, name: str) -> str:
        """Convert to UPPER_SNAKE_CASE for Java constants."""
        return name.upper()

    def get_java_type(self, nexflow_type: str) -> str:
        """Map Nexflow base types to Java types.

        Delegates to java_utils.get_java_type() for consistent type mapping.
        """
        return _get_java_type(nexflow_type)

    def get_java_imports_for_type(self, nexflow_type: str) -> List[str]:
        """
        Get required Java imports for a Nexflow type.

        Args:
            nexflow_type: Nexflow type name

        Returns:
            List of import statements
        """
        import_map = {
            'decimal': ['java.math.BigDecimal'],
            'date': ['java.time.LocalDate'],
            'timestamp': ['java.time.Instant'],
            'uuid': ['java.util.UUID'],
        }
        return import_map.get(nexflow_type.lower(), [])

    def get_package_path(self, package: str) -> Path:
        """Convert Java package to directory path."""
        return Path(package.replace('.', os.sep))

    def indent(self, code: str, level: int = 1, indent_str: str = "    ") -> str:
        """Indent a block of code."""
        prefix = indent_str * level
        return '\n'.join(prefix + line if line.strip() else line
                        for line in code.split('\n'))

    # =========================================================================
    # Java Naming Convention Utilities
    # Delegate to java_utils for single source of truth
    # =========================================================================

    def to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase. Delegates to java_utils."""
        return _to_camel_case(name)

    def to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase. Delegates to java_utils."""
        return _to_pascal_case(name)

    def to_getter(self, field_name: str) -> str:
        """Convert field name to getter call. DEPRECATED: Use to_record_accessor()."""
        return _to_getter(field_name)

    def to_record_accessor(self, field_name: str) -> str:
        """Convert field name to Java Record accessor (fieldName())."""
        camel = _to_camel_case(field_name)
        return f"{camel}()" if camel else "()"

    def to_setter(self, field_name: str) -> str:
        """Convert field name to setter name. DEPRECATED: Records are immutable."""
        return _to_setter(field_name)

    def to_with_method(self, field_name: str) -> str:
        """Convert field name to Record withField method name."""
        camel = _to_camel_case(field_name)
        return f"with{camel[0].upper()}{camel[1:]}" if camel else "with"

    # =========================================================================
    # File Header Generation
    # =========================================================================

    def generate_java_header(self, class_name: str, description: str = "") -> str:
        """Generate standard Java file header."""
        desc = f" * {description}\n *\n" if description else ""
        return f'''/**
 * {class_name}
 *
{desc} * AUTO-GENERATED by Nexflow Code Generator
 * DO NOT EDIT - Changes will be overwritten
 *
 * Generator: {self.__class__.__name__}
 */
'''

    def generate_package_declaration(self, package: str) -> str:
        """Generate Java package declaration."""
        return f"package {package};\n"

    def generate_imports(self, imports: List[str]) -> str:
        """Generate sorted, deduplicated import statements."""
        unique_imports = sorted(set(imports))

        # Group imports: java.*, javax.*, org.*, com.*, others
        java_imports = [i for i in unique_imports if i.startswith('java.')]
        javax_imports = [i for i in unique_imports if i.startswith('javax.')]
        org_imports = [i for i in unique_imports if i.startswith('org.')]
        com_imports = [i for i in unique_imports if i.startswith('com.')]
        other_imports = [i for i in unique_imports
                        if not any(i.startswith(p) for p in ['java.', 'javax.', 'org.', 'com.'])]

        sections = []
        for group in [java_imports, javax_imports, org_imports, com_imports, other_imports]:
            if group:
                sections.append('\n'.join(f"import {imp};" for imp in group))

        return '\n\n'.join(sections) + '\n' if sections else ''

    # =========================================================================
    # Duration and Size Conversion Utilities
    # =========================================================================

    def duration_to_ms(self, duration) -> int:
        """Convert a duration object to milliseconds. Delegates to java_utils."""
        return _duration_to_ms(duration)

    def format_duration(self, duration) -> str:
        """Format duration for comments/display. Delegates to java_utils."""
        return _format_duration(duration)

    def duration_to_time_call(self, duration) -> str:
        """Convert duration to Flink Time.xxx() call. Delegates to java_utils."""
        return _duration_to_time_call(duration)

    def size_to_bytes(self, size) -> int:
        """Convert a size object to bytes."""
        if size is None:
            return 0

        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024
        }
        unit = getattr(size, 'unit', 'B')
        value = getattr(size, 'value', 0)
        return value * multipliers.get(unit, 1)

    def to_java_constant(self, name: str) -> str:
        """Convert name to UPPER_SNAKE_CASE. Delegates to java_utils."""
        return _to_constant(name)
