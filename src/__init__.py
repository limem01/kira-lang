"""
Kira Programming Language
=========================

A clean, expressive programming language built from scratch.

Components:
- Lexer: Tokenizes source code
- Parser: Builds Abstract Syntax Tree (Pratt parser)
- Evaluator: Tree-walking interpreter
- REPL: Interactive shell

Usage:
    from kira.src import evaluate
    result = evaluate("let x = 5 + 3; x * 2")
    
    # Or run REPL
    from kira.src.repl import run_repl
    run_repl()
"""

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError, parse
from .evaluator import Evaluator, evaluate
from .environment import Environment
from .builtins import BUILTINS

__version__ = "1.0.0"
__author__ = "Khalil Limem"

__all__ = [
    'Lexer', 'LexerError',
    'Parser', 'ParserError', 'parse',
    'Evaluator', 'evaluate',
    'Environment',
    'BUILTINS',
]
