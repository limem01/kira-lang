"""
Kira Language - Parser
======================
The parser converts a stream of tokens into an Abstract Syntax Tree (AST).
Uses Pratt parsing (top-down operator precedence) for expressions.

This is the second phase of interpretation:
    Source Code → [Lexer] → Tokens → [Parser] → AST
"""

from typing import Callable, Optional
from .tokens import Token, TokenType
from .lexer import Lexer
from . import ast_nodes as ast


class ParserError(Exception):
    """Raised when the parser encounters a syntax error."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}: {message}")


# Operator precedence levels (higher = binds tighter)
class Precedence:
    LOWEST = 0
    OR = 1           # or
    AND = 2          # and
    NOT = 3          # not
    EQUALS = 4       # == !=
    COMPARE = 5      # < > <= >=
    SUM = 6          # + -
    PRODUCT = 7      # * / %
    POWER = 8        # **
    PREFIX = 9       # -x !x
    CALL = 10        # func()
    INDEX = 11       # arr[i]


# Map token types to precedence
PRECEDENCES = {
    TokenType.OR: Precedence.OR,
    TokenType.AND: Precedence.AND,
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.COMPARE,
    TokenType.GT: Precedence.COMPARE,
    TokenType.LT_EQ: Precedence.COMPARE,
    TokenType.GT_EQ: Precedence.COMPARE,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.PERCENT: Precedence.PRODUCT,
    TokenType.POWER: Precedence.POWER,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACKET: Precedence.INDEX,
}


class Parser:
    """
    Recursive descent parser with Pratt parsing for expressions.
    
    Usage:
        parser = Parser(tokens)
        ast = parser.parse_program()
    """
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: list[str] = []
        
        # Pratt parser function tables
        self.prefix_parse_fns: dict[TokenType, Callable] = {}
        self.infix_parse_fns: dict[TokenType, Callable] = {}
        
        # Register prefix parsers (for literals, identifiers, prefix operators)
        self.register_prefix(TokenType.IDENTIFIER, self.parse_identifier)
        self.register_prefix(TokenType.INTEGER, self.parse_integer)
        self.register_prefix(TokenType.FLOAT, self.parse_float)
        self.register_prefix(TokenType.STRING, self.parse_string)
        self.register_prefix(TokenType.TRUE, self.parse_boolean)
        self.register_prefix(TokenType.FALSE, self.parse_boolean)
        self.register_prefix(TokenType.NULL, self.parse_null)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.NOT, self.parse_prefix_expression)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenType.LBRACKET, self.parse_array_literal)
        self.register_prefix(TokenType.LBRACE, self.parse_dict_or_block)
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FN, self.parse_function_literal)
        
        # Register infix parsers (for binary operators)
        for op in [TokenType.PLUS, TokenType.MINUS, TokenType.ASTERISK,
                   TokenType.SLASH, TokenType.PERCENT, TokenType.POWER,
                   TokenType.EQ, TokenType.NOT_EQ, TokenType.LT, TokenType.GT,
                   TokenType.LT_EQ, TokenType.GT_EQ, TokenType.AND, TokenType.OR]:
            self.register_infix(op, self.parse_infix_expression)
        
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACKET, self.parse_index_expression)
    
    def register_prefix(self, token_type: TokenType, fn: Callable):
        self.prefix_parse_fns[token_type] = fn
    
    def register_infix(self, token_type: TokenType, fn: Callable):
        self.infix_parse_fns[token_type] = fn
    
    @property
    def current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    @property
    def peek_token(self) -> Token:
        if self.pos + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + 1]
    
    def advance(self) -> Token:
        """Move to next token and return previous."""
        token = self.current_token
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Advance if current token matches, else raise error."""
        if self.current_token.type != token_type:
            raise ParserError(
                f"Expected {token_type.name}, got {self.current_token.type.name}",
                self.current_token
            )
        return self.advance()
    
    def current_precedence(self) -> int:
        return PRECEDENCES.get(self.current_token.type, Precedence.LOWEST)
    
    def peek_precedence(self) -> int:
        return PRECEDENCES.get(self.peek_token.type, Precedence.LOWEST)
    
    # ================================================================
    # PROGRAM AND STATEMENTS
    # ================================================================
    
    def parse_program(self) -> ast.Program:
        """Parse entire program."""
        statements = []
        while self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ast.Program(statements)
    
    def parse_statement(self) -> Optional[ast.Statement]:
        """Parse a single statement."""
        # Skip semicolons
        while self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        if self.current_token.type == TokenType.EOF:
            return None
        
        tt = self.current_token.type
        
        if tt == TokenType.LET:
            return self.parse_let_statement()
        elif tt == TokenType.CONST:
            return self.parse_const_statement()
        elif tt == TokenType.RETURN:
            return self.parse_return_statement()
        elif tt == TokenType.WHILE:
            return self.parse_while_statement()
        elif tt == TokenType.FOR:
            return self.parse_for_statement()
        elif tt == TokenType.BREAK:
            self.advance()
            return ast.BreakStatement()
        elif tt == TokenType.CONTINUE:
            self.advance()
            return ast.ContinueStatement()
        elif tt == TokenType.FN and self.peek_token.type == TokenType.IDENTIFIER:
            return self.parse_function_statement()
        else:
            return self.parse_expression_or_assignment_statement()
    
    def parse_let_statement(self) -> ast.LetStatement:
        """Parse: let name = expression"""
        self.advance()  # consume 'let'
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression(Precedence.LOWEST)
        return ast.LetStatement(name_token.literal, value)
    
    def parse_const_statement(self) -> ast.ConstStatement:
        """Parse: const name = expression"""
        self.advance()  # consume 'const'
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression(Precedence.LOWEST)
        return ast.ConstStatement(name_token.literal, value)
    
    def parse_return_statement(self) -> ast.ReturnStatement:
        """Parse: return [expression]"""
        self.advance()  # consume 'return'
        if self.current_token.type in (TokenType.RBRACE, TokenType.EOF, TokenType.SEMICOLON):
            return ast.ReturnStatement(None)
        value = self.parse_expression(Precedence.LOWEST)
        return ast.ReturnStatement(value)
    
    def parse_while_statement(self) -> ast.WhileStatement:
        """Parse: while condition { body }"""
        self.advance()  # consume 'while'
        condition = self.parse_expression(Precedence.LOWEST)
        body = self.parse_block_statement()
        return ast.WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ast.ForStatement:
        """Parse: for var in iterable { body }"""
        self.advance()  # consume 'for'
        var_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.IN)
        iterable = self.parse_expression(Precedence.LOWEST)
        body = self.parse_block_statement()
        return ast.ForStatement(var_token.literal, iterable, body)
    
    def parse_function_statement(self) -> ast.FunctionStatement:
        """Parse: fn name(params) { body }"""
        self.advance()  # consume 'fn'
        name_token = self.expect(TokenType.IDENTIFIER)
        params = self.parse_function_parameters()
        body = self.parse_block_statement()
        return ast.FunctionStatement(name_token.literal, params, body)
    
    def parse_expression_or_assignment_statement(self) -> ast.Statement:
        """Parse expression statement or assignment."""
        expr = self.parse_expression(Precedence.LOWEST)
        
        # Check for assignment
        if self.current_token.type in (TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN):
            op = self.current_token.literal
            self.advance()
            value = self.parse_expression(Precedence.LOWEST)
            
            if isinstance(expr, ast.Identifier):
                return ast.AssignStatement(expr.name, op, value)
            elif isinstance(expr, ast.IndexExpression):
                return ast.IndexAssignStatement(expr.object, expr.index, value)
            else:
                raise ParserError("Invalid assignment target", self.current_token)
        
        return ast.ExpressionStatement(expr)
    
    def parse_block_statement(self) -> ast.BlockStatement:
        """Parse: { statement* }"""
        self.expect(TokenType.LBRACE)
        statements = []
        
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return ast.BlockStatement(statements)
    
    # ================================================================
    # EXPRESSIONS (Pratt Parser)
    # ================================================================
    
    def parse_expression(self, precedence: int) -> ast.Expression:
        """Parse expression using Pratt parsing."""
        prefix_fn = self.prefix_parse_fns.get(self.current_token.type)
        if not prefix_fn:
            raise ParserError(
                f"No prefix parser for {self.current_token.type.name}",
                self.current_token
            )
        
        left = prefix_fn()
        
        while precedence < self.current_precedence():
            infix_fn = self.infix_parse_fns.get(self.current_token.type)
            if not infix_fn:
                return left
            left = infix_fn(left)
        
        return left
    
    # Prefix parsers
    def parse_identifier(self) -> ast.Identifier:
        token = self.advance()
        return ast.Identifier(token.literal)
    
    def parse_integer(self) -> ast.IntegerLiteral:
        token = self.advance()
        return ast.IntegerLiteral(token.value)
    
    def parse_float(self) -> ast.FloatLiteral:
        token = self.advance()
        return ast.FloatLiteral(token.value)
    
    def parse_string(self) -> ast.StringLiteral:
        token = self.advance()
        return ast.StringLiteral(token.value)
    
    def parse_boolean(self) -> ast.BooleanLiteral:
        token = self.advance()
        return ast.BooleanLiteral(token.type == TokenType.TRUE)
    
    def parse_null(self) -> ast.NullLiteral:
        self.advance()
        return ast.NullLiteral()
    
    def parse_prefix_expression(self) -> ast.UnaryOp:
        token = self.advance()
        operand = self.parse_expression(Precedence.PREFIX)
        return ast.UnaryOp(token.literal, operand)
    
    def parse_grouped_expression(self) -> ast.Expression:
        self.advance()  # consume '('
        expr = self.parse_expression(Precedence.LOWEST)
        self.expect(TokenType.RPAREN)
        return expr
    
    def parse_array_literal(self) -> ast.ArrayLiteral:
        self.advance()  # consume '['
        elements = self.parse_expression_list(TokenType.RBRACKET)
        return ast.ArrayLiteral(elements)
    
    def parse_dict_or_block(self) -> ast.Expression:
        """Parse dict literal { key: value } or just look ahead."""
        # Look ahead to distinguish dict from block
        # Dict has pattern: { expr : expr } or { }
        self.advance()  # consume '{'
        
        if self.current_token.type == TokenType.RBRACE:
            self.advance()
            return ast.DictLiteral([])
        
        # Try to parse as dict
        first_expr = self.parse_expression(Precedence.LOWEST)
        
        if self.current_token.type == TokenType.COLON:
            # It's a dict
            self.advance()  # consume ':'
            first_value = self.parse_expression(Precedence.LOWEST)
            pairs = [(first_expr, first_value)]
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.RBRACE:
                    break
                key = self.parse_expression(Precedence.LOWEST)
                self.expect(TokenType.COLON)
                value = self.parse_expression(Precedence.LOWEST)
                pairs.append((key, value))
            
            self.expect(TokenType.RBRACE)
            return ast.DictLiteral(pairs)
        else:
            raise ParserError("Expected ':' in dictionary literal", self.current_token)
    
    def parse_if_expression(self) -> ast.IfExpression:
        self.advance()  # consume 'if'
        condition = self.parse_expression(Precedence.LOWEST)
        consequence = self.parse_block_statement()
        
        alternative = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            alternative = self.parse_block_statement()
        
        return ast.IfExpression(condition, consequence, alternative)
    
    def parse_function_literal(self) -> ast.FunctionLiteral:
        self.advance()  # consume 'fn'
        params = self.parse_function_parameters()
        body = self.parse_block_statement()
        return ast.FunctionLiteral(params, body)
    
    def parse_function_parameters(self) -> list[str]:
        self.expect(TokenType.LPAREN)
        params = []
        
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENTIFIER).literal)
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER).literal)
        
        self.expect(TokenType.RPAREN)
        return params
    
    # Infix parsers
    def parse_infix_expression(self, left: ast.Expression) -> ast.BinaryOp:
        token = self.advance()
        precedence = PRECEDENCES.get(token.type, Precedence.LOWEST)
        
        # Right associativity for power operator
        if token.type == TokenType.POWER:
            precedence -= 1
        
        right = self.parse_expression(precedence)
        return ast.BinaryOp(token.literal, left, right)
    
    def parse_call_expression(self, function: ast.Expression) -> ast.CallExpression:
        self.advance()  # consume '('
        args = self.parse_expression_list(TokenType.RPAREN)
        return ast.CallExpression(function, args)
    
    def parse_index_expression(self, obj: ast.Expression) -> ast.IndexExpression:
        self.advance()  # consume '['
        index = self.parse_expression(Precedence.LOWEST)
        self.expect(TokenType.RBRACKET)
        return ast.IndexExpression(obj, index)
    
    def parse_expression_list(self, end: TokenType) -> list[ast.Expression]:
        """Parse comma-separated expressions until end token."""
        elements = []
        
        if self.current_token.type != end:
            elements.append(self.parse_expression(Precedence.LOWEST))
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == end:
                    break
                elements.append(self.parse_expression(Precedence.LOWEST))
        
        self.expect(end)
        return elements


def parse(source: str) -> ast.Program:
    """Convenience function to parse source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_program()
