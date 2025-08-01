from z3 import *
from symbolicexpressiongrammarvisitor import *

import itertools
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
        glob_vars["Eq"] = z3.eq
        glob_vars["simplify"] = z3.simplify
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
        while count < self.get_max_models():
            count += 1

            if solver.check() == sat:
                model = solver.model()
                yield model

                # exclude this model
                block = []
                for z3_decl in model:  # FuncDeclRef
                    arg_domains = []
                    for i in range(z3_decl.arity()):
                        domain, arg_domain = z3_decl.domain(i), []
                        for j in range(domain.num_constructors()):
                            arg_domain.append(domain.constructor(j)())
                        arg_domains.append(arg_domain)
                    for args in itertools.product(*arg_domains):
                        f2  = eval(str(z3_decl(*args)) + "!=" + str(model.eval(z3_decl(*args))), global_vars, local_vars)
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
        glob_vars["Eq"] = z3.eq
        glob_vars["solver"] = solver

        f2 = eval(fml, glob_vars, check_vars)

        solver.add(f2)
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