# Nexflow Parser Module
# ANTLR-generated parsers and wrapper classes

from .base import ParseResult, ParseError, SourceLocation, BaseParser
from .rules_parser import RulesParser
from .flow_parser import FlowParser
from .schema_parser import SchemaParser
from .transform_parser import TransformParser

# Parser registry - maps language ID to parser class
PARSERS = {
    # L1 - Flow/Process Orchestration
    'flow': FlowParser,
    'l1': FlowParser,

    # L2 - Schema Registry
    'schema': SchemaParser,
    'l2': SchemaParser,

    # L3 - Transform Catalog
    'transform': TransformParser,
    'l3': TransformParser,

    # L4 - Business Rules
    'rules': RulesParser,
    'l4': RulesParser,
}


def get_parser(language: str) -> BaseParser:
    """Get parser instance for the specified DSL language."""
    parser_class = PARSERS.get(language.lower())
    if parser_class is None:
        raise ValueError(f"Unknown language: {language}. Supported: {list(PARSERS.keys())}")
    return parser_class()


def parse(content: str, language: str) -> ParseResult:
    """Parse DSL content and return result."""
    parser = get_parser(language)
    return parser.parse(content)


def validate(content: str, language: str) -> ParseResult:
    """Validate DSL content syntax."""
    parser = get_parser(language)
    return parser.validate(content)


__all__ = [
    'ParseResult',
    'ParseError',
    'SourceLocation',
    'BaseParser',
    'RulesParser',
    'FlowParser',
    'SchemaParser',
    'TransformParser',
    'get_parser',
    'parse',
    'validate',
    'PARSERS',
]
