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
        visitor.setIsEq(True)
        tree = args.expression()
        fml = visitor.visit(tree)
        s = str(sympy.simplify(sympy.parse_expr(fml)))
        r = self.preprocess_simplify(s.replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace("__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" "))
        visitor = SymbolicExpressionGrammarVisitor()
        visitor.setIsEq(True)
        tree = r.expression()
        res = visitor.visit(tree)
        return res

    def process_body_check(self, args):
        visitor = args.get("visitor")
        visitor.setIsEq(True)
        tree = args.get("tree")
        if tree is None or visitor is None or visitor is None:
            raise Exception("Error: process_body_check incorrect arguments")
        fml = visitor.visit(tree)
        args["satisfiable"] = False
        lst = visitor.getVarList()
        if len(lst) > 0:
            check_vars = dict()
            for n in lst:
                check_vars[n] = sympy.Symbol(n, real=True)
            glob_vars = dict()
            glob_vars["And"] = sympy.And
            glob_vars["Or"] = sympy.Or
            glob_vars["Eq"] = sympy.Eq
            glob_vars["Ne"] = sympy.Ne
            glob_vars["simplify"] = sympy.simplify
            s = "simplify(" + fml + ")"
            f2 = eval(s, glob_vars, check_vars)
            if str(type(f2)) != "<class 'sympy.logic.boolalg.BooleanFalse'>" and str(type(f2)) != "<class 'sympy.logic.boolalg.BooleanTrue'>":
                args["satisfiable"] = True
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
        if not models is None and len(models) > 0:
            args["satisfiable"] = True
            lst = visitor.getVarList()
            check_vars = dict()
            if len(lst) > 0:
                for n in lst:
                    check_vars[n] = sympy.symbols(n)
            glob_vars = dict()
            glob_vars["solve"] = sympy.solve
            solutions = eval("solve(" + expr + "," + tv + ")", glob_vars, check_vars)
            if solutions is None:
                res[tv] = expr
            elif isinstance(solutions, str):
                res[tv] = solutions
            elif len(solutions) > 0:
                res[tv] = str(solutions[0])
            else:
                res[tv] = expr
        else:
            args["satisfiable"] = False
        args["inverse"] = res
        return args
