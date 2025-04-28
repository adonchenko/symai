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
        if len(models) > 0:
            args["satisfiable"] = True
        else:
            args["satisfiable"] = False
        return args