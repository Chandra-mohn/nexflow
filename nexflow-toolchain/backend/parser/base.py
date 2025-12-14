# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Base Parser Infrastructure for Nexflow

Provides common error handling, source location tracking, and parsing utilities.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Any, TypeVar, Generic
from enum import Enum
from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener


class ErrorSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SourceLocation:
    """Source location for error reporting."""
    line: int
    column: int
    start_index: int = 0
    stop_index: int = 0

    def __str__(self) -> str:
        return f"line {self.line}:{self.column}"


@dataclass
class ParseError:
    """Parse error with location and context."""
    message: str
    location: Optional[SourceLocation] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    rule: Optional[str] = None
    token: Optional[str] = None

    def __str__(self) -> str:
        loc = f" at {self.location}" if self.location else ""
        return f"[{self.severity.value.upper()}]{loc}: {self.message}"


@dataclass
class ParseResult(Generic[TypeVar('T')]):
    """Result of a parse operation."""
    success: bool
    ast: Optional[Any] = None
    errors: List[ParseError] = field(default_factory=list)
    warnings: List[ParseError] = field(default_factory=list)
    parse_tree: Optional[Any] = None  # Raw ANTLR parse tree

    def add_error(self, message: str, location: Optional[SourceLocation] = None,
                  rule: Optional[str] = None, token: Optional[str] = None):
        self.errors.append(ParseError(
            message=message,
            location=location,
            severity=ErrorSeverity.ERROR,
            rule=rule,
            token=token
        ))
        self.success = False

    def add_warning(self, message: str, location: Optional[SourceLocation] = None,
                    rule: Optional[str] = None, token: Optional[str] = None):
        self.warnings.append(ParseError(
            message=message,
            location=location,
            severity=ErrorSeverity.WARNING,
            rule=rule,
            token=token
        ))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'errors': [
                {
                    'message': e.message,
                    'line': e.location.line if e.location else None,
                    'column': e.location.column if e.location else None,
                    'severity': e.severity.value,
                    'rule': e.rule,
                    'token': e.token
                }
                for e in self.errors
            ],
            'warnings': [
                {
                    'message': w.message,
                    'line': w.location.line if w.location else None,
                    'column': w.location.column if w.location else None,
                    'severity': w.severity.value,
                    'rule': w.rule,
                    'token': w.token
                }
                for w in self.warnings
            ]
        }


class NexflowErrorListener(ErrorListener):
    """Custom error listener for collecting parse errors."""

    def __init__(self):
        super().__init__()
        self.errors: List[ParseError] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        location = SourceLocation(line=line, column=column)
        token_text = offendingSymbol.text if offendingSymbol else None
        self.errors.append(ParseError(
            message=msg,
            location=location,
            severity=ErrorSeverity.ERROR,
            token=token_text
        ))


class BaseParser:
    """Base class for DSL parsers."""

    def __init__(self):
        self._error_listener = NexflowErrorListener()

    def _create_input_stream(self, content: str) -> InputStream:
        """Create an ANTLR input stream from content."""
        return InputStream(content)

    def _get_location(self, ctx) -> Optional[SourceLocation]:
        """Extract source location from parser context."""
        if ctx is None:
            return None
        start = ctx.start if hasattr(ctx, 'start') else None
        stop = ctx.stop if hasattr(ctx, 'stop') else None
        if start:
            return SourceLocation(
                line=start.line,
                column=start.column,
                start_index=start.start if hasattr(start, 'start') else 0,
                stop_index=stop.stop if stop and hasattr(stop, 'stop') else 0
            )
        return None

    def _setup_parser(self, lexer_class, parser_class, content: str):
        """Set up lexer and parser with error listener."""
        input_stream = self._create_input_stream(content)
        lexer = lexer_class(input_stream)

        # Remove default error listeners and add custom one
        lexer.removeErrorListeners()
        lexer.addErrorListener(self._error_listener)

        token_stream = CommonTokenStream(lexer)
        parser = parser_class(token_stream)

        # Remove default error listeners and add custom one
        parser.removeErrorListeners()
        parser.addErrorListener(self._error_listener)

        return parser

    def _collect_errors(self, result: ParseResult):
        """Collect errors from error listener into result."""
        for error in self._error_listener.errors:
            result.errors.append(error)
            result.success = False
        # Clear errors for next parse
        self._error_listener.errors.clear()

    def parse(self, content: str) -> ParseResult:
        """Parse content and return result. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement parse()")

    def validate(self, content: str) -> ParseResult:
        """Validate content syntax without building full AST."""
        return self.parse(content)
