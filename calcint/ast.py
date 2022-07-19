#! /usr/bin/env python3

from __future__ import annotations


class Token(object):
    type: TokenType
    value: T.Any

    def __init__(self, type: TokenType, value = None) -> None:
        self.type = type
        if value is None:
            self.value = type.value
        else:
            self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.type}, {self.value!r})"



class AST(object):
    token: Token
    op: Token
    value: T.Any
    children: T.Sequence[AST]

    def __init__(self, token: Token, *nodes: T.Iterable[AST]) -> None:
        self.token = token
        self.op = token
        self.value = token.value
        self.children = list(nodes)


class Compound(AST):
    """Represents a 'BEGIN ... END' block."""


class Assign(AST):
    def __init__(self, token: Token, var: 'Var', value) -> None:
        super().__init__(token, var, value)


class Var(AST):
    def __init__(self, token) -> None:
        super().__init__(token)


class NoOp(AST):
    """Represents an *empty* statement."""
    def __init__(self) -> None:
        ...

class UnaryOp(AST):
    def __init__(self, token, child: AST) -> None:
        super().__init__(token, child)


class BinOp(AST):
    def __init__(self, token: Token, left: Token, right: Token) -> None:
        super().__init__(token, left, right)


class Num(AST):
    def __init__(self, token: Token) -> None:
        super().__init__(token)



class NodeVisitor(object):
    def visit(self, node: AST):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name)
        return visitor(node)
