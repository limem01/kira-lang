"""
Tests for Kira Language Interpreter
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import evaluate, Lexer, Parser, Evaluator, Environment


def test_evaluate(code, expected):
    """Helper to test evaluation."""
    result = evaluate(code)
    assert result == expected, f"Expected {expected}, got {result}"
    return True


def run_tests():
    """Run all tests."""
    tests_passed = 0
    tests_failed = 0
    
    # Basic arithmetic
    tests = [
        ("5", 5),
        ("5 + 5", 10),
        ("5 - 3", 2),
        ("3 * 4", 12),
        ("10 / 4", 2.5),
        ("10 % 3", 1),
        ("2 ** 3", 8),
        ("-5", -5),
        ("--5", 5),
        ("(2 + 3) * 4", 20),
        
        # Comparisons
        ("5 == 5", True),
        ("5 != 3", True),
        ("5 < 10", True),
        ("5 > 10", False),
        ("5 <= 5", True),
        ("5 >= 6", False),
        
        # Booleans and logic
        ("true", True),
        ("false", False),
        ("not true", False),
        ("true and false", False),
        ("true or false", True),
        
        # Strings
        ('"hello"', "hello"),
        ('"hello" + " " + "world"', "hello world"),
        ('len("hello")', 5),
        
        # Variables
        ("let x = 5; x", 5),
        ("let x = 5; let y = 3; x + y", 8),
        ("let x = 5; x = 10; x", 10),
        
        # Arrays
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][2]", 3),
        ("len([1, 2, 3])", 3),
        ("let a = [1, 2]; push(a, 3); a[2]", 3),
        
        # Dictionaries
        ('{"a": 1}["a"]', 1),
        ('let d = {"x": 10}; d["x"]', 10),
        
        # Functions
        ("fn() { 5 }()", 5),
        ("fn(x) { x * 2 }(5)", 10),
        ("let double = fn(x) { x * 2 }; double(5)", 10),
        ("fn add(a, b) { a + b }; add(2, 3)", 5),
        
        # Closures
        ("let f = fn(x) { fn(y) { x + y } }; let add5 = f(5); add5(3)", 8),
        
        # If expressions
        ("if true { 1 } else { 2 }", 1),
        ("if false { 1 } else { 2 }", 2),
        ("if 5 > 3 { 10 } else { 20 }", 10),
        
        # Loops
        ("let sum = 0; for i in [1,2,3,4,5] { sum = sum + i }; sum", 15),
        ("let i = 0; let sum = 0; while i < 5 { sum = sum + i; i = i + 1 }; sum", 10),
        
        # Built-ins
        ("type(5)", "integer"),
        ("type(3.14)", "float"),
        ("type(true)", "boolean"),
        ('type("hi")', "string"),
        ("abs(-5)", 5),
        ("min(3, 1, 2)", 1),
        ("max(3, 1, 2)", 3),
        ("sum([1, 2, 3])", 6),
    ]
    
    for code, expected in tests:
        try:
            test_evaluate(code, expected)
            tests_passed += 1
            print(f"PASS: {code}")
        except AssertionError as e:
            tests_failed += 1
            print(f"FAIL: {code}")
            print(f"  {e}")
        except Exception as e:
            tests_failed += 1
            print(f"FAIL: {code}")
            print(f"  Error: {e}")
    
    print(f"\n{'='*50}")
    print(f"Tests: {tests_passed} passed, {tests_failed} failed")
    
    return tests_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
