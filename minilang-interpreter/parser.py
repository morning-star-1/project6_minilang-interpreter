# parser.py
from __future__ import annotations
from typing import List, Optional
from ml_ast import (
    Token, TokenType, ParseError,
    Expr, Stmt,
    Literal, Variable, Assign, Grouping, Unary, Binary,
    ExprStmt, PrintStmt, LetStmt, Block, IfStmt, WhileStmt
)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._is_at_end():
            statements.append(self._statement())
        return statements

    # ---------- Statements ----------
    def _statement(self) -> Stmt:
        if self._match(TokenType.LET):
            return self._let_stmt()
        if self._match(TokenType.PRINT):
            expr = self._expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after value.")
            return PrintStmt(expr)
        if self._match(TokenType.IF):
            return self._if_stmt()
        if self._match(TokenType.WHILE):
            return self._while_stmt()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return ExprStmt(expr)

    def _let_stmt(self) -> Stmt:
        name = self._consume(TokenType.IDENT, "Expected variable name.")
        self._consume(TokenType.EQUAL, "Expected '=' after name.")
        init = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';'.")
        return LetStmt(name, init)

    def _if_stmt(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after if.")
        cond = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')'.")
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return IfStmt(cond, then_branch, else_branch)

    def _while_stmt(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after while.")
        cond = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')'.")
        body = self._statement()
        return WhileStmt(cond, body)

    def _block(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._statement())
        self._consume(TokenType.RIGHT_BRACE, "Expected '}'.")
        return statements

    # ---------- Expressions ----------
    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._equality()
        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            raise ParseError(f"[line {equals.line}:{equals.col}] Invalid assignment target.")
        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self._previous()
            right = self._comparison()
            expr = Binary(expr, op, right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op = self._previous()
            right = self._term()
            expr = Binary(expr, op, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._factor()
            expr = Binary(expr, op, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous()
            right = self._unary()
            expr = Binary(expr, op, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            op = self._previous()
            right = self._unary()
            return Unary(op, right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.NULL):
            return Literal(None)
        if self._match(TokenType.IDENT):
            return Variable(self._previous())
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')'.")
            return Grouping(expr)
        t = self._peek()
        raise ParseError(f"[line {t.line}:{t.col}] Expected expression.")

    # ---------- Helpers ----------
    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, typ: TokenType, msg: str) -> Token:
        if self._check(typ):
            return self._advance()
        t = self._peek()
        raise ParseError(f"[line {t.line}:{t.col}] {msg}")

    def _check(self, typ: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().typ == typ

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().typ == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
