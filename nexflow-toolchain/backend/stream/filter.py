# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
SQL-Like Filter Expression Parser

Parses and evaluates SQL-like filter expressions for stream message filtering.
Supports: =, !=, <, >, <=, >=, IN, NOT IN, LIKE, IS NULL, IS NOT NULL, AND, OR, NOT
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class TokenType(Enum):
    """Token types for filter expression lexer."""
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    KEYWORD = "KEYWORD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    DOT = "DOT"
    EOF = "EOF"


@dataclass
class Token:
    """Lexer token."""
    type: TokenType
    value: str
    position: int


class FilterLexer:
    """Tokenizer for filter expressions."""

    KEYWORDS = {'AND', 'OR', 'NOT', 'IN', 'LIKE', 'IS', 'NULL', 'TRUE', 'FALSE'}
    OPERATORS = {'=', '!=', '<>', '<', '>', '<=', '>='}

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        """Tokenize the input text."""
        tokens = []

        while self.pos < self.length:
            self._skip_whitespace()
            if self.pos >= self.length:
                break

            token = self._next_token()
            if token:
                tokens.append(token)

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens

    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1

    def _next_token(self) -> Optional[Token]:
        """Get the next token."""
        char = self.text[self.pos]

        # Single character tokens
        if char == '(':
            self.pos += 1
            return Token(TokenType.LPAREN, '(', self.pos - 1)
        if char == ')':
            self.pos += 1
            return Token(TokenType.RPAREN, ')', self.pos - 1)
        if char == '[':
            self.pos += 1
            return Token(TokenType.LBRACKET, '[', self.pos - 1)
        if char == ']':
            self.pos += 1
            return Token(TokenType.RBRACKET, ']', self.pos - 1)
        if char == ',':
            self.pos += 1
            return Token(TokenType.COMMA, ',', self.pos - 1)
        if char == '.':
            self.pos += 1
            return Token(TokenType.DOT, '.', self.pos - 1)

        # Operators
        if char in '=<>!':
            return self._read_operator()

        # String literals
        if char in '"\'':
            return self._read_string()

        # Numbers
        if char.isdigit() or (char == '-' and self.pos + 1 < self.length
                              and self.text[self.pos + 1].isdigit()):
            return self._read_number()

        # Identifiers and keywords
        if char.isalpha() or char == '_':
            return self._read_identifier()

        raise ValueError(f"Unexpected character '{char}' at position {self.pos}")

    def _read_operator(self) -> Token:
        """Read an operator token."""
        start = self.pos
        # Try two-character operators first
        if self.pos + 1 < self.length:
            two_char = self.text[self.pos:self.pos + 2]
            if two_char in ('!=', '<>', '<=', '>='):
                self.pos += 2
                return Token(TokenType.OPERATOR, two_char, start)

        # Single character operator
        char = self.text[self.pos]
        self.pos += 1
        return Token(TokenType.OPERATOR, char, start)

    def _read_string(self) -> Token:
        """Read a string literal."""
        quote = self.text[self.pos]
        start = self.pos
        self.pos += 1
        value = []

        while self.pos < self.length:
            char = self.text[self.pos]
            if char == quote:
                self.pos += 1
                return Token(TokenType.STRING, ''.join(value), start)
            if char == '\\' and self.pos + 1 < self.length:
                self.pos += 1
                value.append(self.text[self.pos])
            else:
                value.append(char)
            self.pos += 1

        raise ValueError(f"Unterminated string starting at position {start}")

    def _read_number(self) -> Token:
        """Read a numeric literal."""
        start = self.pos
        value = []

        # Optional negative sign
        if self.text[self.pos] == '-':
            value.append('-')
            self.pos += 1

        # Integer part
        while self.pos < self.length and self.text[self.pos].isdigit():
            value.append(self.text[self.pos])
            self.pos += 1

        # Decimal part
        if self.pos < self.length and self.text[self.pos] == '.':
            value.append('.')
            self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                value.append(self.text[self.pos])
                self.pos += 1

        return Token(TokenType.NUMBER, ''.join(value), start)

    def _read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start = self.pos
        value = []

        while self.pos < self.length:
            char = self.text[self.pos]
            if char.isalnum() or char == '_':
                value.append(char)
                self.pos += 1
            else:
                break

        text = ''.join(value)
        upper = text.upper()

        if upper in self.KEYWORDS:
            return Token(TokenType.KEYWORD, upper, start)
        return Token(TokenType.IDENTIFIER, text, start)


