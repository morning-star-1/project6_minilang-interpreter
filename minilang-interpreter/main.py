import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from ml_ast import MiniLangError

def run(source: str, interp: Interpreter):
    tokens = Lexer(source).lex()
    program = Parser(tokens).parse()
    interp.interpret(program)

def repl():
    interp = Interpreter()
    print("MiniLang REPL. Type 'exit' to quit.")

    buffer = ""
    depth = 0

    while True:
        try:
            prompt = "ml> " if depth == 0 else "... "
            line = input(prompt)

            if depth == 0 and line.strip() in ("exit", "quit"):
                break

            buffer += line + "\n"
            depth += line.count("{") - line.count("}")

            # keep reading until all blocks are closed
            if depth > 0:
                continue

            if buffer.strip():
                run(buffer, interp)

            buffer = ""

        except MiniLangError as e:
            print(e)
            buffer = ""
            depth = 0
        except KeyboardInterrupt:
            print("\n(use 'exit' to quit)")
            buffer = ""
            depth = 0
        except EOFError:
            break

def run_file(path: str):
    interp = Interpreter()
    with open(path, "r", encoding="utf-8") as f:
        run(f.read(), interp)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        repl()
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        print("Usage: python main.py [file.ml]")
        sys.exit(2)
