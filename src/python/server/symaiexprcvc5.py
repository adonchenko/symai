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
        glob_vars["And"] = cvc5_pythonic.And
        glob_vars["Or"] = cvc5_pythonic.Or
        glob_vars["Not"] = cvc5_pythonic.Not
        glob_vars["simplify"] = cvc5_pythonic.simplify
        res = eval("simplify(" + fml + ")", glob_vars, simplify_vars)

        p = self.preprocess(self.postprocess(str(res)))
        visitor = SymbolicExpressionGrammarVisitor()
        tree = p.expression()
        res = visitor.visit(tree)
        return str(res)

    def all_models(self, formula, global_vars, local_vars):
        " a generator of up to max models "
        solver = Solver()
        f2 = eval(formula, global_vars, local_vars)
        solver.add(f2)

        count = 0
        while count < self.get_max_models() or self.get_max_models() == 0:
            count += 1

            if solver.check() == sat:
                model = solver.model()
                yield model
                # exclude this model
                block = [False]
                for cvc5_decl in model:
                    f2 = eval(str(cvc5_decl) + "!=" + str(model[cvc5_decl]), global_vars, local_vars)
                    block.append(f2)
                    solver.add(Or(block))

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

        args["satisfiable"] = False
        lst = []
        for m in self.all_models(fml, glob_vars, check_vars):
            args["satisfiable"] = True
            dc = dict()
            for dd in m.decls():
                dc[str(dd)] = str(m[dd])
            lst.append(dc)
        args["model"] = lst

        return args

    def process_body_inverse(self, args):
        raise Exception("Not implemented yet")