import sys

sys.path.append('..')

from rushell.python_compat import from_python_fn
from rushell.instance import run_instance
from rushell.commands import CommandCtx
import os


def lsa(*args, show=False):
    """
    hey?
    """
    print(args)
    return ';'.join(args) + '\n' + '\n'.join(os.listdir('.'))


# noinspection PyTypeChecker
cmd_obj = from_python_fn(lsa)

ctx = CommandCtx()
ctx.add(cmd_obj)
run_instance(ctx)
