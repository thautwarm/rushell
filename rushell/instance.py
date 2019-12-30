from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rushell.auto_completion import RushFastCompleter, RushAdaptorForPromptToolkit
from rushell.commands import CommandCtx
from rushell.exceptions import RushException, ParseError
from rushell.parser_wrap import parse
from rushell.structured import structure_top, Cmd
from rushell.toolz import eval_cmd_with_world, split_cmd_with_world
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

    history = path.expanduser(glob['HISTORY_FILE'])
    session = PromptSession(history=FileHistory(history))

    autocomp_adaptor = RushAdaptorForPromptToolkit(glob['COMPLETER'])
    while True:
        text = session.prompt(glob['PROMPT_PREFIX'], completer=autocomp_adaptor)
        try:
            cmd_name, args = split_cmd_with_world(cmd_world.cmds, Cmd(structure_top(parse(text))))
            print(eval_cmd_with_world(cmd_world.cmds, cmd_name, args))
        except RushException as e:
            print(e.show())
        except ParseError as e:
            print(e.show())
