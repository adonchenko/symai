from sympy import solve

from symbolicexpressiongrammarvisitor import *

import sympy

import symaiexpr
import symaiconfig

class SymAIExpressionSymPy(symaiexpr.SymAIExpression):
    def __init__(self):
        super().__init__()
        self.set_solver(symaiconfig.SymAISolvers.SYMPY.value)

    def process_body_simplify(self, args):
        visitor = SymbolicExpressionGrammarVisitor()
        tree = args.expression()
        fml = visitor.visit(tree)
        lst = visitor.getVarList()
        check_vars = dict()

        for n in lst:
            check_vars[n] = sympy.Symbol(n, real=True)
        glob_vars = dict()
        glob_vars["And"] = sympy.And
        glob_vars["Or"] = sympy.Or
        glob_vars["Not"] = sympy.Not

        f2 = eval(fml, glob_vars, check_vars)

        return str(sympy.simplify(f2))


    def process_body_check(self, args):
        visitor = args.get("visitor")
        tree = args.get("tree")

        if tree is None or visitor is None or visitor is None:
            raise Exception("Error: process_body_check incorrect arguments")
        fml = visitor.visit(tree)
        models = sympy.satisfiable(fml)

        res = dict()
        if models and len(models) > 0:
            lst = visitor.getVarList()
            check_vars = dict()
            s = ""
            if len(lst) > 0:
                s = "("
                b = False
                for n in lst:
                    if b:
                        s = s + ","
                    s = s + n
                    b = True
                    check_vars[n] = sympy.symbols(n, real=True)
                s = s + ")"
            glob_vars = dict()
            glob_vars["And"] = sympy.And
            glob_vars["Or"] = sympy.Or
            glob_vars["Not"] = sympy.Not
            glob_vars["solve"] = sympy.solveset
            f2 = eval(fml, glob_vars, check_vars)
            sm = eval(s, glob_vars, check_vars)
            ss = set()
            solutions = sympy.solve(f2, sm, dict=True)
            for it in solutions:
                for jj in it:
                    res[str(jj)] = str(it[jj])
        else:
            args["satisfiable"] = False
        args["model"] = res
        if len(res) <= 0:
            args["satisfiable"] = False
        return args

    def process_body_inverse(self, args):
        visitor = args.get("visitor")
        tree = args.get("tree")
        tv = args.get("target")
        expr = args["formula"]
        if tree is None or visitor is None or visitor is None or tv is None:
            raise Exception("Error: process_body_inverse incorrect arguments")
        fml = visitor.visit(tree)
        models = sympy.satisfiable(fml)
        res = dict()
        if models:
            args["satisfiable"] = True
            lst = visitor.getVarList()
            check_vars = dict()
            if len(lst) > 0:
                for n in lst:
                    check_vars[n] = sympy.symbols(n)
            glob_vars = dict()
            glob_vars["solve"] = sympy.solve
            solutions = eval("solve(" + expr + "," + tv + ")", glob_vars, check_vars)
            res[tv] = str(solutions[0])
        else:
            args["satisfiable"] = False
        args["inverse"] = res
        return args
