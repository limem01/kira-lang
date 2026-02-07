#!/usr/bin/env python3
"""
Kira Programming Language
=========================

Usage:
    python kira.py              - Start REPL
    python kira.py script.kira  - Run a script file
    python kira.py -e "code"    - Evaluate code string
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError
from src.evaluator import Evaluator
from src.environment import Environment
from src.builtins import KiraRuntimeError
from src.repl import run_repl


def run_file(filepath: str) -> int:
    """Run a Kira script file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return 1
    except IOError as e:
        print(f"Error reading file: {e}")
        return 1
    
    return run_source(source)


def run_source(source: str) -> int:
    """Run Kira source code."""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        program = parser.parse_program()
        
        evaluator = Evaluator()
        env = Environment()
        evaluator.eval(program, env)
        
        return 0
    
    except LexerError as e:
        print(f"Lexer Error at line {e.line}, column {e.column}:")
        print(f"  {e.message}")
        return 1
    
    except ParserError as e:
        print(f"Parse Error at line {e.token.line}:")
        print(f"  {e.message}")
        return 1
    
    except KiraRuntimeError as e:
        print(f"Runtime Error: {e}")
        return 1
    
    except Exception as e:
        print(f"Internal Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Kira Programming Language Interpreter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kira                    Start interactive REPL
  kira script.kira        Run a script file
  kira -e "print(1+2)"    Evaluate expression
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Script file to run (.kira)'
    )
    
    parser.add_argument(
        '-e', '--eval',
        metavar='CODE',
        help='Evaluate code string'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Kira 1.0.0'
    )
    
    args = parser.parse_args()
    
    if args.eval:
        sys.exit(run_source(args.eval))
    elif args.file:
        sys.exit(run_file(args.file))
    else:
        run_repl()


if __name__ == "__main__":
    main()
