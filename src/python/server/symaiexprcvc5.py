from cvc5.pythonic import *

from symbolicexpressiongrammarvisitor import *

import symaiexpr
import symaiconfig

class SymAIExpressionCVC5(symaiexpr.SymAIExpression):
    def __init__(self):
        super().__init__()
        self.set_solver(symaiconfig.SymAISolvers.CVC5.value)

    def process_body_simplify(self, args):
        visitor = SymbolicExpressionGrammarVisitor()
        tree = args.expression()
        fml = visitor.visit(tree)

        simplify_vars = dict()
        lst = visitor.getVarList()

        for n in lst:
            simplify_vars[n] = Real(n)

        glob_vars = dict()
        glob_vars["simplify"] = cvc5_pythonic.simplify
        res = eval("simplify(" + fml + ")", glob_vars, simplify_vars)

        p = self.preprocess(self.postprocess(str(res)))
        visitor = SymbolicExpressionGrammarVisitor()
        tree = p.expression()
        res = visitor.visit(tree)
        return str(res)
