from typing import Any, List, Dict, Union, Set, Callable
from ppi.datatypes import Patch, Line, Chunk
import inspect
import re
from copy import deepcopy
import keyword
import os
from contextlib import redirect_stdout, redirect_stderr


# https://docs.python.org/ja/3/library/functions.html
builtin_functions = [
    "abs", "delattr", "hash", "memoryview", "set", "all", "dict",
    "help", "min", "setattr", "any", "dir", "hex", "next", "slice",
    "ascii", "divmod", "id", "object", "sorted", "bin", "enumerate",
    "input", "oct", "staticmethod", "bool", "eval", "int", "open",
    "str", "brteakpoint", "exec", "isinstance", "ord", "sum", "bytearray",
    "filter", "issubclass", "pow", "super", "bytes", "float", "iter",
    "print", "tuple", "callable", "format", "len", "property", "type",
    "chr", "frozenset", "list", "range", "vars", "classmethod", "getattr",
    "locals", "repr", "zip", "compile", "globals", "map", "reversed",
    "__import__", "complex", "hasattr", "max", "round"]


def get_symbols(globals: Dict[str, Any], locals: Union[None, Dict[str, Any]]):
    symbols = set(globals.keys())
    for kw in keyword.kwlist:
        symbols.add(kw)
    if locals is not None:
        for l in locals.keys():
            symbols.add(l)
    for b in dict(inspect.getmembers(globals["__builtins__"])).keys():
        symbols.add(b)
    for b in builtin_functions:
        symbols.add(b)

    return symbols


def copy(globals: Dict[str, Any], locals: Union[None, Dict[str, Any]]):
    new_globals = {}
    for key, value in globals.items():
        try:
            new_globals[key] = deepcopy(value)
        except TypeError:
            new_globals[key] = value
    new_locals = None if locals is None else {}
    if locals is not None:
        for key, value in locals.items():
            try:
                new_locals[key] = deepcopy(value)
            except TypeError:
                new_locals[key] = value
    return new_globals, new_locals


class Eval:
    def __init__(self, rules, max_patches: int, indent_size: int):
        self._rules = rules
        self._max_pathcs = max_patches
        self._indent_size = indent_size

    def _eval_or_exec(self, code: str, globals: Dict[str, Any],
                      locals: Union[None, Dict[str, Any]]):
        with redirect_stdout(open(os.devnull, "w")), \
                redirect_stderr(open(os.devnull, "w")):
            try:
                result = eval(code, globals, locals)
                return result, globals, locals
            except SyntaxError:
                exec(code, globals, locals)
                return None, globals, locals

    def _eval(self, code: List[Line], patches: List[Patch],
              symbols: Set[str],
              globals: Dict[str, Any], locals: Union[None, Dict[str, Any]]):
        lines = ["".join([c.text for c in line.chunks]) for line in code]
        text = "\n".join(lines)
        try:
            value, globals, locals = self._eval_or_exec(text, globals, locals)
            try:
                yield value, text, patches, globals, locals
            except GeneratorExit:
                return
            return
        except:  # noqa
            pass

        if len(patches) >= self._max_pathcs:
            return

        indents = set()
        for i, l in enumerate(code):
            text = "".join([c.text for c in l.chunks])
            m = re.search("^\\s*", text)
            indent = 0 if m is None else m.end()
            indents.add(indent)
            for rule in self._rules:
                for patch in rule(l, symbols, indents, self._indent_size):
                    l2 = patch.apply(l)
                    if l2 is None:
                        continue
                    new_globals, new_locals = copy(globals, locals)
                    new_code = code[:i] + [l2] + code[i + 1:]
                    new_patches = patches + [patch]
                    for v, s, p, g, loc in self._eval(new_code, new_patches,
                                                      symbols,
                                                      new_globals, new_locals):
                        try:
                            yield v, s, p, g, loc
                        except GeneratorExit:
                            return

    def __call__(self, code: str, globals: Dict[str, Any],
                 locals: Union[None, Dict[str, Any]],
                 callback: Callable[[str, List[Patch], Any], bool]):
        """
        Parameters
        ----------
        code: str
            The source code to be evaluated
        """
        symbols = get_symbols(globals, locals)
        lines = code.split("\n")
        lines = [Line([Chunk(0, line)]) for line in lines]
        for v, code, patches, g, l in self._eval(lines, [], symbols,
                                                 globals, locals):
            if callback(code, patches, v):
                return v, g, l, code
        return self._eval_or_exec(code, globals, locals), code
