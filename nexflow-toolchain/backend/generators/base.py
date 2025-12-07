"""
Base Generator Module

Provides abstract base class and common utilities for all Nexflow code generators.
Target: Flink/Java code generation using Python f-strings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import os


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
    - L2 Schema: POJO classes, Avro schemas, serializers
    - L1 Flow: Flink job structure, sources, sinks
    - L3 Transform: MapFunction, ProcessFunction implementations
    - L4 Rules: CEP patterns, rule evaluation logic
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
        """
        Map Nexflow base types to Java types.

        Args:
            nexflow_type: Nexflow type name (string, integer, decimal, etc.)

        Returns:
            Corresponding Java type
        """
        type_map = {
            'string': 'String',
            'integer': 'Long',
            'decimal': 'BigDecimal',
            'boolean': 'Boolean',
            'date': 'LocalDate',
            'timestamp': 'Instant',
            'uuid': 'UUID',
            'bytes': 'byte[]',
        }
        return type_map.get(nexflow_type.lower(), 'Object')

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
