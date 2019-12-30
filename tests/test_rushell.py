from rushell import __version__
from rushell.parser_wrap import parse
from rushell.structured import structure_top
from rbnf_rts.pprinter import pprint
def test_version():
    assert __version__ == '0.1.0'


if __name__ == "__main__":
    while True:
        # pprint((parse(input())))
        pprint(structure_top(parse(input())))
