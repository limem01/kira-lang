"""
Kira Language - Abstract Syntax Tree (AST) Nodes
=================================================
The AST is a tree representation of the program structure.
Each node type represents a different language construct.

Example: "let x = 5 + 3" becomes:
    LetStatement(
        name="x",
        value=BinaryOp(
            op="+",
            left=IntegerLiteral(5),
            right=IntegerLiteral(3)
        )
    )
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from abc import ABC, abstractmethod


class Node(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def __repr__(self) -> str:
        pass


class Expression(Node):
    """Base class for expression nodes (produce values)."""
    pass


class Statement(Node):
    """Base class for statement nodes (perform actions)."""
    pass


# ============================================================
# LITERAL EXPRESSIONS
# ============================================================

@dataclass
class IntegerLiteral(Expression):
    """Integer literal like 42"""
    value: int
    
    def __repr__(self):
        return f"IntegerLiteral({self.value})"


@dataclass
class FloatLiteral(Expression):
    """Float literal like 3.14"""
    value: float
    
    def __repr__(self):
        return f"FloatLiteral({self.value})"


@dataclass
class StringLiteral(Expression):
    """String literal like "hello" """
    value: str
    
    def __repr__(self):
        return f"StringLiteral({self.value!r})"


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal: true or false"""
    value: bool
    
    def __repr__(self):
        return f"BooleanLiteral({self.value})"


@dataclass
class NullLiteral(Expression):
    """Null literal"""
    
    def __repr__(self):
        return "NullLiteral()"


@dataclass
class ArrayLiteral(Expression):
    """Array literal like [1, 2, 3]"""
    elements: list[Expression]
    
    def __repr__(self):
        return f"ArrayLiteral({self.elements})"


@dataclass
class DictLiteral(Expression):
    """Dictionary literal like {a: 1, b: 2}"""
    pairs: list[tuple[Expression, Expression]]
    
    def __repr__(self):
        return f"DictLiteral({self.pairs})"


# ============================================================
# IDENTIFIER AND ACCESS EXPRESSIONS
# ============================================================

@dataclass
class Identifier(Expression):
    """Variable reference like x"""
    name: str
    
    def __repr__(self):
        return f"Identifier({self.name})"


@dataclass
class IndexExpression(Expression):
    """Index access like arr[0] or dict["key"]"""
    object: Expression
    index: Expression
    
    def __repr__(self):
        return f"IndexExpression({self.object}[{self.index}])"


# ============================================================
# OPERATOR EXPRESSIONS
# ============================================================

@dataclass
class BinaryOp(Expression):
    """Binary operation like a + b"""
    operator: str
    left: Expression
    right: Expression
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(Expression):
    """Unary operation like -x or not x"""
    operator: str
    operand: Expression
    
    def __repr__(self):
        return f"UnaryOp({self.operator}{self.operand})"


@dataclass
class ComparisonOp(Expression):
    """Comparison like a < b < c (chained)"""
    operators: list[str]
    operands: list[Expression]
    
    def __repr__(self):
        return f"ComparisonOp({self.operands}, {self.operators})"


# ============================================================
# FUNCTION EXPRESSIONS
# ============================================================

@dataclass
class FunctionLiteral(Expression):
    """Function definition: fn(a, b) { ... }"""
    parameters: list[str]
    body: 'BlockStatement'
    name: Optional[str] = None  # For named functions
    
    def __repr__(self):
        name = self.name or "anonymous"
        return f"FunctionLiteral({name}({', '.join(self.parameters)}))"


@dataclass
class CallExpression(Expression):
    """Function call like func(a, b)"""
    function: Expression
    arguments: list[Expression]
    
    def __repr__(self):
        return f"CallExpression({self.function}({self.arguments}))"


# ============================================================
# CONDITIONAL EXPRESSIONS
# ============================================================

@dataclass
class IfExpression(Expression):
    """
    If expression (can be used as expression):
    if condition { ... } else { ... }
    """
    condition: Expression
    consequence: 'BlockStatement'
    alternative: Optional['BlockStatement'] = None
    
    def __repr__(self):
        return f"IfExpression({self.condition})"


# ============================================================
# STATEMENTS
# ============================================================

@dataclass
class Program(Node):
    """Root node containing all statements"""
    statements: list[Statement]
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


@dataclass
class BlockStatement(Statement):
    """Block of statements: { stmt1; stmt2; }"""
    statements: list[Statement]
    
    def __repr__(self):
        return f"BlockStatement({len(self.statements)} statements)"


@dataclass
class LetStatement(Statement):
    """Variable declaration: let x = expr"""
    name: str
    value: Expression
    
    def __repr__(self):
        return f"LetStatement({self.name} = {self.value})"


@dataclass
class ConstStatement(Statement):
    """Constant declaration: const x = expr"""
    name: str
    value: Expression
    
    def __repr__(self):
        return f"ConstStatement({self.name} = {self.value})"


@dataclass
class AssignStatement(Statement):
    """Assignment: x = expr or x += expr"""
    name: str
    operator: str  # "=", "+=", "-="
    value: Expression
    
    def __repr__(self):
        return f"AssignStatement({self.name} {self.operator} {self.value})"


@dataclass
class IndexAssignStatement(Statement):
    """Index assignment: arr[0] = expr"""
    object: Expression
    index: Expression
    value: Expression
    
    def __repr__(self):
        return f"IndexAssignStatement({self.object}[{self.index}] = {self.value})"


@dataclass
class ExpressionStatement(Statement):
    """Expression used as statement"""
    expression: Expression
    
    def __repr__(self):
        return f"ExpressionStatement({self.expression})"


@dataclass
class ReturnStatement(Statement):
    """Return statement: return expr"""
    value: Optional[Expression] = None
    
    def __repr__(self):
        return f"ReturnStatement({self.value})"


@dataclass
class WhileStatement(Statement):
    """While loop: while condition { ... }"""
    condition: Expression
    body: BlockStatement
    
    def __repr__(self):
        return f"WhileStatement({self.condition})"


@dataclass
class ForStatement(Statement):
    """For loop: for x in iterable { ... }"""
    variable: str
    iterable: Expression
    body: BlockStatement
    
    def __repr__(self):
        return f"ForStatement({self.variable} in {self.iterable})"


@dataclass
class BreakStatement(Statement):
    """Break out of loop"""
    
    def __repr__(self):
        return "BreakStatement()"


@dataclass
class ContinueStatement(Statement):
    """Continue to next iteration"""
    
    def __repr__(self):
        return "ContinueStatement()"


@dataclass
class FunctionStatement(Statement):
    """Named function declaration: fn name(args) { ... }"""
    name: str
    parameters: list[str]
    body: BlockStatement
    
    def __repr__(self):
        return f"FunctionStatement({self.name}({', '.join(self.parameters)}))"
