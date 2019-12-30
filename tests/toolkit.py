from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import prompt


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        print(document)
        # Display this completion, black on yellow.
        yield Completion('completion1', start_position=0, style='bg:ansiyellow fg:ansiblack')

        # Underline completion.
        yield Completion('completion2', start_position=0, style='underline')


text = prompt('> ', completer=MyCustomCompleter())
