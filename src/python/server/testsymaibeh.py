from symaicorecommands import *

import unittest

class SymAIBehaviorsTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = None

    def test_do_parse_expr(self):
        test_data = [
            [
                "a.b(0)!=c==q&&g==5||v==10",
                "a.b(0)!=c&&c==q&&g==5||v==10"
            ]
        ]
        for it in test_data:
            self.parser = TreeUtils.prepare_parser_beh(it[0])
            tr = self.parser.expression()
            v = BehGrammarVisitor()
            s = v.visit(tr)
            self.assertEqual(s, it[1], "Expression does not match to expected")

    def test_do_parse_beh(self):
        test_data = [
            [
                "ENGINE_WORKCYCLE(0)= checkCrankshaftRotationAngle . getCrankshaftRotationSin .(STROKE1 + isStroke2 + isStroke3 + isStroke4) .changeCrankshaftRotationAngle1 . ENGINE_WORKCYCLE + notCheckCrankshaftRotationAngle,",
                ["ENGINE_WORKCYCLE(0)"]
            ],
            [
                "ENGINE_WORKCYCLE(0+1)= checkCrankshaftRotationAngle . getCrankshaftRotationSin .(STROKE1 + isStroke2 + isStroke3 + isStroke4) .changeCrankshaftRotationAngle1 . ENGINE_WORKCYCLE + notCheckCrankshaftRotationAngle,",
                ["ENGINE_WORKCYCLE(0+1)"]
            ]
        ]

        for it in test_data:
            s = str(it[0])
            self.parser = TreeUtils.prepare_parser_beh(s)
            tr = self.parser.behaviors()
            v = BehGrammarVisitor()
            v.visit(tr)
            behaviors = v.getBehaviors()
            self.assertEqual(len(it[1]), len(behaviors), "does not match behaviors number")
            bk = behaviors.keys()
            for bname in it[1]:
                self.assertTrue(bname in bk, "does not match behaviors key")


    def tearDown(self):
        self.parser = None