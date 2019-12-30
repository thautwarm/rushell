from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document
from rushell.parser_wrap import parse, ParseError
from rushell.structured import get_current, structure_top, Cmd, Str, Concat
from abc import ABC
from typing import List, Callable, Dict


class CommandNameCannotDecide(Exception):
    pass


def collect_raw(xs: List[str], s: Concat):
    """Deciding the command name from a `Str`"""
    _pat = Str
    _str = Concat
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
    registers: Dict[str, Callable[[Cmd, Str, CompleteEvent], Completion]]

    def __init__(self):
        self.registers = {}

    def add(self, command_name: str, completer: Callable[[Cmd, Str, CompleteEvent], Completion]):
        self.registers[command_name] = completer

    def complete(self, last_cmd: Cmd, current_pattern: Str, complete_event: CompleteEvent):
        fst = last_cmd.args[0]
        if isinstance(fst, Concat):
            xs = []
            try:
                collect_raw(xs, fst)
                cmd_name = ''.join(xs)
            except CommandNameCannotDecide:
                return

        elif isinstance(fst, Str):
            cmd_name = fst.value
        else:
            # CommandNameCannotDecide
            return
        f = self.registers.get(cmd_name)
        if f is None:
            return
        return f(last_cmd, current_pattern, complete_event)


class RushAdaptorForPromptToolkit(Completer):
    def __init__(self, comp: RushFastCompleter):
        self.comp_func = comp.complete

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        cur_doc = document.text
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
