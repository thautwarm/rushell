from typing import List, Callable, Dict
from rushell.structured import Concat, Cmd, Str, Arg
from rushell.exceptions import CommandArgumentError, CommandNotFound

AllCmdsInWorld = Dict[str, Callable[[List[Arg]], str]]


def eval_str_sections_with_world_(xs: List[str], world: AllCmdsInWorld, s: Concat):
    """Deciding the command name from a `Str`"""
    _pat = Str
    _str = Concat
    _cmd = Cmd
    _type = type
    for each in s.args:
        if _type(each) is _pat:
            xs.append(each.value)
        elif _type(each) is _cmd:
            cmd_name, args = split_cmd_with_world(world, each)
            xs.append(eval_cmd_with_world(world, cmd_name, args))
        else:
            eval_str_sections_with_world_(xs, world, each)


def eval_concat_with_world(world: AllCmdsInWorld, s: Concat):
    xs = []
    eval_str_sections_with_world_(xs, world, s)
    return ''.join(xs)


def split_cmd_with_world(world: AllCmdsInWorld, cmd: Cmd):
    """split `Cmd` into (command_name: str, args: List[Arg])"""
    args = cmd.args
    if not args:
        raise CommandArgumentError("command pattern list empty")
    cmd_name_arg, *args = args

    if isinstance(cmd_name_arg, Str):
        return cmd_name_arg.value, args

    if isinstance(cmd_name_arg, Cmd):
        # the command name is quoted like: "`cat cmd.txt`" -a
        fname, fargs = split_cmd_with_world(world, cmd_name_arg)
        return eval_cmd_with_world(world, fname, fargs), args

    return eval_concat_with_world(world, cmd_name_arg), args


def eval_arg_with_world(world: AllCmdsInWorld, arg: Arg):
    if isinstance(arg, Concat):
        return eval_concat_with_world(world, arg)
    if isinstance(arg, Cmd):
        cmd_name, args = split_cmd_with_world(world, arg)
        return eval_cmd_with_world(world, cmd_name, args)
    return arg


def eval_cmd_with_world(world: AllCmdsInWorld, command_name: str, args: List[Arg]) -> str:
    cmd_obj = world.get(command_name, None)
    if cmd_obj is None:
        raise CommandNotFound(command_name)
    return cmd_obj(args)
