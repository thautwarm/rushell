from rbnf_rts.rts import AST
from rbnf_rts.token import Token
from dataclasses import dataclass
from typing import List, Union


@dataclass(unsafe_hash=True, order=True, eq=True)
class Cmd:
    # args can be empty
    args: List['Arg']


@dataclass(unsafe_hash=True, order=True, eq=True)
class Quote:
    # args cannot be empty!
    args: List['Arg']


@dataclass(unsafe_hash=True, order=True, eq=True)
class Str:
    args: List['Arg']


@dataclass(unsafe_hash=True, order=True, eq=True)
class Pat:
    value: str


Arg = Union[Cmd, Str, Quote, Pat]


class MK:
    def doubleQuotedStr(self, node: AST) -> Str:
        """doubleQuotedStr : '"' [args] '"';"""
        cs = node.contents
        n = len(cs)
        if n is 2:
            # doubleQuotedStr : '"' '"'
            return Str([])

        else:
            # doubleQuotedStr : '"' args '"';
            return Str(self.args_with_space(cs[1]))

    def quote(self, node: AST) -> Quote:
        """quote : '`' args '`';"""
        return Quote(self.args_without_space(node.contents[1]))

    def pattern(self, node: AST) -> Pat:
        """pattern : [pattern] ch;"""
        cs = node.contents
        xs = []
        append = xs.append
        _len = len
        ch = self.ch
        while _len(cs) is 2:
            append(ch(cs[1]))
            cs = cs[0].contents
        append(ch(cs[0]))
        xs.reverse()
        return Pat(''.join(xs))

    @staticmethod
    def ch(node: AST) -> str:
        """
        ch : '\\' '"';
        ch : '\\' '\\';
        ch :  <any>;
        """
        cs = node.contents
        if len(cs) is 1:
            # ch: <any>;
            return cs[0].value
        # ch : '\\' '"';
        # ch : '\\' '\\';
        return cs[1].value

    def args_with_space(self, node: AST) -> List[Arg]:
        """
        arg : doubleQuotedStr;
        arg : pattern;
        arg : quote;
        strPattern : arg;
        strPattern : <space>;
        args : [args] strPattern;
        """
        cs = node.contents
        xs = []
        append = xs.append
        _len = len
        _type = type
        _token = Token
        _pat = Pat
        while _len(cs) is 2:
            c = cs[1].contents[0]
            if _type(c) is _token:
                # noinspection PyArgumentList
                append(_pat(c.value))
            else:
                append(getattr(self, c.tag)(c))
            cs = cs[0].contents
        c = cs[0].contents[0]
        if _type(c) is _token:
            # noinspection PyArgumentList
            append(_pat(c.value))
        else:
            append(getattr(self, c.tag)(c))

        xs.reverse()
        return xs

    def args_without_space(self, node: AST) -> List[Arg]:
        """
        arg : doubleQuotedStr;
        arg : pattern;
        arg : quote;
        strPattern : arg;
        strPattern : <space>;
        args : [args] strPattern;
        """
        cs = node.contents
        xs = []
        append = xs.append
        _len = len
        _type = type
        _token = Token
        while _len(cs) is 2:
            c = cs[1].contents[0]
            if _type(c) is not _token:
                append(getattr(self, c.tag)(c))
            cs = cs[0].contents
        c = cs[0].contents[0]
        if _type(c) is not _token:
            append(getattr(self, c.tag)(c))

        xs.reverse()
        return xs


def structure_top(ast: AST):
    if len(ast.contents) is 2:
        return []
    return MK().args_without_space(ast.contents[1])
