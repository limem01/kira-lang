"""
Kira Language - REPL (Read-Eval-Print Loop)
============================================
Interactive interpreter for the Kira language.
"""

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .evaluator import Evaluator
from .environment import Environment
from .builtins import KiraRuntimeError, kira_repr

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗  ██╗██╗██████╗  █████╗                              ║
║   ██║ ██╔╝██║██╔══██╗██╔══██╗                             ║
║   █████╔╝ ██║██████╔╝███████║                             ║
║   ██╔═██╗ ██║██╔══██╗██╔══██║                             ║
║   ██║  ██╗██║██║  ██║██║  ██║                             ║
║   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                             ║
║                                                           ║
║   Kira Programming Language v1.0                          ║
║   Type 'help' for commands, 'exit' to quit               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Kira REPL Commands:
  help     - Show this help message
  exit     - Exit the REPL
  clear    - Clear the screen
  env      - Show all variables in current environment
  reset    - Reset environment (clear all variables)

Language Quick Reference:
  let x = 5              - Declare variable
  const PI = 3.14        - Declare constant
  fn add(a, b) { a + b } - Define function
  if x > 0 { ... }       - Conditional
  while x > 0 { ... }    - While loop
  for i in range(10) { } - For loop
  [1, 2, 3]              - Array literal
  {"a": 1, "b": 2}       - Dictionary literal

Built-in Functions:
  print, println, input, len, type, str, int, float,
  range, push, pop, first, last, rest, keys, values,
  abs, min, max, sum, sorted, reversed, join, split,
  upper, lower, strip, replace, contains
"""


def run_repl():
    """Start the interactive REPL."""
    print(BANNER)
    
    env = Environment()
    evaluator = Evaluator()
    
    while True:
        try:
            # Read
            line = input("kira> ")
            
            # Handle commands
            if line.strip() == "":
                continue
            if line.strip() == "exit":
                print("Goodbye!")
                break
            if line.strip() == "help":
                print(HELP_TEXT)
                continue
            if line.strip() == "clear":
                print("\033[2J\033[H", end="")
                continue
            if line.strip() == "env":
                print("Variables:")
                for name, value in env.store.items():
                    const = " (const)" if name in env.constants else ""
                    print(f"  {name}{const} = {kira_repr(value)}")
                continue
            if line.strip() == "reset":
                env = Environment()
                print("Environment reset.")
                continue
            
            # Handle multi-line input (count braces)
            while line.count('{') > line.count('}'):
                line += '\n' + input("...   ")
            
            # Eval
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse_program()
            result = evaluator.eval(program, env)
            
            # Print (only if result is not None)
            if result is not None:
                print(kira_repr(result))
        
        except LexerError as e:
            print(f"Lexer Error: {e.message}")
        except ParserError as e:
            print(f"Parse Error: {e.message}")
        except KiraRuntimeError as e:
            print(f"Runtime Error: {e}")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    run_repl()
