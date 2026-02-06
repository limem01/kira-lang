"""
Kira Language - Environment (Scope Management)
===============================================
The environment stores variable bindings and handles scope.
Each function call creates a new environment with the outer scope as parent.
"""

from typing import Any, Optional


class Environment:
    """
    Environment for storing variable bindings.
    Implements lexical scoping through parent chain.
    
    Example:
        global_env = Environment()
        global_env.set("x", 10)
        
        func_env = Environment(parent=global_env)
        func_env.set("y", 20)
        
        func_env.get("x")  # 10 (from parent)
        func_env.get("y")  # 20 (local)
    """
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.store: dict[str, Any] = {}
        self.constants: set[str] = set()
        self.parent = parent
    
    def get(self, name: str) -> tuple[Any, bool]:
        """
        Get a variable's value.
        Returns (value, found) tuple.
        Searches local scope first, then parent scopes.
        """
        if name in self.store:
            return self.store[name], True
        if self.parent:
            return self.parent.get(name)
        return None, False
    
    def set(self, name: str, value: Any, is_const: bool = False) -> Any:
        """
        Set a variable in the current scope.
        """
        if name in self.constants:
            raise RuntimeError(f"Cannot reassign constant '{name}'")
        
        self.store[name] = value
        if is_const:
            self.constants.add(name)
        return value
    
    def assign(self, name: str, value: Any) -> Any:
        """
        Assign to an existing variable (searches parent scopes).
        """
        if name in self.store:
            if name in self.constants:
                raise RuntimeError(f"Cannot reassign constant '{name}'")
            self.store[name] = value
            return value
        if self.parent:
            return self.parent.assign(name, value)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def exists(self, name: str) -> bool:
        """Check if variable exists in any scope."""
        if name in self.store:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


def create_global_environment() -> Environment:
    """Create the global environment with built-in values."""
    env = Environment()
    return env
