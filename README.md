# Kira Programming Language

<p align="center">
  <strong>A clean, expressive programming language built from scratch</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#language-guide">Language Guide</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## Overview

**Kira** is a dynamically-typed programming language implemented in Python. It features a hand-written lexer, a Pratt parser for elegant expression handling, and a tree-walking interpreter with proper lexical scoping and closures.

This project demonstrates fundamental compiler/interpreter concepts:
- **Lexical Analysis** - Tokenizing source code
- **Parsing** - Building Abstract Syntax Trees using Pratt parsing
- **Evaluation** - Tree-walking interpretation
- **Scope Management** - Lexical scoping with closures
- **First-class Functions** - Functions as values

## Features

### Language Features
- 📦 **Variables & Constants** - `let` and `const` declarations
- 🔢 **Data Types** - integers, floats, strings, booleans, arrays, dictionaries
- 🎯 **Operators** - arithmetic, comparison, logical, string concatenation
- 🔄 **Control Flow** - if/else expressions, while loops, for-in loops
- 📝 **Functions** - first-class functions with closures
- 🧮 **Expressions** - everything is an expression where possible
- 💬 **Comments** - single-line comments with `#`

### Built-in Functions
```
I/O:        print, println, input
Types:      len, type, str, int, float
Arrays:     range, push, pop, first, last, rest, sorted, reversed, join
Dicts:      keys, values
Math:       abs, min, max, sum
Strings:    split, upper, lower, strip, replace
Utility:    contains
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kira-lang.git
cd kira-lang

# No dependencies required - pure Python 3.10+
python kira.py
```

## Quick Start

### Interactive REPL
```bash
python kira.py
```

```
kira> let x = 10
kira> let y = 20
kira> x + y
30
kira> fn greet(name) { "Hello, " + name + "!" }
kira> greet("World")
"Hello, World!"
```

### Run a Script
```bash
python kira.py examples/fibonacci.kira
```

### Evaluate Expression
```bash
python kira.py -e "println(2 ** 10)"
# Output: 1024
```

## Language Guide

### Variables
```javascript
let x = 5           // Mutable variable
const PI = 3.14159  // Immutable constant

x = 10              // OK
PI = 3              // Error: Cannot reassign constant
```

### Data Types
```javascript
// Numbers
let int_num = 42
let float_num = 3.14

// Strings
let greeting = "Hello, World!"
let char = greeting[0]  // "H"

// Booleans
let is_valid = true
let is_empty = false

// Null
let nothing = null

// Arrays
let numbers = [1, 2, 3, 4, 5]
let first = numbers[0]
numbers[0] = 100

// Dictionaries
let person = {"name": "Alice", "age": 30}
let name = person["name"]
```

### Operators
```javascript
// Arithmetic
5 + 3    // 8
10 - 4   // 6
3 * 4    // 12
15 / 4   // 3.75
17 % 5   // 2
2 ** 10  // 1024

// Comparison
5 == 5   // true
5 != 3   // true
5 < 10   // true
5 >= 5   // true

// Logical
true and false  // false
true or false   // true
not true        // false

// String concatenation
"Hello, " + "World!"  // "Hello, World!"
```

### Control Flow
```javascript
// If expression (returns a value)
let status = if age >= 18 { "adult" } else { "minor" }

// If statement
if x > 0 {
    println("positive")
} else {
    println("non-positive")
}

// While loop
let i = 0
while i < 5 {
    println(i)
    i = i + 1
}

// For loop
for x in [1, 2, 3, 4, 5] {
    println(x * x)
}

for i in range(10) {
    println(i)
}
```

### Functions
```javascript
// Named function
fn add(a, b) {
    return a + b
}

// Implicit return (last expression)
fn multiply(a, b) {
    a * b
}

// Anonymous function
let square = fn(x) { x * x }

// Higher-order functions
fn apply_twice(f, x) {
    f(f(x))
}
apply_twice(square, 3)  // 81

// Closures
fn make_adder(n) {
    fn(x) { x + n }
}
let add5 = make_adder(5)
add5(10)  // 15
```

### Recursion
```javascript
fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

fn fib(n) {
    if n <= 1 { return n }
    fib(n - 1) + fib(n - 2)
}
```

## Architecture

```
Source Code
    │
    ▼
┌─────────┐
│  Lexer  │  → Tokenizes source into tokens
└────┬────┘
     │
     ▼
┌─────────┐
│ Parser  │  → Builds Abstract Syntax Tree (Pratt parser)
└────┬────┘
     │
     ▼
┌───────────┐
│ Evaluator │  → Tree-walking interpreter
└───────────┘
     │
     ▼
  Result
```

### Components

| Component | File | Description |
|-----------|------|-------------|
| Tokens | `src/tokens.py` | Token type definitions |
| Lexer | `src/lexer.py` | Tokenizer implementation |
| AST | `src/ast_nodes.py` | Abstract Syntax Tree node definitions |
| Parser | `src/parser.py` | Pratt parser implementation |
| Evaluator | `src/evaluator.py` | Tree-walking interpreter |
| Environment | `src/environment.py` | Scope and variable management |
| Builtins | `src/builtins.py` | Built-in functions |
| REPL | `src/repl.py` | Interactive shell |

### Key Design Decisions

1. **Pratt Parsing** - Elegant handling of operator precedence without complex grammar rules
2. **Tree-Walking Interpreter** - Simple and educational (vs. bytecode compilation)
3. **Lexical Scoping** - Closures capture their environment correctly
4. **Expression-Oriented** - `if` returns values, enabling functional patterns
5. **Dynamic Typing** - Simpler implementation, focus on core concepts

## Examples

See the `examples/` directory:
- `hello.kira` - Hello World
- `fibonacci.kira` - Recursive and iterative Fibonacci
- `quicksort.kira` - Quicksort implementation
- `closures.kira` - Closures and higher-order functions

## Running Tests

```bash
python -m pytest tests/ -v
```

## Extending Kira

### Adding a Built-in Function

```python
# In src/builtins.py

def builtin_my_func(x, y):
    """Description of my function."""
    return x + y

BUILTINS['my_func'] = BuiltinFunction('my_func', builtin_my_func)
```

### Adding a New Operator

1. Add token type in `tokens.py`
2. Add lexer rule in `lexer.py`
3. Add precedence in `parser.py`
4. Add evaluation in `evaluator.py`

## License

MIT License - see [LICENSE](LICENSE)

## Author

**Khalil Limem**
