import sys

sys.path.append('..')

from rushell import __version__
from rushell.parser_wrap import parse, ParseError
from rushell.structured import structure_top, get_current, Cmd
from rbnf_rts.pprinter import pprint


def test_version():
    assert __version__ == '0.1.0'


if __name__ == "__main__":
    while True:
        # pprint((parse(input())))
        args = structure_top(parse(input()))
        print(args)
        print(get_current(Cmd(args)))
