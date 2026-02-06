"""
Kira Language - Built-in Functions
===================================
These functions are available globally in every Kira program.
"""

from typing import Any, Callable
from dataclasses import dataclass


@dataclass
class BuiltinFunction:
    """Wrapper for built-in functions."""
    name: str
    fn: Callable
    
    def __repr__(self):
        return f"<builtin function {self.name}>"


class KiraRuntimeError(Exception):
    """Runtime error in Kira program."""
    pass


# ============================================================
# BUILT-IN FUNCTION IMPLEMENTATIONS
# ============================================================

def builtin_print(*args) -> None:
    """Print values to stdout."""
    output = ' '.join(kira_str(arg) for arg in args)
    print(output)
    return None


def builtin_println(*args) -> None:
    """Print values with newline."""
    builtin_print(*args)
    return None


def builtin_len(obj) -> int:
    """Get length of string, array, or dict."""
    if isinstance(obj, str):
        return len(obj)
    if isinstance(obj, list):
        return len(obj)
    if isinstance(obj, dict):
        return len(obj)
    raise KiraRuntimeError(f"len() not supported for {type(obj).__name__}")


def builtin_type(obj) -> str:
    """Get type name of value."""
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "boolean"
    if isinstance(obj, int):
        return "integer"
    if isinstance(obj, float):
        return "float"
    if isinstance(obj, str):
        return "string"
    if isinstance(obj, list):
        return "array"
    if isinstance(obj, dict):
        return "dict"
    if isinstance(obj, BuiltinFunction):
        return "builtin"
    if hasattr(obj, 'parameters'):  # Function
        return "function"
    return "unknown"


def builtin_str(obj) -> str:
    """Convert value to string."""
    return kira_str(obj)


def builtin_int(obj) -> int:
    """Convert value to integer."""
    if isinstance(obj, bool):
        return 1 if obj else 0
    if isinstance(obj, (int, float)):
        return int(obj)
    if isinstance(obj, str):
        try:
            return int(obj)
        except ValueError:
            raise KiraRuntimeError(f"Cannot convert '{obj}' to integer")
    raise KiraRuntimeError(f"Cannot convert {type(obj).__name__} to integer")


def builtin_float(obj) -> float:
    """Convert value to float."""
    if isinstance(obj, bool):
        return 1.0 if obj else 0.0
    if isinstance(obj, (int, float)):
        return float(obj)
    if isinstance(obj, str):
        try:
            return float(obj)
        except ValueError:
            raise KiraRuntimeError(f"Cannot convert '{obj}' to float")
    raise KiraRuntimeError(f"Cannot convert {type(obj).__name__} to float")


def builtin_input(prompt="") -> str:
    """Read input from user."""
    return input(prompt)


def builtin_range(*args) -> list:
    """Generate a range of integers."""
    if len(args) == 1:
        return list(range(args[0]))
    elif len(args) == 2:
        return list(range(args[0], args[1]))
    elif len(args) == 3:
        return list(range(args[0], args[1], args[2]))
    raise KiraRuntimeError("range() takes 1 to 3 arguments")


def builtin_push(arr, value) -> list:
    """Append value to array (mutates and returns array)."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("push() requires an array")
    arr.append(value)
    return arr


def builtin_pop(arr) -> Any:
    """Remove and return last element of array."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("pop() requires an array")
    if len(arr) == 0:
        raise KiraRuntimeError("pop() on empty array")
    return arr.pop()


def builtin_first(arr) -> Any:
    """Get first element of array."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("first() requires an array")
    if len(arr) == 0:
        raise KiraRuntimeError("first() on empty array")
    return arr[0]


def builtin_last(arr) -> Any:
    """Get last element of array."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("last() requires an array")
    if len(arr) == 0:
        raise KiraRuntimeError("last() on empty array")
    return arr[-1]


def builtin_rest(arr) -> list:
    """Get array without first element."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("rest() requires an array")
    return arr[1:]


def builtin_keys(d) -> list:
    """Get keys of dictionary."""
    if not isinstance(d, dict):
        raise KiraRuntimeError("keys() requires a dict")
    return list(d.keys())


def builtin_values(d) -> list:
    """Get values of dictionary."""
    if not isinstance(d, dict):
        raise KiraRuntimeError("values() requires a dict")
    return list(d.values())


def builtin_abs(x) -> int | float:
    """Absolute value."""
    if isinstance(x, (int, float)):
        return abs(x)
    raise KiraRuntimeError("abs() requires a number")


def builtin_min(*args) -> Any:
    """Minimum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)


def builtin_max(*args) -> Any:
    """Maximum value."""
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)


