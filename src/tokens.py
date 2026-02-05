"""
Kira Language - Token Definitions
=================================
Tokens are the smallest units of meaning in source code.
The lexer converts raw text into a stream of tokens.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    """All token types in the Kira language."""
    
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    LET = auto()
    CONST = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    
    # Operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    ASTERISK = auto()      # *
    SLASH = auto()         # /
    PERCENT = auto()       # %
    POWER = auto()         # **
    
    # Comparison
    EQ = auto()            # ==
    NOT_EQ = auto()        # !=
    LT = auto()            # <
    GT = auto()            # >
    LT_EQ = auto()         # <=
    GT_EQ = auto()         # >=
    
    # Logical
    AND = auto()           # and
    OR = auto()            # or
    NOT = auto()           # not
    
    # Assignment
    ASSIGN = auto()        # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    
    # Delimiters
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    COMMA = auto()         # ,
    COLON = auto()         # :
    SEMICOLON = auto()     # ;
    DOT = auto()           # .
    ARROW = auto()         # ->
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    ILLEGAL = auto()


@dataclass
class Token:
    """
    A token with its type, literal value, and source location.
    
    Attributes:
        type: The type of token
        literal: The actual string value from source
        value: The parsed value (e.g., int for INTEGER)
        line: Line number in source
        column: Column number in source
    """
    type: TokenType
    literal: str
    value: Any = None
    line: int = 1
    column: int = 1
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.literal!r}, line={self.line})"


# Keyword mapping
KEYWORDS = {
    'let': TokenType.LET,
    'const': TokenType.CONST,
    'fn': TokenType.FN,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'in': TokenType.IN,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
}


def lookup_identifier(ident: str) -> TokenType:
    """Check if identifier is a keyword, return appropriate token type."""
    return KEYWORDS.get(ident, TokenType.IDENTIFIER)
