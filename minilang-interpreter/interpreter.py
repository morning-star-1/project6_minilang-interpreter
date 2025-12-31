# interpreter.py
from __future__ import annotations
from typing import Any, Dict, Optional
from ml_ast import (
    RuntimeErrorML, Token,
    Expr, Stmt,
    Literal, Variable, Assign, Grouping, Unary, Binary,
    ExprStmt, PrintStmt, LetStmt, Block, IfStmt, WhileStmt,
    TokenType
)

class Environment:
    def __init__(self, parent: Optional[Environment] = None):
        self.values: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeErrorML(f"[line {name.line}:{name.col}] Undefined variable '{name.lexeme}'.")

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeErrorML(f"[line {name.line}:{name.col}] Undefined variable '{name.lexeme}'.")

class Interpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, statements):
        for stmt in statements:
            self._execute(stmt)

    # ---------- Statements ----------
    def _execute(self, stmt: Stmt):
        if isinstance(stmt, ExprStmt):
            self._eval(stmt.expr)
        elif isinstance(stmt, PrintStmt):
            value = self._eval(stmt.expr)
            print(value)
        elif isinstance(stmt, LetStmt):
            value = self._eval(stmt.initializer)
            self.env.define(stmt.name.lexeme, value)
        elif isinstance(stmt, Block):
            self._execute_block(stmt.statements, Environment(self.env))
        elif isinstance(stmt, IfStmt):
            if self._is_truthy(self._eval(stmt.condition)):
                self._execute(stmt.then_branch)
            elif stmt.else_branch:
                self._execute(stmt.else_branch)
        elif isinstance(stmt, WhileStmt):
            while self._is_truthy(self._eval(stmt.condition)):
                self._execute(stmt.body)
        else:
            raise RuntimeErrorML(f"Unknown statement type: {type(stmt)}")

    def _execute_block(self, statements, env: Environment):
        previous = self.env
        try:
            self.env = env
            for stmt in statements:
                self._execute(stmt)
        finally:
            self.env = previous

    # ---------- Expressions ----------
    def _eval(self, expr: Expr) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Variable):
            return self.env.get(expr.name)
        if isinstance(expr, Assign):
            value = self._eval(expr.value)
            self.env.assign(expr.name, value)
            return value
        if isinstance(expr, Grouping):
            return self._eval(expr.expr)
        if isinstance(expr, Unary):
            right = self._eval(expr.right)
            if expr.op.typ == TokenType.MINUS:
                self._check_number(expr.op, right)
                return -right
            if expr.op.typ == TokenType.BANG:
                return not self._is_truthy(right)
        if isinstance(expr, Binary):
            left = self._eval(expr.left)
            right = self._eval(expr.right)
            return self._apply_binary(expr.op, left, right)
        raise RuntimeErrorML(f"Unknown expression type: {type(expr)}")

    def _apply_binary(self, op: Token, left: Any, right: Any):
        t = op.typ
        if t == TokenType.PLUS:
            return left + right
        if t == TokenType.MINUS:
            self._check_numbers(op, left, right)
            return left - right
        if t == TokenType.STAR:
            self._check_numbers(op, left, right)
            return left * right
        if t == TokenType.SLASH:
            self._check_numbers(op, left, right)
            return left / right
        if t == TokenType.EQUAL_EQUAL:
            return left == right
        if t == TokenType.BANG_EQUAL:
            return left != right
        if t == TokenType.LESS:
            self._check_numbers(op, left, right)
            return left < right
        if t == TokenType.LESS_EQUAL:
            self._check_numbers(op, left, right)
            return left <= right
        if t == TokenType.GREATER:
            self._check_numbers(op, left, right)
            return left > right
        if t == TokenType.GREATER_EQUAL:
            self._check_numbers(op, left, right)
            return left >= right
        raise RuntimeErrorML(f"Invalid operator {op.lexeme}")

    # ---------- Helpers ----------
    def _is_truthy(self, value: Any) -> bool:
        return bool(value)

    def _check_number(self, op: Token, value: Any):
        if not isinstance(value, (int, float)):
            raise RuntimeErrorML(f"[line {op.line}:{op.col}] Operand must be a number.")

    def _check_numbers(self, op: Token, left: Any, right: Any):
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise RuntimeErrorML(f"[line {op.line}:{op.col}] Operands must be numbers.")
