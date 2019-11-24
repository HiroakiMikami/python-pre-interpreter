import unittest
from ppi.datatypes import Line, Chunk, Range, Patch


class TestLine(unittest.TestCase):
    def test_normalize(self):
        line = Line([
            Chunk(None, "s0"),
            Chunk(None, "s1"),
            Chunk(0, "s2"),
            Chunk(2, "s3"),
            Chunk(7, ""),
            Chunk(10, "s4"),
            Chunk(20, "")
        ])
        line.normalize()
        self.assertEqual(
            [Chunk(None, "s0s1"), Chunk(0, "s2s3"), Chunk(10, "s4")],
            line.chunks
        )


class TestPatch(unittest.TestCase):
    def test_apply(self):
        p = Patch(Range(2, 4), "foo")
        line = Line([Chunk(0, "0123456789")])
        self.assertEqual(
            Line([Chunk(0, "01"), Chunk(None, "foo"), Chunk(4, "456789")]),
            p.apply(line))

        line = Line([Chunk(None, "foo"), Chunk(0, "0123456789")])
        self.assertEqual(
            Line([Chunk(None, "foo"), Chunk(0, "01"),
                  Chunk(None, "foo"), Chunk(4, "456789")]),
            p.apply(line))

        line = Line([Chunk(None, "foo"), Chunk(3, "3456789")])
        self.assertEqual(None, p.apply(line))

        line = Line([Chunk(0, "012")])
        self.assertEqual(None, p.apply(line))

        p = Patch(Range(-1, -1), "foo")
        self.assertEqual(Line([Chunk(0, "012"), Chunk(None, "foo")]),
                         p.apply(line))


if __name__ == "__main__":
    unittest.main()
