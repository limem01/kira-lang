"""
Kira Language - Lexer (Tokenizer)
=================================
The lexer reads source code character by character and produces tokens.
This is the first phase of interpretation/compilation.

Example:
    "let x = 5 + 3"
    → [LET, IDENTIFIER("x"), ASSIGN, INTEGER(5), PLUS, INTEGER(3)]
"""

from .tokens import Token, TokenType, lookup_identifier


class LexerError(Exception):
    """Raised when the lexer encounters invalid syntax."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class Lexer:
    """
    Converts source code string into a stream of tokens.
    
    Usage:
        lexer = Lexer("let x = 5")
        tokens = lexer.tokenize()
    """
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    @property
    def current_char(self) -> str | None:
        """Get current character or None if at end."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> str | None:
        """Look ahead without consuming."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> str | None:
        """Consume current character and move forward."""
        char = self.current_char
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        """Skip spaces and tabs (but not newlines)."""
        while self.current_char in (' ', '\t', '\r'):
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comments starting with #."""
        while self.current_char and self.current_char != '\n':
            self.advance()
    
    def make_token(self, type: TokenType, literal: str, value=None) -> Token:
        """Create a token with current position info."""
        return Token(
            type=type,
            literal=literal,
            value=value,
            line=self.line,
            column=self.column - len(literal)
        )
    
    def read_string(self, quote_char: str) -> Token:
        """Read a string literal (single or double quoted)."""
        start_line = self.line
        start_col = self.column
        self.advance()  # consume opening quote
        
        result = []
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\':
                self.advance()
                escape_char = self.current_char
                if escape_char == 'n':
                    result.append('\n')
                elif escape_char == 't':
                    result.append('\t')
                elif escape_char == 'r':
                    result.append('\r')
                elif escape_char == '\\':
                    result.append('\\')
                elif escape_char == quote_char:
                    result.append(quote_char)
                else:
                    result.append('\\')
                    result.append(escape_char or '')
                self.advance()
            elif self.current_char == '\n':
                raise LexerError("Unterminated string literal", start_line, start_col)
            else:
                result.append(self.current_char)
                self.advance()
        
        if self.current_char != quote_char:
            raise LexerError("Unterminated string literal", start_line, start_col)
        
        self.advance()  # consume closing quote
        value = ''.join(result)
        return Token(TokenType.STRING, value, value, start_line, start_col)
    
    def read_number(self) -> Token:
        """Read an integer or float literal."""
        start_col = self.column
        result = []
        has_dot = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    break  # Second dot, stop here
                if not (self.peek() and self.peek().isdigit()):
                    break  # Dot not followed by digit
                has_dot = True
            result.append(self.current_char)
            self.advance()
        
        literal = ''.join(result)
        if has_dot:
            return Token(TokenType.FLOAT, literal, float(literal), self.line, start_col)
        else:
            return Token(TokenType.INTEGER, literal, int(literal), self.line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_col = self.column
        result = []
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result.append(self.current_char)
            self.advance()
        
        literal = ''.join(result)
        token_type = lookup_identifier(literal)
        
        # Set value for boolean literals
        value = None
        if token_type == TokenType.TRUE:
            value = True
        elif token_type == TokenType.FALSE:
            value = False
        
        return Token(token_type, literal, value, self.line, start_col)
    
    def next_token(self) -> Token:
        """Get the next token from the source."""
        self.skip_whitespace()
        
        if self.current_char is None:
            return self.make_token(TokenType.EOF, "")
        
        char = self.current_char
        
        # Comments
        if char == '#':
            self.skip_comment()
            return self.next_token()
        
        # Newlines (significant in some contexts)
        if char == '\n':
            self.advance()
            return self.make_token(TokenType.NEWLINE, "\\n")
        
        # Strings
        if char in ('"', "'"):
            return self.read_string(char)
        
        # Numbers
        if char.isdigit():
            return self.read_number()
        
        # Identifiers and keywords
        if char.isalpha() or char == '_':
            return self.read_identifier()
        
        # Two-character operators
        if char == '=' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.EQ, "==")
        
        if char == '!' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.NOT_EQ, "!=")
        
        if char == '<' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.LT_EQ, "<=")
        
        if char == '>' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.GT_EQ, ">=")
        
        if char == '*' and self.peek() == '*':
            self.advance()
            self.advance()
            return self.make_token(TokenType.POWER, "**")
        
        if char == '+' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.PLUS_ASSIGN, "+=")
        
        if char == '-' and self.peek() == '=':
            self.advance()
            self.advance()
            return self.make_token(TokenType.MINUS_ASSIGN, "-=")
        
        if char == '-' and self.peek() == '>':
            self.advance()
            self.advance()
            return self.make_token(TokenType.ARROW, "->")
        
        # Single-character operators and delimiters
        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.ASTERISK,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '=': TokenType.ASSIGN,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
        }
        
        if char in single_char_tokens:
            self.advance()
            return self.make_token(single_char_tokens[char], char)
        
        # Unknown character
        self.advance()
        raise LexerError(f"Unexpected character: {char!r}", self.line, self.column - 1)
    
    def tokenize(self) -> list[Token]:
        """Tokenize the entire source and return list of tokens."""
        self.tokens = []
        while True:
            token = self.next_token()
            # Skip newlines for simpler parsing (can be changed for newline-significant syntax)
            if token.type != TokenType.NEWLINE:
                self.tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return self.tokens
