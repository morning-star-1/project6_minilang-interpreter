# MiniLang Interpreter

MiniLang is a small interpreted language for teaching lexing, parsing, ASTs, and evaluation.

## Features
- Variables and assignment
- Arithmetic and comparison expressions
- Block-scoped environments
- Control flow (`if` / `else`, `while`)
- `print` builtin
- REPL and file execution

## Quickstart
### Prerequisites
- Python 3.11+

### REPL
```bash
python main.py
```

### Run a file
```bash
python main.py example.ml
```

## Architecture
- Lexer -> tokens with line/column tracking
- Parser -> recursive descent AST
- Interpreter -> evaluation with nested environments

## Tests
```bash
python -m unittest discover -s tests
```
