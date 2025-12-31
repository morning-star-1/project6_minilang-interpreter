from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional, List

class MiniLangError(Exception): pass
class LexError(MiniLangError): pass
class ParseError(MiniLangError): pass
class RuntimeErrorML(MiniLangError): pass

class TokenType(Enum):
    LEFT_PAREN = auto(); RIGHT_PAREN = auto()
    LEFT_BRACE = auto(); RIGHT_BRACE = auto()
    SEMICOLON = auto()
    PLUS = auto(); MINUS = auto(); STAR = auto(); SLASH = auto()
    BANG = auto(); EQUAL = auto(); LESS = auto(); GREATER = auto()
    BANG_EQUAL = auto(); EQUAL_EQUAL = auto()
    LESS_EQUAL = auto(); GREATER_EQUAL = auto()
    IDENT = auto(); NUMBER = auto(); STRING = auto()
    LET = auto(); IF = auto(); ELSE = auto()
    WHILE = auto(); PRINT = auto()
    TRUE = auto(); FALSE = auto(); NULL = auto()
    EOF = auto()

KEYWORDS = {
    "let": TokenType.LET, "if": TokenType.IF, "else": TokenType.ELSE,
    "while": TokenType.WHILE, "print": TokenType.PRINT,
    "true": TokenType.TRUE, "false": TokenType.FALSE, "null": TokenType.NULL,
}

@dataclass(frozen=True)
class Token:
    typ: TokenType
    lexeme: str
    literal: Any
    line: int
    col: int

# ===== AST =====
class Expr: ...
class Stmt: ...

@dataclass
class Literal(Expr):
    value: Any

@dataclass
class Variable(Expr):
    name: Token

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

@dataclass
class Grouping(Expr):
    expr: Expr

@dataclass
class Unary(Expr):
    op: Token
    right: Expr

@dataclass
class Binary(Expr):
    left: Expr
    op: Token
    right: Expr

@dataclass
class ExprStmt(Stmt):
    expr: Expr

@dataclass
class PrintStmt(Stmt):
    expr: Expr

@dataclass
class LetStmt(Stmt):
    name: Token
    initializer: Expr

@dataclass
class Block(Stmt):
    statements: List[Stmt]

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt
