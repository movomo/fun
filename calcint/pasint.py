#! /usr/bin/env python3

"""
program : PROGRAM variable SEMI block DOT

block : declarations compound_statement

declarations : VAR (variable_declaration SEMI)+
             | empty

variable_declaration : ID (COMMA ID)* COLON type_spec

type_spec : INTEGER | REAL

compound_statement : BEGIN statement_list END

statement_list : statement
               | statement SEMI statement_list

statement : compound_statement
          | assignment_statement
          | empty

assignment_statement : variable ASSIGN expr

empty :

expr : term ((PLUS | MINUS) term)*

term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*

factor : PLUS factor
       | MINUS factor
       | INTEGER_CONST
       | REAL_CONST
       | LPAREN expr RPAREN
       | variable

variable: ID
"""

import traceback
import typing as T

from enum import Enum, auto

from ast import (
    AST,
    Program, Block, VarDecl, Type, Compound, Assign, Var,
    NoOp, BinOp, UnaryOp, Num,
    Token, NodeVisitor,
)


class CalcError(Exception):
    ...


class TOKEN(Enum):
    EOF = auto()
    PROGRAM = 'PROGRAM'
    VAR = 'VAR'
    BEGIN = 'BEGIN'
    END = 'END'
    DOT = '.'
    SEMI = ';'
    EMPTY = auto()
    ASSIGN = ':='
    INTEGER = 'INTEGER'
    REAL = 'REAL'
    INTEGER_CONST = auto()
    REAL_CONST = auto()
    ID = auto()
    LPAREN = '('
    RPAREN = ')'
    MUL = '*'
    DIV = '/'
    INTEGER_DIV = 'DIV'
    PLUS = '+'
    MINUS = '-'


RESERVED_KEYWORDS = {
    'PROGRAM': Token(TOKEN.PROGRAM),
    'VAR': Token(TOKEN.VAR),
    'BEGIN': Token(TOKEN.BEGIN),
    'END': Token(TOKEN.END),
    'INTEGER': Token(TOKEN.INTEGER),
    'REAL': Token(TOKEN.REAL),
    'DIV': Token(TOKEN.INTEGER_DIV),
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

    def skip_comment(self):
        while self.char != '}':
            self.advance()
        self.advance()

    def number(self):
        result = []
        while self.char is not None and self.char.isdigit():
            result.append(self.char)
            self.advance()

        if self.char == '.':
            result.append(self.char)
            self.advance()
            while self.char is not None and self.char.isdigit():
                result.append(self.char)
                self.advance()
            token = Token(TOKEN.REAL_CONST, float(''.join(result))
        else:
            token = Token(TOKEN.INTEGER_CONST, int(''.join(result))

        return token

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
                self.advance()
            elif char == '.':
                token = Token(TOKEN.DOT)
                self.advance()

            elif char.isdigit():
                token = self.number()
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
        self.eat(TOKEN.PROGRAM)

        var_node = self.variable()
        name = var_node.value
        self.eat(TOKEN.SEMI)

        block_node = self.block()

        program_node = Program(name, block_node)
        self.eat(TOKEN.DOT)

        return node

    def compound_statement(self):
        """compound_statement : BEGIN statement_list END"""
        self.eat(TOKEN.BEGIN)
        nodes = self.statement_list()
        self.eat(TOKEN.END)

        root = Compound(*nodes)

        return root

    def statement_list(self):
        """statement_list : statement | statement SEMI statement_list"""
        nodes = [self.statement()]
        while self.token.type == TOKEN.SEMI:
            self.eat(TOKEN.SEMI)
            nodes.append(self.statement())

        if self.token.type == TOKEN.ID:
            self.error()

        return nodes

    def statement(self):
        """statement : compound_statement
                     | assignment_statement
                     | empty
        """
        if self.token.type == TOKEN.BEGIN:
            node = self.compound_statement()
        elif self.token.type == TOKEN.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()

        return node

    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        self.eat(TOKEN.ASSIGN)
        right = self.expr()
        node = Assign(self.token, left, right)
        return node

    def variable(self):
        """variable: ID"""
        node = Var(self.token)
        self.eat(TOKEN.ID)
        return node

    def empty(self):
        """"""
        return NoOp()

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.token
        if token.type == TOKEN.PLUS:
            self.eat(TOKEN.PLUS)
            node = UnaryOp(token, self.factor())
        elif token.type == TOKEN.MINUS:
            self.eat(TOKEN.MINUS)
            node = UnaryOp(token, self.factor())
        elif token.type == TOKEN.INTEGER:
            self.eat(TOKEN.INTEGER)
            node = Num(token)
        elif token.type == TOKEN.LPAREN:
            self.eat(TOKEN.LPAREN)
            node = self.expr()
            self.eat(TOKEN.RPAREN)
        else:
            node = self.variable()

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
        node = self.program()
        if self.token.type != TOKEN.EOF:
            self.error()
        return node


class Interpreter(NodeVisitor):
    parser: Parser
    GLOBAL_SCOPE: dict[str, T.Any]

    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def interpret(self):
        return self.visit(self.parser.parse())

    def visit_Compound(self, node: AST):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node: AST):
        name = node.children[0].value
        self.GLOBAL_SCOPE[name] = self.visit(node.children[1])

    def visit_Var(self, node: AST):
        name = node.value
        if name in self.GLOBAL_SCOPE:
            return self.GLOBAL_SCOPE[name]
        else:
            raise NameError(name)

    def visit_NoOp(self, node: AST):
        return

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
