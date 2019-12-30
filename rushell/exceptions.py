class ParseError(Exception):
    __slots__ = ['msg', 'offset']
    msg: str
    offset: int

    def show(self):
        cls = self.__class__.__name__
        return f'<p class="{cls}"> {cls}: {self.msg}'


class RushException(Exception):
    def show(self):
        cls = self.__class__.__name__
        return f'<p class="{cls}"> {cls}'


class CommandArgumentError(RushException):
    def __init__(self, msg=None):
        self.msg = msg or ""

    def show(self):
        cls = self.__class__.__name__
        return f'<p class="{cls}"> {cls} : {self.msg}'


class CommandNotFound(RushException):
    command_name: str

    def __init__(self, command_name: str):
        self.command_name = command_name

    def show(self):
        cls = self.__class__.__name__
        return f'<p class="{cls}"> {cls} : {self.command_name}'


class CommandContextUnset(RushException):
    pass
