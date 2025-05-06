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

    def process_body_check(self, args):
        visitor = args.get("visitor")
        tree = args.get("tree")
        if tree is None or visitor is None:
            raise Exception("Error: process_body_check incorrect arguments")
        fml = visitor.visit(tree)
        check_vars = dict()
        lst = visitor.getVarList()

        solver = Solver()

        for n in lst:
            check_vars[n] = Real(n)

        check_vars["solver"] = solver
        glob_vars = dict()
        res = dict()
        exec("solver.add(" + fml + ")", glob_vars, check_vars)

        if solver.check() == sat:
            args["satisfiable"] = True
            m = solver.model()
            for dd in  m.decls():
                res[str(dd)] = str(m[dd])
        else:
            args["satisfiable"] = False
        args["model"] = res
        return args

    def process_body_inverse(self, args):
        raise Exception("Not implemented yet")