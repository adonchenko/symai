import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/")
from treeutils import *
import unittest

class SymAITestCase(unittest.TestCase):
    def test_get_vars_using_assignment(self):
        test_data = [["(a.d.f==3==b) && c(s) > d && e(125) == 22|| f == g + 125 && h <= i", [{'a.d.f': 3.0, 'b': 3.0, 'e(125)': 22.0}, {'f': 'g+125'}, "c(s)>d || h<=i"]],\
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

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(SymAITestCase('test_get_vars_using_assignment'))
    runner = unittest.TextTestRunner()
    runner.run(suite)