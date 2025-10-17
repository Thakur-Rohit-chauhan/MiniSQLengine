"""
SQL Lexer (Tokenizer) for CoreDB.

This module provides tokenization of SQL statements into a stream of tokens
that can be consumed by the parser.
"""

import re
from typing import Iterator, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .exceptions import SQLSyntaxError


class TokenType(Enum):
    """Types of tokens in SQL."""
    # Keywords
    CREATE = "CREATE"
    TABLE = "TABLE"
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    DROP = "DROP"
    ALTER = "ALTER"
    JOIN = "JOIN"
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    OUTER = "OUTER"
    ON = "ON"
    AS = "AS"
    REFERENCES = "REFERENCES"
    
    # Data types
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    
    # Operators
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER_LITERAL = "NUMBER_LITERAL"
    BOOLEAN_LITERAL = "BOOLEAN_LITERAL"
    NULL = "NULL"
    
    # Punctuation
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    COMMA = ","
    SEMICOLON = ";"
    ASTERISK = "*"
    DOT = "."
    
    # Special
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


@dataclass
class Token:
    """Represents a single token in the SQL statement."""
    
    type: TokenType
    value: str
    position: int
    line: int = 1
    column: int = 1
    
    def __str__(self) -> str:
        return f"Token({self.type.value}, '{self.value}', pos={self.position})"


class SQLTokenizer:
    """
    SQL tokenizer that converts SQL strings into tokens.
    
    This tokenizer handles basic SQL syntax including:
    - Keywords (CREATE, SELECT, INSERT, etc.)
    - Identifiers (table names, column names)
    - Literals (strings, numbers, booleans)
    - Operators and punctuation
    """
    
    # SQL keywords mapping
    KEYWORDS = {
        'CREATE': TokenType.CREATE,
        'TABLE': TokenType.TABLE,
        'INSERT': TokenType.INSERT,
        'INTO': TokenType.INTO,
        'VALUES': TokenType.VALUES,
        'SELECT': TokenType.SELECT,
        'FROM': TokenType.FROM,
        'WHERE': TokenType.WHERE,
        'UPDATE': TokenType.UPDATE,
        'SET': TokenType.SET,
        'DELETE': TokenType.DELETE,
        'DROP': TokenType.DROP,
        'ALTER': TokenType.ALTER,
        'JOIN': TokenType.JOIN,
        'INNER': TokenType.INNER,
        'LEFT': TokenType.LEFT,
        'RIGHT': TokenType.RIGHT,
        'FULL': TokenType.FULL,
        'OUTER': TokenType.OUTER,
        'ON': TokenType.ON,
        'AS': TokenType.AS,
        'REFERENCES': TokenType.REFERENCES,
        'INT': TokenType.INT,
        'TEXT': TokenType.TEXT,
        'FLOAT': TokenType.FLOAT,
        'BOOLEAN': TokenType.BOOLEAN,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
        'NOT': TokenType.NOT,
        'NULL': TokenType.NULL,
    }
    
    # Regular expressions for different token types
    PATTERNS = [
        (r'\s+', None),  # Whitespace (ignored)
        (r'--.*', None),  # Single-line comments (ignored)
        (r'/\*.*?\*/', None),  # Multi-line comments (ignored)
        (r'\b\d+\.\d+\b', TokenType.NUMBER_LITERAL),  # Float numbers
        (r'\b\d+\b', TokenType.NUMBER_LITERAL),  # Integer numbers
        (r'\btrue\b|\bfalse\b', TokenType.BOOLEAN_LITERAL),  # Boolean literals
        (r"'([^'\\]|\\.)*'", TokenType.STRING_LITERAL),  # Single-quoted strings
        (r'"([^"\\]|\\.)*"', TokenType.STRING_LITERAL),  # Double-quoted strings
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),  # Identifiers
        (r'!=', TokenType.NOT_EQUALS),
        (r'<=', TokenType.LESS_EQUAL),
        (r'>=', TokenType.GREATER_EQUAL),
        (r'=', TokenType.EQUALS),
        (r'<', TokenType.LESS_THAN),
        (r'>', TokenType.GREATER_THAN),
        (r'\*', TokenType.ASTERISK),
        (r'\(', TokenType.LEFT_PAREN),
        (r'\)', TokenType.RIGHT_PAREN),
        (r',', TokenType.COMMA),
        (r';', TokenType.SEMICOLON),
        (r'\.', TokenType.DOT),
    ]
    
    def __init__(self, sql: str):
        """Initialize tokenizer with SQL string."""
        self.sql = sql.strip()
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self._tokenize()
    
    def _tokenize(self) -> None:
        """Tokenize the SQL string into a list of tokens."""
        while self.position < len(self.sql):
            token = self._next_token()
            if token:
                self.tokens.append(token)
        
        # Add EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            value="",
            position=self.position,
            line=self.line,
            column=self.column
        ))
    
    def _next_token(self) -> Optional[Token]:
        """Get the next token from the SQL string."""
        if self.position >= len(self.sql):
            return None
        
        # Try each pattern
        for pattern, token_type in self.PATTERNS:
            match = re.match(pattern, self.sql[self.position:], re.IGNORECASE)
            if match:
                value = match.group(0)
                start_pos = self.position
                
                # Update position
                self._update_position(value)
                
                # Skip whitespace and comments
                if token_type is None:
                    return self._next_token()
                
                # Handle string literals (remove quotes)
                if token_type == TokenType.STRING_LITERAL:
                    value = value[1:-1]  # Remove quotes
                    # Handle escape sequences
                    value = value.replace("\\'", "'").replace('\\"', '"')
                
                # Check if identifier is a keyword
                if token_type == TokenType.IDENTIFIER:
                    token_type = self.KEYWORDS.get(value.upper(), TokenType.IDENTIFIER)
                
                return Token(
                    type=token_type,
                    value=value,
                    position=start_pos,
                    line=self.line,
                    column=self.column - len(value)
                )
        
        # No pattern matched - unknown token
        char = self.sql[self.position]
        self.position += 1
        self._update_position(char)
        
        return Token(
            type=TokenType.UNKNOWN,
            value=char,
            position=self.position - 1,
            line=self.line,
            column=self.column - 1
        )
    
    def _update_position(self, text: str) -> None:
        """Update line and column position based on consumed text."""
        for char in text:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def get_tokens(self) -> List[Token]:
        """Get all tokens."""
        return self.tokens
    
    def tokenize(self) -> Iterator[Token]:
        """Iterate over tokens."""
        for token in self.tokens:
            yield token
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at a token without consuming it."""
        index = self.position + offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None
    
    def consume(self, expected_type: Optional[TokenType] = None) -> Optional[Token]:
        """Consume and return the next token."""
        if self.position >= len(self.tokens):
            return None
        
        token = self.tokens[self.position]
        
        if expected_type and token.type != expected_type:
            raise SQLSyntaxError(
                f"Expected {expected_type.value}, got {token.type.value}",
                token.position
            )
        
        self.position += 1
        return token
    
    def expect(self, expected_type: TokenType) -> Token:
        """Expect and consume a specific token type."""
        token = self.consume(expected_type)
        if not token:
            raise SQLSyntaxError(f"Expected {expected_type.value}, got EOF")
        return token
    
    def reset(self) -> None:
        """Reset tokenizer position to beginning."""
        self.position = 0
    
    def has_more(self) -> bool:
        """Check if there are more tokens to consume."""
        return self.position < len(self.tokens) - 1  # -1 for EOF token
