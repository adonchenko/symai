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
        return str(sympy.simplify(fml, rational=True, evaluate=True))

    def process_body_check(self, args):
        fml = args.get("formula")
        visitor = args.get("visitor")
        if fml is None or visitor is None:
            raise Exception("Error: process_body_check incorrect arguments")
        models = sympy.satisfiable(fml)
        x, y, z = sympy.symbols("x y z")
        solution = sympy.solve(fml, (x, y, z), dict=True)
        res = dict()
        if models:
            args["satisfiable"] = True
            lst = visitor.getVarList()
            check_vars = dict()
            s = ""
            if len(lst) > 0:
                s = ",("
                b = False
                for n in lst:
                    if b:
                        s = s + ","
                    s = s + n
                    b = True
                    check_vars[n] = sympy.symbols(n)
                s = s + ")"
            glob_vars = dict()
            glob_vars["solve"] = sympy.solve
            solutions = eval("solve(" + fml + s + ", dict=True)", glob_vars, check_vars)
            for it in solutions:
                for jj in it:
                    res[str(jj)] = str(it[jj])
        else:
            args["satisfiable"] = False
        args["model"] = res
        return args
    