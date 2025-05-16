from z3 import *
from symbolicexpressiongrammarvisitor import *

import symaiexpr
import symaiconfig

class SymAIExpressionZ3(symaiexpr.SymAIExpression):
    def __init__(self):
        super().__init__()
        self.set_solver(symaiconfig.SymAISolvers.Z3.value)

    def process_body_simplify(self, args):
        visitor = SymbolicExpressionGrammarVisitor()
        tree = args.expression()
        fml = visitor.visit(tree)

        simplify_vars = dict()
        lst = visitor.getVarList()

        for n in lst:
            simplify_vars[n] = Real(n)

        glob_vars = dict()
        glob_vars["And"] = And
        glob_vars["Or"] = Or
        glob_vars["Not"] = Not
        glob_vars["simplify"] = z3.simplify
        res = eval("simplify(" + fml + ")", glob_vars, simplify_vars)

        p = self.preprocess(self.postprocess(str(res)))
        visitor = SymbolicExpressionGrammarVisitor()
        tree = p.expression()
        res = visitor.visit(tree)
        return str(res)

    def process_body_check(self, args):
        visitor = args.get("visitor")
        tree = args.get("tree")
        if visitor is None or visitor is None:
            raise Exception("Error: process_body_check incorrect arguments")
        fml = visitor.visit(tree)
        check_vars = dict()
        lst = visitor.getVarList()

        solver = Solver()

        for n in lst:
            check_vars[n] = Real(n)
        glob_vars = dict()
        glob_vars["And"] = And
        glob_vars["Or"] = Or
        glob_vars["Not"] = Not
        glob_vars["solver"] = solver

        exec("solver.add(" + fml + ")", glob_vars, check_vars)
        res = dict()
        if solver.check() == sat:
            args["satisfiable"] = True
            m = solver.model()
            for dd in  m.decls():
                res[str(dd.name())] = str(m[dd])
        else:
            args["satisfiable"] = False
        args["model"] = res
        return args

    def process_body_inverse(self, args):
        raise Exception("Not implemented yet")