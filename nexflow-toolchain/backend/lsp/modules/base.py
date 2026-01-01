"""
Base Language Module Interface

Defines the contract that all DSL modules must implement.
This enables the plugin architecture where modules can be
registered and loaded independently.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from lsprotocol import types


@dataclass
class ModuleCapabilities:
    """
    Declare what LSP features a module supports.

    Modules only need to implement methods for capabilities they enable.
    The driver will only route requests for enabled capabilities.
    """
    diagnostics: bool = True      # Real-time error reporting
    completion: bool = False      # Auto-completion
    hover: bool = False           # Hover documentation
    symbols: bool = False         # Document outline
    definition: bool = False      # Go to definition
    references: bool = False      # Find all references
    formatting: bool = False      # Code formatting
    rename: bool = False          # Rename symbol
    code_actions: bool = False    # Quick fixes


@dataclass
class SymbolInfo:
    """
    Information about a symbol in the document.
    Used for symbols, definition, and references.
    """
    name: str
    kind: types.SymbolKind
    range: types.Range
    selection_range: types.Range
    children: List["SymbolInfo"] = field(default_factory=list)
    detail: Optional[str] = None

    def to_document_symbol(self) -> types.DocumentSymbol:
        """Convert to LSP DocumentSymbol."""
        return types.DocumentSymbol(
            name=self.name,
            kind=self.kind,
            range=self.range,
            selection_range=self.selection_range,
            detail=self.detail,
            children=[c.to_document_symbol() for c in self.children]
        )


class LanguageModule(ABC):
    """
    Abstract base class for pluggable DSL language modules.

    Each module provides language support for one DSL:
    - L1: ProcDSL (.proc) - Process Orchestration
    - L2: SchemaDSL (.schema) - Data Schemas
    - L3: TransformDSL (.xform) - Transformations
    - L4: RulesDSL (.rules) - Decision Logic

    Modules are registered with the LSP driver at startup and
    receive requests routed by file extension.

    Usage:
        class ProcModule(LanguageModule):
            @property
            def language_id(self) -> str:
                return "procdsl"

            @property
            def file_extensions(self) -> List[str]:
                return [".proc"]

            # ... implement required methods
    """

    # =========================================================================
    # Required Properties (must override)
    # =========================================================================

    @property
    @abstractmethod
    def language_id(self) -> str:
        """
        Unique identifier for this language.

        Examples: 'procdsl', 'schemadsl', 'transformdsl', 'rulesdsl'
        """

    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """
        File extensions this module handles.

        Examples: ['.proc'], ['.schema'], ['.xform'], ['.rules']
        """

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Human-readable name for display in UI.

        Examples: 'ProcDSL (L1 Process Orchestration)'
        """

    # =========================================================================
    # Optional Properties (override to customize)
    # =========================================================================

    @property
    def capabilities(self) -> ModuleCapabilities:
        """
        Declare which LSP features this module supports.

        Override to enable additional features beyond diagnostics.
        """
        return ModuleCapabilities(diagnostics=True)

    @property
    def trigger_characters(self) -> List[str]:
        """
        Characters that trigger completion.

        Override to customize completion triggers.
        """
        return [" "]

    @property
    def version(self) -> str:
        """Module version string."""
        return "0.1.0"

    # =========================================================================
    # Core Methods (implement based on capabilities)
    # =========================================================================

    @abstractmethod
    def get_diagnostics(self, uri: str, content: str) -> List[types.Diagnostic]:
        """
        Parse content and return diagnostics (errors/warnings).

        This is the primary method - all modules must implement it.

        Args:
            uri: Document URI
            content: Full document text

        Returns:
            List of LSP Diagnostic objects
        """

    def get_completions(
        self,
        uri: str,
        content: str,
        position: types.Position,
        trigger_character: Optional[str] = None
    ) -> List[types.CompletionItem]:
        """
        Return completion items at the given position.

        Override if capabilities.completion = True.

        Args:
            uri: Document URI
            content: Full document text
            position: Cursor position
            trigger_character: Character that triggered completion (if any)

        Returns:
            List of CompletionItem objects
        """
        return []

    def get_hover(
        self,
        uri: str,
        content: str,
        position: types.Position
    ) -> Optional[types.Hover]:
        """
        Return hover information at the given position.

        Override if capabilities.hover = True.

        Args:
            uri: Document URI
            content: Full document text
            position: Cursor position

        Returns:
            Hover object with markdown content, or None
        """
        return None

    def get_symbols(self, uri: str, content: str) -> List[types.DocumentSymbol]:
        """
        Return document symbols for the outline view.

        Override if capabilities.symbols = True.

        Args:
            uri: Document URI
            content: Full document text

        Returns:
            List of DocumentSymbol objects (hierarchical)
        """
        return []

    def get_definition(
        self,
        uri: str,
        content: str,
        position: types.Position
    ) -> Optional[types.Location]:
        """
        Return the definition location for symbol at position.

        Override if capabilities.definition = True.

        Args:
            uri: Document URI
            content: Full document text
            position: Cursor position

        Returns:
            Location of definition, or None
        """
        return None

    def get_references(
        self,
        uri: str,
        content: str,
        position: types.Position,
        include_declaration: bool = True
    ) -> List[types.Location]:
        """
        Return all references to symbol at position.

        Override if capabilities.references = True.

        Args:
            uri: Document URI
            content: Full document text
            position: Cursor position
            include_declaration: Whether to include the declaration

        Returns:
            List of Location objects
        """
        return []

    def format_document(
        self,
        uri: str,
        content: str,
        options: types.FormattingOptions
    ) -> List[types.TextEdit]:
        """
        Return text edits to format the document.

        Override if capabilities.formatting = True.

        Args:
            uri: Document URI
            content: Full document text
            options: Formatting options (tab size, etc.)

        Returns:
            List of TextEdit objects
        """
        return []

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def create_range(
        self,
        start_line: int,
        start_char: int,
        end_line: int,
        end_char: int
    ) -> types.Range:
        """
        Helper to create an LSP Range.

        Note: LSP uses 0-based line numbers, but parsers often use 1-based.
        This method expects 0-based line numbers.
        """
        return types.Range(
            start=types.Position(line=start_line, character=start_char),
            end=types.Position(line=end_line, character=end_char)
        )

    def create_diagnostic(
        self,
        message: str,
        line: int,
        column: int,
        end_column: Optional[int] = None,
        severity: types.DiagnosticSeverity = types.DiagnosticSeverity.Error,
        source: Optional[str] = None
    ) -> types.Diagnostic:
        """
        Helper to create an LSP Diagnostic.

        Args:
            message: Error/warning message
            line: 1-based line number (converted to 0-based)
            column: 0-based column number
            end_column: End column (defaults to column + 1)
            severity: Error, Warning, Information, or Hint
            source: Source identifier (defaults to language_id)

        Returns:
            Diagnostic object
        """
        if end_column is None:
            end_column = column + 1

        return types.Diagnostic(
            range=types.Range(
                start=types.Position(line=line - 1, character=column),
                end=types.Position(line=line - 1, character=end_column)
            ),
            message=message,
            severity=severity,
            source=source or f"nexflow-{self.language_id}"
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.language_id} v{self.version}>"
