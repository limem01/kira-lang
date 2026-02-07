"""
Kira Language - Evaluator (Interpreter)
========================================
The evaluator walks the AST and executes each node.
This is where the actual computation happens.

Flow:
    Source → [Lexer] → Tokens → [Parser] → AST → [Evaluator] → Result
"""

from typing import Any, Optional
from dataclasses import dataclass
from . import ast_nodes as ast
from .environment import Environment
from .builtins import BUILTINS, BuiltinFunction, KiraRuntimeError, kira_str


@dataclass
class Function:
    """User-defined function."""
    parameters: list[str]
    body: ast.BlockStatement
    env: Environment  # Closure environment
    name: Optional[str] = None
    
    def __repr__(self):
        name = self.name or "anonymous"
        return f"<function {name}>"


class ReturnValue(Exception):
    """Used to implement return statements (unwind call stack)."""
    def __init__(self, value: Any):
        self.value = value


class BreakSignal(Exception):
    """Used to implement break statements."""
    pass


class ContinueSignal(Exception):
    """Used to implement continue statements."""
    pass


class Evaluator:
    """
    Tree-walking interpreter for Kira language.
    
    Usage:
        evaluator = Evaluator()
        result = evaluator.eval(ast, environment)
    """
    
    def eval(self, node: ast.Node, env: Environment) -> Any:
        """Evaluate an AST node in the given environment."""
        
        # Dispatch based on node type
        method_name = f'eval_{type(node).__name__}'
        method = getattr(self, method_name, None)
        
        if method is None:
            raise KiraRuntimeError(f"Unknown node type: {type(node).__name__}")
        
        return method(node, env)
    
    # ================================================================
    # PROGRAM AND STATEMENTS
    # ================================================================
    
    def eval_Program(self, node: ast.Program, env: Environment) -> Any:
        """Evaluate all statements in program."""
        result = None
        for stmt in node.statements:
            result = self.eval(stmt, env)
        return result
    
    def eval_BlockStatement(self, node: ast.BlockStatement, env: Environment) -> Any:
        """Evaluate statements in a block."""
        result = None
        for stmt in node.statements:
            result = self.eval(stmt, env)
        return result
    
    def eval_ExpressionStatement(self, node: ast.ExpressionStatement, env: Environment) -> Any:
        """Evaluate expression and return its value."""
        return self.eval(node.expression, env)
    
    def eval_LetStatement(self, node: ast.LetStatement, env: Environment) -> Any:
        """Evaluate let declaration."""
        value = self.eval(node.value, env)
        env.set(node.name, value, is_const=False)
        return value
    
    def eval_ConstStatement(self, node: ast.ConstStatement, env: Environment) -> Any:
        """Evaluate const declaration."""
        value = self.eval(node.value, env)
        env.set(node.name, value, is_const=True)
        return value
    
    def eval_AssignStatement(self, node: ast.AssignStatement, env: Environment) -> Any:
        """Evaluate assignment."""
        value = self.eval(node.value, env)
        
        if node.operator == "=":
            env.assign(node.name, value)
        elif node.operator == "+=":
            current, found = env.get(node.name)
            if not found:
                raise KiraRuntimeError(f"Undefined variable: {node.name}")
            env.assign(node.name, current + value)
        elif node.operator == "-=":
            current, found = env.get(node.name)
            if not found:
                raise KiraRuntimeError(f"Undefined variable: {node.name}")
            env.assign(node.name, current - value)
        
        return value
    
    def eval_IndexAssignStatement(self, node: ast.IndexAssignStatement, env: Environment) -> Any:
        """Evaluate index assignment like arr[0] = value."""
        obj = self.eval(node.object, env)
        index = self.eval(node.index, env)
        value = self.eval(node.value, env)
        
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise KiraRuntimeError("Array index must be integer")
            if index < 0 or index >= len(obj):
                raise KiraRuntimeError(f"Array index out of bounds: {index}")
            obj[index] = value
        elif isinstance(obj, dict):
            obj[index] = value
        else:
            raise KiraRuntimeError("Cannot index into this type")
        
        return value
    
    def eval_ReturnStatement(self, node: ast.ReturnStatement, env: Environment) -> Any:
        """Evaluate return statement."""
        value = None
        if node.value:
            value = self.eval(node.value, env)
        raise ReturnValue(value)
    
    def eval_WhileStatement(self, node: ast.WhileStatement, env: Environment) -> Any:
        """Evaluate while loop."""
        while self.is_truthy(self.eval(node.condition, env)):
            try:
                self.eval(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return None
    
    def eval_ForStatement(self, node: ast.ForStatement, env: Environment) -> Any:
        """Evaluate for loop."""
        iterable = self.eval(node.iterable, env)
        
        if not hasattr(iterable, '__iter__'):
            raise KiraRuntimeError(f"Cannot iterate over {type(iterable).__name__}")
        
        for item in iterable:
            env.set(node.variable, item)
            try:
                self.eval(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        
        return None
    
    def eval_BreakStatement(self, node: ast.BreakStatement, env: Environment) -> Any:
        raise BreakSignal()
    
    def eval_ContinueStatement(self, node: ast.ContinueStatement, env: Environment) -> Any:
        raise ContinueSignal()
    
    def eval_FunctionStatement(self, node: ast.FunctionStatement, env: Environment) -> Any:
        """Evaluate function declaration."""
        func = Function(
            parameters=node.parameters,
            body=node.body,
            env=env,
            name=node.name
        )
        env.set(node.name, func)
        return func
    
    # ================================================================
    # EXPRESSIONS
    # ================================================================
    
    def eval_IntegerLiteral(self, node: ast.IntegerLiteral, env: Environment) -> int:
        return node.value
    
    def eval_FloatLiteral(self, node: ast.FloatLiteral, env: Environment) -> float:
        return node.value
    
    def eval_StringLiteral(self, node: ast.StringLiteral, env: Environment) -> str:
        return node.value
    
    def eval_BooleanLiteral(self, node: ast.BooleanLiteral, env: Environment) -> bool:
        return node.value
    
    def eval_NullLiteral(self, node: ast.NullLiteral, env: Environment) -> None:
        return None
    
    def eval_ArrayLiteral(self, node: ast.ArrayLiteral, env: Environment) -> list:
        return [self.eval(elem, env) for elem in node.elements]
    
    def eval_DictLiteral(self, node: ast.DictLiteral, env: Environment) -> dict:
        result = {}
        for key_node, value_node in node.pairs:
            key = self.eval(key_node, env)
            value = self.eval(value_node, env)
            result[key] = value
        return result
    
    def eval_Identifier(self, node: ast.Identifier, env: Environment) -> Any:
        """Look up identifier in environment or builtins."""
        value, found = env.get(node.name)
        if found:
            return value
        
        if node.name in BUILTINS:
            return BUILTINS[node.name]
        
        raise KiraRuntimeError(f"Undefined variable: {node.name}")
    
    def eval_IndexExpression(self, node: ast.IndexExpression, env: Environment) -> Any:
        """Evaluate index expression like arr[0] or dict["key"]."""
        obj = self.eval(node.object, env)
        index = self.eval(node.index, env)
        
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise KiraRuntimeError("Array index must be integer")
            if index < 0 or index >= len(obj):
                raise KiraRuntimeError(f"Array index out of bounds: {index}")
            return obj[index]
        elif isinstance(obj, dict):
            if index not in obj:
                raise KiraRuntimeError(f"Key not found: {index}")
            return obj[index]
        elif isinstance(obj, str):
            if not isinstance(index, int):
                raise KiraRuntimeError("String index must be integer")
            if index < 0 or index >= len(obj):
                raise KiraRuntimeError(f"String index out of bounds: {index}")
            return obj[index]
        else:
            raise KiraRuntimeError(f"Cannot index into {type(obj).__name__}")
    
    def eval_BinaryOp(self, node: ast.BinaryOp, env: Environment) -> Any:
        """Evaluate binary operation."""
        # Short-circuit evaluation for and/or
        if node.operator == 'and':
            left = self.eval(node.left, env)
            if not self.is_truthy(left):
                return left
            return self.eval(node.right, env)
        
        if node.operator == 'or':
            left = self.eval(node.left, env)
            if self.is_truthy(left):
                return left
            return self.eval(node.right, env)
        
        left = self.eval(node.left, env)
        right = self.eval(node.right, env)
        
        op = node.operator
        
        # Arithmetic
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return kira_str(left) + kira_str(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, list) and isinstance(right, int):
                return left * right
            return left * right
        if op == '/':
            if right == 0:
                raise KiraRuntimeError("Division by zero")
            return left / right
        if op == '%':
            if right == 0:
                raise KiraRuntimeError("Modulo by zero")
            return left % right
        if op == '**':
            return left ** right
        
        # Comparison
        if op == '==':
            return left == right
        if op == '!=':
            return left != right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op == '<=':
            return left <= right
        if op == '>=':
            return left >= right
        
        raise KiraRuntimeError(f"Unknown operator: {op}")
    
    def eval_UnaryOp(self, node: ast.UnaryOp, env: Environment) -> Any:
        """Evaluate unary operation."""
        operand = self.eval(node.operand, env)
        
        if node.operator == '-':
            return -operand
        if node.operator == 'not':
            return not self.is_truthy(operand)
        
        raise KiraRuntimeError(f"Unknown unary operator: {node.operator}")
    
    def eval_IfExpression(self, node: ast.IfExpression, env: Environment) -> Any:
        """Evaluate if expression."""
        condition = self.eval(node.condition, env)
        
        if self.is_truthy(condition):
            return self.eval(node.consequence, env)
        elif node.alternative:
            return self.eval(node.alternative, env)
        
        return None
    
    def eval_FunctionLiteral(self, node: ast.FunctionLiteral, env: Environment) -> Function:
        """Evaluate function literal (creates closure)."""
        return Function(
            parameters=node.parameters,
            body=node.body,
            env=env,
            name=node.name
        )
    
    def eval_CallExpression(self, node: ast.CallExpression, env: Environment) -> Any:
        """Evaluate function call."""
        func = self.eval(node.function, env)
        args = [self.eval(arg, env) for arg in node.arguments]
        
        return self.apply_function(func, args)
    
    # ================================================================
    # HELPERS
    # ================================================================
    
    def apply_function(self, func: Any, args: list[Any]) -> Any:
        """Apply a function to arguments."""
        if isinstance(func, BuiltinFunction):
            try:
                return func.fn(*args)
            except TypeError as e:
                raise KiraRuntimeError(f"Error calling {func.name}: {e}")
        
        if isinstance(func, Function):
            if len(args) != len(func.parameters):
                raise KiraRuntimeError(
                    f"Expected {len(func.parameters)} arguments, got {len(args)}"
                )
            
            # Create new environment for function call
            func_env = Environment(parent=func.env)
            
            # Bind parameters to arguments
            for param, arg in zip(func.parameters, args):
                func_env.set(param, arg)
            
            # Execute function body
            try:
                result = self.eval(func.body, func_env)
                return result
            except ReturnValue as rv:
                return rv.value
        
        raise KiraRuntimeError(f"Cannot call {type(func).__name__}")
    
    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, int) or isinstance(value, float):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        if isinstance(value, dict):
            return len(value) > 0
        return True


def evaluate(source: str) -> Any:
    """Convenience function to evaluate source code."""
    from .parser import parse
    program = parse(source)
    evaluator = Evaluator()
    env = Environment()
    return evaluator.eval(program, env)
