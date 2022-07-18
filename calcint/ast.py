#! /usr/bin/env python3

from __future__ import annotations


class Token(object):
    type: TokenType
    value: T.Any

    def __init__(self, type: TokenType, value) -> None:
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.type}, {self.value!r})"


class AST(object):
    token: Token
    op: Token
    children: T.Sequence[AST]


class BinOp(AST):
    def __init__(self, op: Token, left: Token, right: Token) -> None:
        self.token = op
        self.op = op
        self.children = [left, right];


class Num(AST):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value


class NodeVisitor(object):
    def visit(self, node: AST):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name)
        return visitor(node)
