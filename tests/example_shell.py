from rushell.python_compat import from_python_fn
from rushell.instance import run_instance
from rushell.commands import CommandCtx
import os
import sys

sys.path.append('..')


def lsa(*args, show=False):
    """
    hey?
    """
    return ';'.join(args) + '\n' + '\n'.join(os.listdir('.'))


# noinspection PyTypeChecker
cmd_obj = from_python_fn(lsa)

ctx = CommandCtx()
run_instance(ctx)
