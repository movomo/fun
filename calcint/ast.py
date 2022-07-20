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

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.token!r}, *{self.children!r})'

    def __str__(self) -> str:
        return f'{type(self).__name__}({self.value!r})'


class Program(AST):
    name: str

    def __init__(self, name, node: AST) -> None:
        self.token = self.op = self.value = None
        self.name = name
        self.children = [node]


class Block(AST):
    """Optional declarations followed by mandatory compound block.
    """
    def __init__(self, *nodes: T.Iterable[AST]) -> None:
        """
        :nodes:
            Last node must be the compound statement.
            All preceding it are declarations.
        """
        self.token = self.op = self.value = None
        self.children = list(nodes)


class VarDecl(AST):
    def __init__(self, var_node: 'Var', type_node: 'Type') -> None:
        self.token = self.op = self.value = None
        self.children = [var_node, type_node]


class Type(AST):
    def __init__(self, token) -> None:
        super().__init__(token)


class Compound(AST):
    """Represents a 'BEGIN ... END' block."""
    def __init__(self, *nodes: T.Iterable[AST]) -> None:
        self.token = self.op = self.value = None
        self.children = list(nodes)


class Assign(AST):
    def __init__(self, token: Token, var: 'Var', value) -> None:
        super().__init__(token, var, value)


class Var(AST):
    def __init__(self, token) -> None:
        super().__init__(token)


class NoOp(AST):
    """Represents an *empty* statement."""
    def __init__(self) -> None:
        self.token = self.op = self.value = None
        self.children = list()

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
        print(node)
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name)
        return visitor(node)
