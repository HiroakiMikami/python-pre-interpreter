import unittest
from ppi.eval import Eval
import ppi.rules as R
import builtins


class TestEval(unittest.TestCase):
    def test_simple_case(self):
        _globals = {"__name__": "__main__", "__package__": None,
                    "__doc__": None, "__builtins__": builtins}
        e = Eval([R.Indent, R.CloseBrackets], 2, 2)

        def callback(s, patches, value):
            return True
        value, _globals, _, _ = e("def f()\nreturn 10", _globals, None,
                                  callback)
        self.assertEqual(None, value)
        self.assertTrue("f" in _globals)
        value, _globals, _, _ = e("f(", _globals, None, callback)
        self.assertEqual(10, value)

    def test_multiple_candidates(self):
        _globals = {"__name__": "__main__", "__package__": None,
                    "__doc__": None, "__builtins__": builtins}
        e = Eval([R.SpellMiss], 2, 2)

        def callback(s, patches, value):
            return "add" in s
        _, _globals, _, _ = e("def add(x, y):\n  return x + y", _globals,
                              None, callback)
        _, _globals, _, _ = e("def add2(x, y):\n  return x + y", _globals,
                              None, callback)
        value, _globals, _, _ = e("dad(1, 2)", _globals, None, callback)
        self.assertEqual(3, value)


if __name__ == "__main__":
    unittest.main()
