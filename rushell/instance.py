from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rushell.auto_completion import RushFastCompleter, RushAdaptorForPromptToolkit
from rushell.commands import CommandCtx
from rushell.exceptions import RushException, ParseError
from rushell.parser_wrap import parse
from rushell.structured import structure_top, Cmd
import os.path as path
import sys


def run_instance(cmd_world: CommandCtx, completer=None):
    completer = completer or RushFastCompleter()
    p = path.expanduser('~/.rushrc.py')
    with open(p) as f:
        rc_code = f.read()

    sys.path.append(path.dirname(p))
    glob = {
        '__file__': p, 'COMPLETER': completer, 'PROMPT_PREFIX': 'rush> ', "HISTORY_FILE": '~/.rush_history'
    }
    cmd_world.scope = glob
    exec(rc_code, glob)

    history = glob['HISTORY_FILE']
    session = PromptSession(history=FileHistory(history))

    autocomp_adaptor = RushAdaptorForPromptToolkit(glob['COMPLETER'])
    while True:
        text = session.prompt(glob['PROMPT_PREFIX'], completer=autocomp_adaptor)
        try:
            structure_top(parse(text))
        except RushException as e:
            e.print()
        except ParseError as e:
            e.print()
