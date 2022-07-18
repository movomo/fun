#! /usr/bin/env python3

import traceback
import typing as T

from enum import Enum, auto

from ast import AST, BinOp, Num, Token, NodeVisitor


class CalcError(Exception):
    ...


class TokenType(Enum):
    EOF = auto()
    LITERAL = auto()
    LPAREN = auto()
    RPAREN = auto()
    MUL = auto()
    DIV = auto()
    ADD = auto()
    SUB = auto()


class Lexer(object):
    text: str
    pos: int
    char: str | None

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.char = self.text[self.pos]

    def error(self):
        raise CalcError(f"invalid character {self.char}")

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
            char = self.char

            if char.isdigit():
                token = Token(TokenType.LITERAL, self.integer())
            elif char == '(':
                token = Token(TokenType.LPAREN, char)
                self.advance()
            elif char == ')':
                token = Token(TokenType.RPAREN, char)
                self.advance()
            elif char == '*':
                token = Token(TokenType.MUL, char)
                self.advance()
            elif char == '/':
                token = Token(TokenType.DIV, char)
                self.advance()
            elif char == '+':
                token = Token(TokenType.ADD, char)
                self.advance()
            elif char == '-':
                token = Token(TokenType.SUB, char)
                self.advance()
            else:
                self.error()

            print('   ', token)
            return token

        return Token(TokenType.EOF, None)


class Parser(object):
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
        """factor: LITERAL | ( LPAREN expr RPAREN)"""
        token = self.token
        if token.type == TokenType.LITERAL:
            self.eat(TokenType.LITERAL)
            return Num(token)
        # elif token.type == TokenType.LPAREN:
        else:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

    def term(self):
        """term: factor ( ( MUL | DIV ) factor )*"""
        node = self.factor()
        while self.token.type in {TokenType.MUL, TokenType.DIV}:
            token = self.token

            match token.type:
                case TokenType.MUL:
                    self.eat(TokenType.MUL)
                case TokenType.DIV:
                    self.eat(TokenType.DIV)

            node = BinOp(token, node, self.factor())

        return node

    def expr(self):
        """expr: term ( ( ADD | SUB ) term )*

        expr: term ( ( ADD | SUB ) term )*
        term: factor ( ( MUL | DIV ) factor )*
        factor: LITERAL | ( LPAREN expr RPAREN)
        """
        node = self.term()
        while self.token.type in {TokenType.ADD, TokenType.SUB}:
            token = self.token

            match token.type:
                case TokenType.ADD:
                    self.eat(TokenType.ADD)
                case TokenType.SUB:
                    self.eat(TokenType.SUB)

            node = BinOp(token, node, self.term())

        return node

    def parse(self):
        return self.expr()


class Interpreter(NodeVisitor):
    parser: Parser

    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def interpret(self):
        return self.visit(self.parser.parse())

    def visit_BinOp(self, node: AST):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])

        match node.op.type:
            case TokenType.ADD:
                return left + right
            case TokenType.SUB:
                return left - right
            case TokenType.MUL:
                return left * right
            case TokenType.DIV:
                return left / right

    def visit_Num(self, node: Num) -> int:
        return node.value


def main():
    while True:
        text = input('calc> ')
        if not text:
            continue
        elif text.casefold() == 'bye':
            print('bye')
            break


        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
        except CalcError as why:
            traceback.print_exception(why)
        else:
            print(result)


if __name__ == '__main__':
    main()
