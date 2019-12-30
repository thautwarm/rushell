from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from rushell.parser_wrap import parse, ParseError
from rushell.structured import get_current, structure_top, Cmd, Pat, Str
from abc import ABC
from typing import List, Callable, Dict


class CommandNameCannotDecide(Exception):
    pass


def collect_raw(xs: List[str], s: Str):
    """Deciding the command name from a `Str`"""
    _pat = Pat
    _str = Str
    _cmd = Cmd
    _type = type
    for each in s.args:
        if _type(each) is _pat:
            xs.append(each.value)
        elif _type(each) is _cmd:
            raise CommandNameCannotDecide
        else:
            collect_raw(xs, each)


class RushFastCompleter(ABC):
    registers: Dict[str, Callable[[Cmd, Pat, CompleteEvent], Completion]]

    def complete(self, last_cmd: Cmd, current_pattern: Pat, complete_event: CompleteEvent):
        fst = last_cmd.args[0]
        if isinstance(fst, Str):
            xs = []
            try:
                collect_raw(xs, fst)
                cmd_name = ''.join(xs)
            except CommandNameCannotDecide:
                return

        elif isinstance(fst, Pat):
            cmd_name = fst.value
        else:
            # CommandNameCannotDecide
            return
        return self.registers.get(cmd_name)(last_cmd, current_pattern, complete_event)


class RushAdaptorForPromptToolkit(Completer):
    def __init__(self, comp: RushFastCompleter):
        self.comp_func = comp.complete

    def get_completions(self, document: str, complete_event: CompleteEvent):
        cur_doc = document
        while True:
            try:
                ast = parse(cur_doc)
                break
            except ParseError as p:
                cur_doc = cur_doc[p.offset:]

        last_cmd, last_pattern = get_current(Cmd(structure_top(ast)))
        options = self.comp_func(last_cmd, last_pattern, complete_event)
        if options:
            yield from options
