import unittest
from ppi.datatypes import Line, Chunk, Range, Patch
import ppi.rules as R


class TestSpellMiss(unittest.TestCase):
    def test_spell_miss(self):
        line = Line([Chunk(0, "d g()")])
        self.assertEqual(
            [Patch(Range(0, 1), "def")],
            list(R.SpellMiss(line, set(["def"]), set()))
        )


class TestBlock(unittest.TestCase):
    def test_equal_sign(self):
        line = Line([Chunk(0, "([()")])
        self.assertEqual(
            [Patch(Range(-1, -1), "])")],
            list(R.CloseBrackets(line, set(), set()))
        )
        self.assertEqual(
            [Patch(Range(-1, -1), ":")],
            list(R.CloseBrackets(Line([Chunk(0, "def f()")]), set(), set()))
        )


class TestEqualSign(unittest.TestCase):
    def test_equal_sign(self):
        line = Line([Chunk(None, "x = 1"), Chunk(2, "x = 1")])
        self.assertEqual(
            [Patch(Range(4, 5), "==")],
            list(R.EqualSign(line, set(), set()))
        )
        self.assertEqual([],
                         list(R.EqualSign(
                             Line([Chunk(0, "x == 1")]), set(), set())))


class TestIndent(unittest.TestCase):
    def test_indent(self):
        line = Line([Chunk(0, "x = 1")])
        self.assertEqual(
            [Patch(Range(0, 0), "    ")],
            list(R.Indent(line, set(), set()))
        )

        line = Line([Chunk(0, "x = 1")])
        self.assertEqual(
            [Patch(Range(0, 0), "  ")],
            list(R.Indent(line, set(), set([2])))
        )

        line = Line([Chunk(0, "   x = 1")])
        self.assertEqual(
            set([Patch(Range(0, 3), "  "), Patch(Range(0, 3), "    ")]),
            set(R.Indent(line, set(), set([2]), 2))
        )


if __name__ == "__main__":
    unittest.main()
