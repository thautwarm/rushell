from rushell.parser_generated import *
from rbnf_rts.rts import Tokens, State, AST
from rushell.exceptions import ParseError

__all__ = ['parse']
_parse = mk_parser()


def parse(text: str, filename: str = "unknown") -> AST:
    tokens = list(run_lexer(filename, text))
    res = _parse(State(), Tokens(tokens))
    if res[0]:
        return res[1]

    msgs = []
    token = None
    for each in res[1]:
        i, msg = each
        token = tokens[i]
        lineno = token.lineno
        colno = token.colno
        msgs.append(f"Line {lineno}, column {colno}, {msg}")
    err = ParseError()
    err.msg = f"Filename {filename}:\n" + "\n".join(msgs)
    err.offset = 0 if token is None else token.offset
    raise err