@dataclass
class FilterExpression:
    """Base class for filter expressions."""

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Evaluate the expression against a record."""
        raise NotImplementedError


@dataclass
class FieldAccess(FilterExpression):
    """Field access expression (e.g., 'customer.address.city')."""
    path: List[Union[str, int]]

    def evaluate(self, record: Dict[str, Any]) -> Any:
        """Get the field value from the record."""
        value = record
        for part in self.path:
            if isinstance(part, int):
                if isinstance(value, list) and 0 <= part < len(value):
                    value = value[part]
                else:
                    return None
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value


@dataclass
class Literal(FilterExpression):
    """Literal value expression."""
    value: Any

    def evaluate(self, record: Dict[str, Any]) -> Any:
        return self.value


@dataclass
class ComparisonExpr(FilterExpression):
    """Comparison expression (=, !=, <, >, <=, >=)."""
    left: FilterExpression
    operator: str
    right: FilterExpression

    def evaluate(self, record: Dict[str, Any]) -> bool:
        left_val = self.left.evaluate(record)
        right_val = self.right.evaluate(record)

        if left_val is None or right_val is None:
            return False

        if self.operator == '=':
            return left_val == right_val
        elif self.operator in ('!=', '<>'):
            return left_val != right_val
        elif self.operator == '<':
            return left_val < right_val
        elif self.operator == '>':
            return left_val > right_val
        elif self.operator == '<=':
            return left_val <= right_val
        elif self.operator == '>=':
            return left_val >= right_val
        return False


@dataclass
class InExpr(FilterExpression):
    """IN expression (field IN ('a', 'b', 'c'))."""
    field: FilterExpression
    values: List[FilterExpression]
    negated: bool = False

    def evaluate(self, record: Dict[str, Any]) -> bool:
        field_val = self.field.evaluate(record)
        if field_val is None:
            return False

        value_list = [v.evaluate(record) for v in self.values]
        result = field_val in value_list
        return not result if self.negated else result


@dataclass
class LikeExpr(FilterExpression):
    """LIKE expression with SQL pattern matching."""
    field: FilterExpression
    pattern: str

    def evaluate(self, record: Dict[str, Any]) -> bool:
        field_val = self.field.evaluate(record)
        if field_val is None or not isinstance(field_val, str):
            return False

        # Convert SQL LIKE pattern to regex
        regex = self.pattern.replace('%', '.*').replace('_', '.')
        regex = f'^{regex}$'
        return bool(re.match(regex, field_val, re.IGNORECASE))


@dataclass
class IsNullExpr(FilterExpression):
    """IS NULL / IS NOT NULL expression."""
    field: FilterExpression
    negated: bool = False

    def evaluate(self, record: Dict[str, Any]) -> bool:
        field_val = self.field.evaluate(record)
        is_null = field_val is None
        return not is_null if self.negated else is_null


@dataclass
class AndExpr(FilterExpression):
    """Logical AND expression."""
    left: FilterExpression
    right: FilterExpression

    def evaluate(self, record: Dict[str, Any]) -> bool:
        return self.left.evaluate(record) and self.right.evaluate(record)


@dataclass
class OrExpr(FilterExpression):
    """Logical OR expression."""
    left: FilterExpression
    right: FilterExpression

    def evaluate(self, record: Dict[str, Any]) -> bool:
        return self.left.evaluate(record) or self.right.evaluate(record)


@dataclass
class NotExpr(FilterExpression):
    """Logical NOT expression."""
    expr: FilterExpression

    def evaluate(self, record: Dict[str, Any]) -> bool:
        return not self.expr.evaluate(record)


class FilterParser:
    """Parser for SQL-like filter expressions."""

    def __init__(self, expression: str):
        self.tokens = FilterLexer(expression).tokenize()
        self.pos = 0
        self.expression = expression

    def parse(self) -> FilterExpression:
        """Parse the filter expression."""
        if not self.tokens or self.current().type == TokenType.EOF:
            raise ValueError("Empty filter expression")

        expr = self._parse_or()

        if self.current().type != TokenType.EOF:
            raise ValueError(f"Unexpected token: {self.current().value}")

        return expr

    def current(self) -> Token:
        """Get current token."""
        return self.tokens[self.pos]

    def advance(self) -> Token:
        """Advance to next token and return current."""
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType, value: Optional[str] = None) -> Token:
        """Expect a specific token type and optionally value."""
        token = self.current()
        if token.type != token_type:
            raise ValueError(f"Expected {token_type}, got {token.type} at position {token.position}")
        if value and token.value != value:
            raise ValueError(f"Expected '{value}', got '{token.value}' at position {token.position}")
        return self.advance()

    def _parse_or(self) -> FilterExpression:
        """Parse OR expressions."""
        left = self._parse_and()

        while (self.current().type == TokenType.KEYWORD and
               self.current().value == 'OR'):
            self.advance()
            right = self._parse_and()
            left = OrExpr(left, right)

        return left

    def _parse_and(self) -> FilterExpression:
        """Parse AND expressions."""
        left = self._parse_not()

        while (self.current().type == TokenType.KEYWORD and
               self.current().value == 'AND'):
            self.advance()
            right = self._parse_not()
            left = AndExpr(left, right)

        return left

    def _parse_not(self) -> FilterExpression:
        """Parse NOT expressions."""
        if (self.current().type == TokenType.KEYWORD and
            self.current().value == 'NOT'):
            self.advance()
            return NotExpr(self._parse_not())

        return self._parse_comparison()

    def _parse_comparison(self) -> FilterExpression:
        """Parse comparison expressions."""
        left = self._parse_primary()

        # Check for comparison operators
        if self.current().type == TokenType.OPERATOR:
            op = self.advance().value
            right = self._parse_primary()
            return ComparisonExpr(left, op, right)

        # Check for IN / NOT IN
        if (self.current().type == TokenType.KEYWORD and
            self.current().value in ('IN', 'NOT')):
            negated = False
            if self.current().value == 'NOT':
                self.advance()
                negated = True
            self.expect(TokenType.KEYWORD, 'IN')
            values = self._parse_value_list()
            return InExpr(left, values, negated)

        # Check for LIKE
        if (self.current().type == TokenType.KEYWORD and
            self.current().value == 'LIKE'):
            self.advance()
            pattern = self.expect(TokenType.STRING).value
            return LikeExpr(left, pattern)

        # Check for IS NULL / IS NOT NULL
        if (self.current().type == TokenType.KEYWORD and
            self.current().value == 'IS'):
            self.advance()
            negated = False
            if self.current().type == TokenType.KEYWORD and self.current().value == 'NOT':
                self.advance()
                negated = True
            self.expect(TokenType.KEYWORD, 'NULL')
            return IsNullExpr(left, negated)

        return left

    def _parse_primary(self) -> FilterExpression:
        """Parse primary expressions (literals, field access, parentheses)."""
        token = self.current()

        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self._parse_or()
            self.expect(TokenType.RPAREN)
            return expr

        # String literal
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(token.value)

        # Number literal
        if token.type == TokenType.NUMBER:
            self.advance()
            value = float(token.value) if '.' in token.value else int(token.value)
            return Literal(value)

        # Boolean/NULL keywords
        if token.type == TokenType.KEYWORD:
            if token.value == 'TRUE':
                self.advance()
                return Literal(True)
            if token.value == 'FALSE':
                self.advance()
                return Literal(False)
            if token.value == 'NULL':
                self.advance()
                return Literal(None)

        # Field access
        if token.type == TokenType.IDENTIFIER:
            return self._parse_field_access()

        raise ValueError(f"Unexpected token: {token.value} at position {token.position}")

    def _parse_field_access(self) -> FieldAccess:
        """Parse field access expression (e.g., 'customer.address.city' or 'items[0]')."""
        path = [self.advance().value]

        while True:
            # Dot notation
            if self.current().type == TokenType.DOT:
                self.advance()
                path.append(self.expect(TokenType.IDENTIFIER).value)
            # Array index
            elif self.current().type == TokenType.LBRACKET:
                self.advance()
                index = int(self.expect(TokenType.NUMBER).value)
                path.append(index)
                self.expect(TokenType.RBRACKET)
            else:
                break

        return FieldAccess(path)

    def _parse_value_list(self) -> List[FilterExpression]:
        """Parse a list of values for IN expression."""
        self.expect(TokenType.LPAREN)
        values = []

        while self.current().type != TokenType.RPAREN:
            if values:
                self.expect(TokenType.COMMA)

            token = self.current()
            if token.type == TokenType.STRING:
                self.advance()
                values.append(Literal(token.value))
            elif token.type == TokenType.NUMBER:
                self.advance()
                value = float(token.value) if '.' in token.value else int(token.value)
                values.append(Literal(value))
            else:
                raise ValueError(f"Expected literal value in list at position {token.position}")

        self.expect(TokenType.RPAREN)
        return values


def parse_filter(expression: str) -> FilterExpression:
    """Parse a filter expression string."""
    return FilterParser(expression).parse()


def matches_filter(record: Dict[str, Any], filter_expr: Optional[str]) -> bool:
    """Check if a record matches a filter expression."""
    if not filter_expr:
        return True

    try:
        expr = parse_filter(filter_expr)
        return expr.evaluate(record)
    except Exception as e:
        raise ValueError(f"Filter error: {e}")
