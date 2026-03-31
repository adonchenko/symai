from symaicorecommands import *

import unittest

class SymAIActivitiesTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = None

    def test_do_parse_act(self):
        test_data = [
            [
                "a2: 1 -> ((x == (V0 + 9.96)*t - 4.98) && (1 <= t <= 3.25)) || ((x == (V0 + 54.78)*t - 150.645) && (3.25 <= t <= 7.75)) || ((x == (V0 + 99.6)*t - 498) && (7.75 <= t <= 10)),",
                "a2:0<1->((x==(V0+9.96)*t-4.98)&&(1<=t&&t<=3.25))||((x==(V0+54.78)*t-150.645)&&(3.25<=t&&t<=7.75))||((x==(V0+99.6)*t-498)&&(7.75<=t&&t<=10)),"
            ],
            [
                "a2:a<b->c=0,a1: True-> ,",
                "a2:a<b->c=0,a1:0<1->1,"
            ],
            [
              "a1: True-> ,a2:a<b->c=0,",
              "a1:0<1->1,a2:a<b->c=0,"
            ],
            [
              "a1: True-> ,",
              "a1:0<1->1,"
            ],
            [
              "a1: 1-> 1,",
              "a1:0<1->1,"
            ],
            [
                "a(1): a > b -> c = a + b, a(2): a < b -> c = b - a, a(3): a == b -> a = c - b, a(4): 1 -> a = b + c,",
                "a(1):a>b->c=a+b,a(2):a<b->c=b-a,a(3):a==b->a=c-b,a(4):0<1->a=b+c,"
            ]
        ]

        for it in test_data:
            s = str(it[0])
            self.parser = TreeUtils.prepare_parser_beh(s)
            tr = self.parser.actions()
            v = ActGrammarVisitor()
            res = v.visit(tr)
            self.assertEqual(it[1], res, "Expected actions are not equal to expected result")
            act = v.getResults()
            # behaviors = v.getResults()
            # self.assertEqual(len(it[1]), len(behaviors), "does not match behaviors number")
            # bk = behaviors.keys()
            # for bname in it[1]:
            #    self.assertTrue(bname in bk, "does not match behaviors key")


    def tearDown(self):
        self.parser = None
