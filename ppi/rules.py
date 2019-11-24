from typing import Set
from ppi.datatypes import Line, Patch, Range
import re
import bisect
import Levenshtein


def SpellMiss(line: Line, symbols: Set[str],
              indents: Set[int], default_indent: int = 4):
    """
    Correct spell miss

    Parameters
    ----------
    line: Line
        line to be preprocessed
    symbols: Set[str]
        Symbols defined in this context
    indents: Set[int]
        Set of indents
    default_indent: int
        The default indent size

    Yields
    ------
    Patch
        Patch to be applied
    """
    symbols_dict = {}
    for symbol in symbols:
        symbols_dict[symbol.lower()] = symbol

    for chunk in line.chunks:
        if chunk.offset is None:
            continue
        for m in re.finditer("\\w+", chunk.text):
            s = m.start()
            e = m.end()
            token = m.string[s:e]
            token_key = token.lower()

            if token_key in symbols_dict:
                continue

            candidates = []
            for symbol_key, symbol in symbols_dict.items():
                threshold = max(len(token_key), len(symbol_key))
                dist = Levenshtein.distance(token_key, symbol_key)
                if dist < threshold:
                    candidates.append([dist,
                                       Patch(Range(chunk.offset + s,
                                                   chunk.offset + e),
                                             symbol)])

            candidates.sort(key=lambda x: x[0])
            for _, patch in candidates:
                yield patch


def CloseBrackets(line: Line, symbols: Set[str],
                  indents: Set[int], default_indent: int = 4):
    """
    Close brackets

    Parameters
    ----------
    line: Line
        line to be preprocessed
    symbols: Set[str]
        Symbols defined in this context
    indents: Set[int]
        Set of indents
    default_indent: int
        The default indent size

    Yields
    ------
    Patch
        Patch to be applied
    """
    text = "".join([c.text for c in line.chunks])

    stack = []
    for ch in text:
        if ch == "(":
            stack.append(")")
        elif ch == "[":
            stack.append("]")
        elif ch == ")":
            stack.pop(-1)
        elif ch == "]":
            stack.pop(-1)
    stack.reverse()
    patch = "".join(stack)

    block = re.search(
        "def|if|elif|else|for|while|try|catch|finally|with", text)
    if block is not None and not text.endswith(":"):
        patch += ":"
    if patch != "":
        yield Patch(Range(-1, -1), patch)


def EqualSign(line: Line, symbols: Set[str],
              indents: Set[int], default_indent: int = 4):
    """
    Replace substition into equal sign

    Parameters
    ----------
    line: Line
        line to be preprocessed
    symbols: Set[str]
        Symbols defined in this context
    indents: Set[int]
        Set of indents
    default_indent: int
        The default indent size

    Yields
    ------
    Patch
        Patch to be applied
    """
    for chunk in line.chunks:
        if chunk.offset is not None:
            for m in re.finditer("(?<=[^=!><])=(?=[^=])", chunk.text):
                yield Patch(Range(chunk.offset + m.start(),
                                  chunk.offset + m.end()), "==")


def Indent(line: Line, symbols: Set[str],
           indents: Set[int], default_indent: int = 4):
    """
    Fix indent

    Parameters
    ----------
    line: Line
        line to be preprocessed
    symbols: Set[str]
        Symbols defined in this context
    indents: Set[int]
        Set of indents
    default_indent: int
        The default indent size

    Yields
    ------
    Patch
        Patch to be applied
    """
    if len(line.chunks) == 0:
        return
    if line.chunks[0].offset is None:
        return
    text = line.chunks[0].text
    m = re.search("^\\s*", text)
    indent = 0 if m is None else m.end()

    indents = indents if len(indents) > 0 else [0]
    indents = list(indents) + [max(indents) + default_indent]
    indents.sort()
    index = bisect.bisect_right(indents, indent)
    if index > 0:
        i = indents[index - 1]
        if i != indent:
            yield Patch(Range(0, indent), " " * i)
    i = indents[index]
    if i != indent:
        yield Patch(Range(0, indent), " " * i)
