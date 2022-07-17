#! /usr/bin/env python3

import typing as T

from enum import Enum, auto


class CalcError(Exception):
    ...


class TokenType(Enum):
    EOF = auto()
    LITERAL = auto()
    MUL = auto()
    DIV = auto()
    ADD = auto()
    SUB = auto()


class Token(object):
    type: TokenType
    value: T.Any

    def __init__(self, type: TokenType, value) -> None:
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.type}, {self.value!r})"


class Lexer(object):
    text: str
    pos: int
    char: str | None

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.char = self.text[self.pos]

    def error(self):
        raise CalcError("invalid character")

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.char = None
        else:
            self.char = self.text[self.pos]

    def skip_whitespace(self):
        while self.char is not None and self.char.isspace():
            self.advance()

    def integer(self):
        result = []
        while self.char is not None and self.char.isdigit():
            result.append(self.char)
            self.advance()
        return int(''.join(result))

    def next(self) -> Token:
        while self.char is not None:
            if self.char.isspace():
                self.skip_whitespace()
                continue

            token = None
            if self.char.isdigit():
                token = Token(TokenType.LITERAL, self.integer())
            elif self.char == '*':
                token = Token(TokenType.MUL, self.char)
                self.advance()
            elif self.char == '/':
                token = Token(TokenType.DIV, self.char)
                self.advance()
            elif self.char == '+':
                token = Token(TokenType.ADD, self.char)
                self.advance()
            elif self.char == '-':
                token = Token(TokenType.SUB, self.char)
                self.advance()
            else:
                self.error()

            print('   ', token)
            return token

        return Token(TokenType.EOF, None)


class Interpreter(object):
    lexer: Lexer
    token: Token | None

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.token = self.lexer.next()

    def error(self):
        raise CalcError("invalid syntax")

    def eat(self, expected: TokenType):
        if self.token.type == expected:
            self.token = self.lexer.next()
        else:
            self.error()

    def factor(self) -> int:
        """factor: LITERAL"""
        token = self.token
        self.eat(TokenType.LITERAL)
        return token.value

    def term(self):
        """term: factor ( ( MUL | DIV ) factor )*"""
        result = self.factor()
        while self.token.type in {TokenType.MUL, TokenType.DIV}:
            token = self.token

            match token.type:
                case TokenType.MUL:
                    self.eat(TokenType.MUL)
                    result *= self.factor()
                case TokenType.DIV:
                    self.eat(TokenType.DIV)
                    result /= self.factor()

        return result

    def expr(self):
        """expr: term ( ( ADD | SUB ) term )*

        expr: term ( ( ADD | SUB ) term )*
        term: factor ( ( MUL | DIV ) factor )*
        factor: LITERAL
        """

        result = self.term()
        while self.token.type in {TokenType.ADD, TokenType.SUB}:
            token = self.token

            match token.type:
                case TokenType.ADD:
                    self.eat(TokenType.ADD)
                    result += self.term()
                case TokenType.SUB:
                    self.eat(TokenType.SUB)
                    result -= self.term()

        return result


def main():
    while True:
        text = input('calc> ')
        if not text:
            continue
        elif text.casefold() == 'quit':
            print('bye')
            break

        lexer = Lexer(text)
        interpreter = Interpreter(lexer)

        try:
            result = interpreter.expr()
        except CalcError as why:
            print(why)
        else:
            print(result)


if __name__ == '__main__':
    main()