def builtin_sum(arr) -> int | float:
    """Sum of array elements."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("sum() requires an array")
    return sum(arr)


def builtin_sorted(arr) -> list:
    """Return sorted copy of array."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("sorted() requires an array")
    return sorted(arr)


def builtin_reversed(arr) -> list:
    """Return reversed copy of array."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("reversed() requires an array")
    return list(reversed(arr))


def builtin_join(arr, sep="") -> str:
    """Join array elements into string."""
    if not isinstance(arr, list):
        raise KiraRuntimeError("join() requires an array")
    return sep.join(str(x) for x in arr)


def builtin_split(s, sep=None) -> list:
    """Split string into array."""
    if not isinstance(s, str):
        raise KiraRuntimeError("split() requires a string")
    return s.split(sep)


def builtin_upper(s) -> str:
    """Convert string to uppercase."""
    if not isinstance(s, str):
        raise KiraRuntimeError("upper() requires a string")
    return s.upper()


def builtin_lower(s) -> str:
    """Convert string to lowercase."""
    if not isinstance(s, str):
        raise KiraRuntimeError("lower() requires a string")
    return s.lower()


def builtin_strip(s) -> str:
    """Remove whitespace from both ends of string."""
    if not isinstance(s, str):
        raise KiraRuntimeError("strip() requires a string")
    return s.strip()


def builtin_replace(s, old, new) -> str:
    """Replace occurrences in string."""
    if not isinstance(s, str):
        raise KiraRuntimeError("replace() requires a string")
    return s.replace(old, new)


def builtin_contains(container, item) -> bool:
    """Check if container contains item."""
    if isinstance(container, str):
        return item in container
    if isinstance(container, list):
        return item in container
    if isinstance(container, dict):
        return item in container
    raise KiraRuntimeError("contains() requires string, array, or dict")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def kira_str(obj) -> str:
    """Convert Kira value to string representation."""
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        elements = ', '.join(kira_repr(e) for e in obj)
        return f"[{elements}]"
    if isinstance(obj, dict):
        pairs = ', '.join(f"{kira_repr(k)}: {kira_repr(v)}" for k, v in obj.items())
        return f"{{{pairs}}}"
    if isinstance(obj, BuiltinFunction):
        return f"<builtin function {obj.name}>"
    if hasattr(obj, 'parameters'):
        name = getattr(obj, 'name', 'anonymous')
        return f"<function {name}>"
    return str(obj)


def kira_repr(obj) -> str:
    """Convert Kira value to repr (with quotes for strings)."""
    if isinstance(obj, str):
        return f'"{obj}"'
    return kira_str(obj)


# ============================================================
# BUILTINS REGISTRY
# ============================================================

BUILTINS = {
    # I/O
    'print': BuiltinFunction('print', builtin_print),
    'println': BuiltinFunction('println', builtin_println),
    'input': BuiltinFunction('input', builtin_input),
    
    # Type functions
    'len': BuiltinFunction('len', builtin_len),
    'type': BuiltinFunction('type', builtin_type),
    'str': BuiltinFunction('str', builtin_str),
    'int': BuiltinFunction('int', builtin_int),
    'float': BuiltinFunction('float', builtin_float),
    
    # Array functions
    'range': BuiltinFunction('range', builtin_range),
    'push': BuiltinFunction('push', builtin_push),
    'pop': BuiltinFunction('pop', builtin_pop),
    'first': BuiltinFunction('first', builtin_first),
    'last': BuiltinFunction('last', builtin_last),
    'rest': BuiltinFunction('rest', builtin_rest),
    'sorted': BuiltinFunction('sorted', builtin_sorted),
    'reversed': BuiltinFunction('reversed', builtin_reversed),
    'join': BuiltinFunction('join', builtin_join),
    
    # Dict functions
    'keys': BuiltinFunction('keys', builtin_keys),
    'values': BuiltinFunction('values', builtin_values),
    
    # Math functions
    'abs': BuiltinFunction('abs', builtin_abs),
    'min': BuiltinFunction('min', builtin_min),
    'max': BuiltinFunction('max', builtin_max),
    'sum': BuiltinFunction('sum', builtin_sum),
    
    # String functions
    'split': BuiltinFunction('split', builtin_split),
    'upper': BuiltinFunction('upper', builtin_upper),
    'lower': BuiltinFunction('lower', builtin_lower),
    'strip': BuiltinFunction('strip', builtin_strip),
    'replace': BuiltinFunction('replace', builtin_replace),
    
    # Utility
    'contains': BuiltinFunction('contains', builtin_contains),
}
