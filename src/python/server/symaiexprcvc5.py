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

        simplify_vars = {"res" : ""}
        expr = "from cvc5.pythonic import *\n"
        lst = visitor.getVarList()
        for n in lst:
            expr = expr + n + "=Real(\"" + n + "\")\n"
        expr = expr + "res=simplify(" + fml + ")\n"
        exec(expr, {"And": And, "Or": Or, "Not": Not, "Eq": eq}, simplify_vars)
        res = simplify_vars["res"]

        p = self.preprocess(self.postprocess(str(res)))
        visitor = SymbolicExpressionGrammarVisitor()
        tree = p.expression()
        res = visitor.visit(tree)
        return str(res)

    def all_models(self, formula, global_vars, local_vars):
        """ a generator of up to max models """
        solver = global_vars["solver"]
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
        if visitor is None or tree is None:
            raise Exception("Error: process_body_check incorrect arguments")
        fml = visitor.visit(tree)
        check_vars = dict()
        lst = visitor.getVarList()

        solver = Solver()

        for n in lst:
            check_vars[n] = Real(n)
        glob_vars = {"And": And, "Or": Or, "Not": Not, "solver": solver, "Eq": eq}

        b = False
        lst = []
        for m in self.all_models(fml, glob_vars, check_vars):
            b = True
            dc = dict()
            for dd in m.decls():
                dc[str(dd)] = str(m[dd])
            lst.append(dc)
        args["model"] = lst
        args["satisfiable"] = b
        return args

    def process_body_inverse(self, args):
        raise Exception("Not implemented yet")