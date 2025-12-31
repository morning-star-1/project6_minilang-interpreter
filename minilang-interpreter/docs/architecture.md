# Architecture

## Overview
- Lexer tokenizes source
- Parser builds an AST via recursive descent
- Interpreter evaluates the AST

## Data flow
Source code -> tokens -> AST -> evaluation

## Key decisions
- Keep the grammar small and readable
- Prioritize clarity over performance
