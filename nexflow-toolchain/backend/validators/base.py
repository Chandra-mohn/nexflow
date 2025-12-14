# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Base Validator Classes

Foundation for semantic validation of Nexflow DSL ASTs.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from enum import Enum


class Severity(Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """A single validation error or warning."""
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: Severity = Severity.ERROR
    code: Optional[str] = None  # e.g., "SCHEMA_NOT_FOUND", "TYPE_MISMATCH"

    def __str__(self) -> str:
        loc = ""
        if self.file:
            loc = str(self.file)
            if self.line:
                loc += f":{self.line}"
                if self.column:
                    loc += f":{self.column}"
            loc += ": "
        severity_prefix = f"[{self.severity.value.upper()}] " if self.severity != Severity.ERROR else ""
        return f"{loc}{severity_prefix}{self.message}"


@dataclass
class ValidationResult:
    """Result of validation containing errors and warnings."""
    success: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    def add_error(self, message: str, **kwargs) -> None:
        """Add an error and mark validation as failed."""
        self.errors.append(ValidationError(message=message, severity=Severity.ERROR, **kwargs))
        self.success = False

    def add_warning(self, message: str, **kwargs) -> None:
        """Add a warning (does not fail validation)."""
        self.warnings.append(ValidationError(message=message, severity=Severity.WARNING, **kwargs))

    def add_info(self, message: str, **kwargs) -> None:
        """Add an info message."""
        self.warnings.append(ValidationError(message=message, severity=Severity.INFO, **kwargs))

    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.success:
            self.success = False

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len([w for w in self.warnings if w.severity == Severity.WARNING])

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


@dataclass
class ValidationContext:
    """
    Shared context for cross-file validation.

    Stores registered schemas, transforms, rules, and flows
    for reference validation across DSL files.
    """
    # Registered definitions by name
    schemas: Dict[str, Any] = field(default_factory=dict)
    transforms: Dict[str, Any] = field(default_factory=dict)
    rules: Dict[str, Any] = field(default_factory=dict)
    decision_tables: Dict[str, Any] = field(default_factory=dict)
    flows: Dict[str, Any] = field(default_factory=dict)

    # File paths for better error reporting
    schema_files: Dict[str, Path] = field(default_factory=dict)
    transform_files: Dict[str, Path] = field(default_factory=dict)
    rules_files: Dict[str, Path] = field(default_factory=dict)
    flow_files: Dict[str, Path] = field(default_factory=dict)

    def register_schema(self, name: str, ast: Any, file_path: Optional[Path] = None) -> None:
        """Register a schema definition."""
        self.schemas[name] = ast
        if file_path:
            self.schema_files[name] = file_path

    def register_transform(self, name: str, ast: Any, file_path: Optional[Path] = None) -> None:
        """Register a transform definition."""
        self.transforms[name] = ast
        if file_path:
            self.transform_files[name] = file_path

    def register_rule(self, name: str, ast: Any, file_path: Optional[Path] = None) -> None:
        """Register a procedural rule definition."""
        self.rules[name] = ast
        if file_path:
            self.rules_files[name] = file_path

    def register_decision_table(self, name: str, ast: Any, file_path: Optional[Path] = None) -> None:
        """Register a decision table definition."""
        self.decision_tables[name] = ast
        if file_path:
            self.rules_files[name] = file_path

    def register_flow(self, name: str, ast: Any, file_path: Optional[Path] = None) -> None:
        """Register a flow/process definition."""
        self.flows[name] = ast
        if file_path:
            self.flow_files[name] = file_path

    def has_schema(self, name: str) -> bool:
        return name in self.schemas

    def has_transform(self, name: str) -> bool:
        return name in self.transforms

    def has_rule(self, name: str) -> bool:
        return name in self.rules or name in self.decision_tables

    def has_flow(self, name: str) -> bool:
        return name in self.flows

    def get_all_schema_names(self) -> Set[str]:
        return set(self.schemas.keys())

    def get_all_transform_names(self) -> Set[str]:
        return set(self.transforms.keys())

    def get_all_rule_names(self) -> Set[str]:
        return set(self.rules.keys()) | set(self.decision_tables.keys())


class BaseValidator:
    """
    Base class for AST validators.

    Validators check semantic correctness of ASTs after parsing.
    They can use a shared ValidationContext for cross-file validation.
    """

    def __init__(self, context: Optional[ValidationContext] = None):
        self.context = context or ValidationContext()

    def validate(self, ast: Any, file_path: Optional[Path] = None) -> ValidationResult:
        """
        Validate an AST.

        Args:
            ast: The AST to validate
            file_path: Optional path for error reporting

        Returns:
            ValidationResult with errors and warnings
        """
        raise NotImplementedError("Subclasses must implement validate()")

    def _get_location(self, node: Any) -> tuple:
        """Extract location info from an AST node."""
        if hasattr(node, 'location') and node.location:
            return (node.location.line, node.location.column)
        return (None, None)
