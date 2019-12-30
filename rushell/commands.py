from rushell.exceptions import CommandContextUnset
from rushell.structured import Arg, Str, Cmd, Concat
from rushell import toolz
from typing import List, Dict, Iterable, Callable, Union, Optional
import abc


class CommandCtx:
    cmds: Dict[str, 'CommandObject']
    scope: dict

    def __init__(self):
        self.cmds = {}

    def add(self, cmd_obj: 'CommandObject'):
        cmd_obj._cmd_ctx = self
        self.cmds[cmd_obj.name] = cmd_obj


class CommandObject:
    doc: str
    name: str

    _cmd_ctx: Optional[CommandCtx]

    @property
    def cmd_ctx(self):
        c = self._cmd_ctx
        if c:
            return c
        raise CommandContextUnset

    @abc.abstractmethod
    def __call__(self, args: List[Arg]) -> str:
        raise NotImplementedError


class ClassicCommandObject(CommandObject):
    vararg_names: Iterable[str]
    logic: Callable[[List[str], Dict[str, Union[str, List[str]]]], str]

    def __call__(self, args: List[Arg]) -> str:
        _world = self.cmd_ctx.cmds
        _str = Str
        _cmd = Cmd
        _concat = Concat
        positional = []
        keywords = {}

        keyword_cur = None
        for each in args:
            if isinstance(each, _str):
                arg_str = each.value
                if arg_str.startswith('-'):
                    if arg_str.startswith('--'):
                        keywords[arg_str[2:]] = True
                    else:
                        keyword_cur = arg_str[1:]
                    continue

            elif isinstance(each, _concat):
                arg_str = toolz.eval_concat_with_world(_world, each)
            else:
                cmd_name, cmd_args = toolz.split_cmd_with_world(_world, each)
                arg_str = toolz.eval_cmd_with_world(_world, cmd_name, cmd_args)

            if keyword_cur is not None:
                if keyword_cur in self.vararg_names:
                    try:
                        keywords[keyword_cur].append(arg_str)
                    except KeyError:
                        keywords[keyword_cur] = [arg_str]
                else:
                    keywords[keyword_cur] = arg_str
                keyword_cur = None
            else:
                positional.append(arg_str)

        return self.logic(positional, keywords)
