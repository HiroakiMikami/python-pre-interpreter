import os
import sys
from typing import List

from ppi.eval import Eval
from ppi.datatypes import Patch
import ppi.rules as R


def main():
    filename = sys.argv[1]
    max_patches = int(os.environ.get("PPI_MAX_PATCHES", 3))
    indent_size = int(os.environ.get("PPI_INDENT_SIZE", 4))
    e = Eval(
        [R.SpellMiss, R.CloseBrackets, R.Indent, R.EqualSign],
        max_patches,
        indent_size
    )
    with open(filename, "r") as file:
        lines = file.readlines()

    def callback(code: str, patches: List[Patch], value):
        if len(patches) == 0:
            return True
        print(code)
        print("Patches:")
        for p in patches:
            print("  {}".format(p))
        sys.stdout.write("Accept this patch? [Y/n]")
        sys.stdout.flush()
        if input().lower() == "n":
            return False
        return True

    _, _, _, code = e("".join(lines), globals(), locals(), callback)
    try:
        eval(code)
    except SyntaxError:
        exec(code)
