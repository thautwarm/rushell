import inspect
import types
from rushell.commands import ClassicCommandObject
from typing import List

from rushell.exceptions import CommandArgumentError

_empty = inspect._empty


def process_empty(x):
    if x is _empty:
        return None
    return x


def identity(x):
    return x


unset = object()


def describe_parameters(ps: List[inspect.Parameter]):
    positional = []
    varargs = None

    kwargs = {}
    var_kwargs = None
    docs = []
    for p in ps:
        kind = p.kind
        name = p.name
        anno = process_empty(p.annotation)
        default = process_empty(p.default)

        desc = ['', identity, unset, name]

        if anno:
            if anno is bool and default is False:
                desc[0] = f'use --{name} to set True'
            elif isinstance(anno, str):
                desc[0] = anno
            else:
                desc[0] = f'{name} will be converted to {anno}'
                desc[1] = anno

        if default:
            desc[2] = default
            desc[0] += f'; default to be {default!r}'

        if kind is inspect.Parameter.POSITIONAL_ONLY:
            positional.append(desc)

        elif kind is inspect.Parameter.VAR_POSITIONAL:
            varargs = desc
        elif kind is inspect.Parameter.KEYWORD_ONLY:
            kwargs[name] = desc
        elif kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
            kwargs[name] = desc
        elif kind is inspect.Parameter.VAR_KEYWORD:
            var_kwargs = desc

        docs.append((name, desc[0]))
    return docs, positional, varargs, kwargs, var_kwargs


def get_actual_arguments(args, kwargs: dict, pos, var, kws: dict, var_kw):
    pos = iter(pos)
    actual_args = []
    actual_kws = {}
    for i, arg in enumerate(args):
        try:
            [_, conv, _, _] = next(pos)
        except StopIteration:
            if not var:
                raise CommandArgumentError(f"too many positional arguments: {args}")
            [_, conv, _, _] = var
            actual_args.extend(conv(args[i:]))
            break

        actual_args.append(conv(arg))

    for [_, _, default, name] in pos:
        if default is unset:
            raise CommandArgumentError(f"{name} doesn't have default value")
        actual_args.append(default)

    kws = kws.copy()
    kwargs = list(kwargs.items())
    for i, (k, v) in enumerate(kwargs):
        try:
            [_, conv, _, _] = kws.pop(k)
        except KeyError:
            if not var_kw:
                raise CommandArgumentError(f"too many keyword arguments: {[k for k, _ in kwargs]}")
            [_, conv, _, _] = var_kw
            actual_kws.update(conv(dict(kwargs[i:])))
            break
        actual_kws[k] = conv(v)

    for k, [_, _, default, _] in kws.items():
        if default is unset:
            raise CommandArgumentError(f"{k} doesn't have default value")
        actual_kws[k] = default

    return actual_args, actual_kws


def from_python_fn(f: types.FunctionType, alias: str = None):
    """
    hints for style:

        def f(x: 'a' = 1):
            "doc!"
    ->

    f
    ===
    <ul class="argument-explanations">
       <li class="argument-annotation">
            <p class="argument-name"> x </p> :
            <p class="argument-note"> a ; default to be 1 </p>
        </li>
    </ul>
    <p class="function-documentation">doc!</p>
    """
    ps = list(inspect.Signature.from_callable(f).parameters.values())
    arg_docs, pos, var, kws, var_kw = describe_parameters(ps)

    def logic(args, kwargs):
        args, kwargs = get_actual_arguments(args, kwargs, pos, var, kws, var_kw)
        return f(*args, **kwargs)

    cco = ClassicCommandObject()
    cco.vararg_names = ()
    cco.logic = logic

    doc = f.__doc__ or ''
    arg_anns = '\n'.join('<li class="argument-annotation">'
                         f'<p class="argument-name">{n}</p> : <p class="argument-note">{d}</p>'
                         '</li>' for n, d in arg_docs)
    cco.doc = '<ul class="argument-explanations">' + arg_anns + '</ul>\n<p class="function-documentation">' + doc + '</p>'
    command_name = alias or f.__name__
    cco.name = command_name
    return cco
