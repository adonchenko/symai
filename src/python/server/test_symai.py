import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/")

from testsymaicore import *

import unittest

class SymAITestCase(unittest.TestCase):
    def test_get_vars_using_assignment(self):
        test_data = [["(a.d.f==3==b) && c(s) > d && e(125) == 22|| f == g + 125 && h <= i", [{'a.d.f': 3.0, 'b': 3.0, 'e(125)': 22.0}, {'f': 'g+125'}, "c(s)>d || h<=i"]],
                     ["(a.d.f>=3==b) && c(s) == d && e(125) > 22|| f != g + 125 && h <= i", [{'b': 3.0}, {'c(s)''' : 'd''', 'f': 'g+125' }, "(a.d.f>=3) && e(125)>22 || h<=i"]]]
        for it in test_data:
            a, b, c = TreeUtils.get_vars_using_assignment(it[0])
            self.assertEqual(c, it[1][2], "Resulting expression is unexpected")
            self.assertEqual(len(a), len(it[1][0]), "Number of extracted constants is incorrect")
            for i in a.keys():
                f = False
                for j in it[1][0].keys():
                    if it[1][0][j] == a[i]:
                        f = True
                        break
                self.assertEqual(f, True, f"Variable {i} must not be included to extracted constants")

            self.assertEqual(len(b), len(it[1][1]), "Number of extracted symbolic expressions is incorrect")
            for i in b.keys():
                f = False
                for j in it[1][1].keys():
                    if it[1][1][j] == b[i]:
                        f = True
                        break
                self.assertEqual(f, True, f"Variable {i} must not be included to extracted symbolic expressions")

    def test_do_remove_vars(self):
        test_data = [["n<a && b > h", ['a'], "b>h"],
                     ["n<a && b > h", ['a', 'h'],""],
                     ["n<a && b > h", ['h'],"n<a"],
                     ["((n<a) && (c == 10)) && (b > h)", ['b'],"((n<a) && (c==10))"]]
        cc = SymAICoreCommands()
        for it in test_data:
            s = cc.do_remove_vars(it[0], it[1])
            self.assertEqual(s, it[2], "Incorrect result")
            p = TreeUtils.prepare_parser_expr(s)
            self.assertIsNotNone(p, "Incorrect syntax of the result")
            if len(s) > 0:
                tr = p.assignmentExpression()
                self.assertIsNotNone(tr, "Cannot parse result")

    def test_action_has_logical(self):
        test_data = [["a=345", False],
                     ["a = a + 1; y = y + 1; c >= 10 && b == x", True],
                     ["h = 123;((a > b && c > d || (e == f) && (a == 4 && c == g)))", True]]
        for it in test_data:
            tr = TreeUtils.prepare_parser_expr(it[0]).assignmentExpressionList()
            v = ExtSEGrammarVisitor()
            b = v.action_has_logical(tr)
            self.assertEqual(b, it[1], "Incorrect result")

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(SymAITestCase('test_get_vars_using_assignment'))
    suite.addTest(SymAITestCase('test_do_remove_vars'))
    suite.addTest(SymAITestCase('test_action_has_logical'))
    suite.addTest(SymAICoreTestCase('test_do_actions'))
    suite.addTest(SymAICoreTestCase('test_do_behaviors'))
    suite.addTest(SymAICoreTestCase('test_do_property'))
    runner = unittest.TextTestRunner()
    runner.run(suite)