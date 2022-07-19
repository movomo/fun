#! /usr/bin/env python3

"""
program : compound_statement DOT
compound_statement : BEGIN statement_list END
statement_list : statement
               | statement SEMI statement_list
statement : compound_statement
          | assignment_statement
          | empty
assignment_statement : variable ASSIGN expr
empty :
expr: term ((PLUS | MINUS) term)*
term: factor ((MUL | DIV) factor)*
factor : PLUS factor
       | MINUS factor
       | INTEGER
       | LPAREN expr RPAREN
       | variable
variable: ID
"""

import traceback
import typing as T

from enum import Enum, auto

from ast import (
    AST,
    Compound, Assign, Var,
    NoOp, BinOp, UnaryOp, Num,
    Token, NodeVisitor,
)


class CalcError(Exception):
    ...


class TOKEN(Enum):
    EOF = auto()
    BEGIN = 'BEGIN'
    END = 'END'
    DOT = '.'
    SEMI = ';'
    EMPTY = auto()
    ASSIGN = ':='
    INTEGER = auto()
    LPAREN = '('
    RPAREN = ')'
    MUL = '*'
    DIV = '/'
    PLUS = '+'
    MINUS = '-'
    ID = auto()


RESERVED_KEYWORDS = {
    'BEGIN': Token(TOKEN.BEGIN),
    'END': Token(TOKEN.END),
}


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

            if char.isalpha():
                token = self._id()
                
            elif char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                token = Token(TOKEN.ASSIGN)
            elif char == ';':
                token = Token(TOKEN.SEMI)
            elif char == '.':
                token = Token(TOKEN.DOT)
                
            elif char.isdigit():
                token = Token(TOKEN.INTEGER, self.integer())
            elif char == '(':
                token = Token(TOKEN.LPAREN, char)
                self.advance()
            elif char == ')':
                token = Token(TOKEN.RPAREN, char)
                self.advance()
            elif char == '*':
                token = Token(TOKEN.MUL, char)
                self.advance()
            elif char == '/':
                token = Token(TOKEN.DIV, char)
                self.advance()
            elif char == '+':
                token = Token(TOKEN.PLUS, char)
                self.advance()
            elif char == '-':
                token = Token(TOKEN.MINUS, char)
                self.advance()
            else:
                self.error()

            print('   ', token)
            return token

        return Token(TOKEN.EOF, None)

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos <= len(self.text) - 1:
            return self.text[peek_pos]

    def _id(self):
        chars = []
        while self.char is not None and self.char.isalnum():
            chars.append(self.char)
            self.advance()
            
        identifier = ''.join(chars)
        token = RESERVED_KEYWORDS.get(identifier, Token(TOKEN.ID, identifier))
        return token


class Parser(object):
    lexer: Lexer
    token: Token | None

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.token = self.lexer.next()

    def error(self):
        raise CalcError("invalid syntax")

    def eat(self, expected: TOKEN):
        if self.token.type == expected:
            self.token = self.lexer.next()
        else:
            self.error()

    def program(self):
        """program : compound_statement DOT"""
        node = self.compound_statement()
        self.eat(DOT)
        return node
        
    def compound_statement(self):
        """compound_statement : BEGIN statement_list END"""
        self.eat(TOKEN.BEGIN)
        nodes = self.statement_list()
        self.eat(TOKEN.END)
        
        root = Compound(None, *nodes)
        
        return root

    def factor(self):
        """factor: ( PLUS | MINUS ) factor | INTEGER | ( LPAREN expr RPAREN)"""
        token = self.token
        if token.type == TOKEN.PLUS:
            self.eat(TOKEN.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == TOKEN.MINUS:
            self.eat(TOKEN.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == TOKEN.INTEGER:
            self.eat(TOKEN.INTEGER)
            return Num(token)
        # elif token.type == TOKEN.LPAREN:
        else:
            self.eat(TOKEN.LPAREN)
            node = self.expr()
            self.eat(TOKEN.RPAREN)
            return node

    def term(self):
        """term: factor ( ( MUL | DIV ) factor )*"""
        node = self.factor()
        while self.token.type in {TOKEN.MUL, TOKEN.DIV}:
            token = self.token

            match token.type:
                case TOKEN.MUL:
                    self.eat(TOKEN.MUL)
                case TOKEN.DIV:
                    self.eat(TOKEN.DIV)

            node = BinOp(token, node, self.factor())

        return node

    def expr(self):
        """expr: term ( ( PLUS | MINUS ) term )*

        expr: term ( ( PLUS | MINUS ) term )*
        term: factor ( ( MUL | DIV ) factor )*
        factor: ( PLUS | MINUS ) factor | INTEGER | ( LPAREN expr RPAREN)
        """
        node = self.term()
        while self.token.type in {TOKEN.PLUS, TOKEN.MINUS}:
            token = self.token

            match token.type:
                case TOKEN.PLUS:
                    self.eat(TOKEN.PLUS)
                case TOKEN.MINUS:
                    self.eat(TOKEN.MINUS)

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

    def visit_UnaryOp(self, node: AST):
        value = self.visit(node.children[0])
        match node.op.type:
            case TOKEN.PLUS:
                return value
            case TOKEN.MINUS:
                return -value

    def visit_BinOp(self, node: AST):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])

        match node.op.type:
            case TOKEN.PLUS:
                return left + right
            case TOKEN.MINUS:
                return left - right
            case TOKEN.MUL:
                return left * right
            case TOKEN.DIV:
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
