# lexer.py
from __future__ import annotations
from typing import List, Any
from ml_ast import Token, TokenType, KEYWORDS, LexError

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1
        self.start_col = 1

    def lex(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self.start_col = self.col
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.col))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _peek(self) -> str:
        return "\0" if self._is_at_end() else self.source[self.current]

    def _peek_next(self) -> str:
        return "\0" if self.current + 1 >= len(self.source) else self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.col += 1
        return True

    def _add(self, typ: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(typ, text, literal, self.line, self.start_col))

    def _scan_token(self):
        ch = self._advance()

        # whitespace
        if ch in (" ", "\r", "\t", "\n"):
            return

        # comment //
        if ch == "/" and self._peek() == "/":
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return

        # single-char
        if ch == "(": return self._add(TokenType.LEFT_PAREN)
        if ch == ")": return self._add(TokenType.RIGHT_PAREN)
        if ch == "{": return self._add(TokenType.LEFT_BRACE)
        if ch == "}": return self._add(TokenType.RIGHT_BRACE)
        if ch == ";": return self._add(TokenType.SEMICOLON)
        if ch == "+": return self._add(TokenType.PLUS)
        if ch == "-": return self._add(TokenType.MINUS)
        if ch == "*": return self._add(TokenType.STAR)
        if ch == "/": return self._add(TokenType.SLASH)

        # one/two-char ops
        if ch == "!": return self._add(TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG)
        if ch == "=": return self._add(TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL)
        if ch == "<": return self._add(TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS)
        if ch == ">": return self._add(TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER)

        # string
        if ch == '"':
            return self._string()

        # number
        if ch.isdigit():
            return self._number()

        # ident/keyword
        if ch.isalpha() or ch == "_":
            return self._ident()

        raise LexError(f"[line {self.line}:{self.start_col}] Unexpected character {ch!r}")

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            self._advance()
        if self._is_at_end():
            raise LexError(f"[line {self.line}:{self.start_col}] Unterminated string")
        self._advance()  # closing quote
        value = self.source[self.start + 1 : self.current - 1]
        self._add(TokenType.STRING, value)

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self.source[self.start:self.current]
        self._add(TokenType.NUMBER, float(text) if "." in text else int(text))

    def _ident(self):
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[self.start:self.current]
        typ = KEYWORDS.get(text, TokenType.IDENT)
        lit = None
        if typ == TokenType.TRUE: lit = True
        elif typ == TokenType.FALSE: lit = False
        elif typ == TokenType.NULL: lit = None
        self._add(typ, lit)
