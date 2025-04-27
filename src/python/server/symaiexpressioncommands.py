import json
import symaicommands
import symaiconfig
import symaiexpr
import symaiexprsympy
import symaiexprz3
import symaiexprcvc5
from symbolicexpressiongrammarvisitor import *

class SymAIExpressionCommands(symaicommands.SymAICommands):

    def do_check_solver(self, solver_name : str)->symaiexpr.SymAIExpression():
        match solver_name:
            case symaiconfig.SymAISolvers.BASE.value:
                return symaiexpr.SymAIExpression()
            case symaiconfig.SymAISolvers.SYMPY.value:
                return symaiexprsympy.SymAIExpressionSymPy()
            case symaiconfig.SymAISolvers.CVC5.value:
                return symaiexprcvc5.SymAIExpressionCVC5()
            case symaiconfig.SymAISolvers.Z3.value:
                return symaiexprz3.SymAIExpressionZ3()
            case default: raise Exception(f"Not implemented solver type {solver_name}")

    def do_shutdown(self):
        self.get_logger().info("Shutdown received")

    def do_simplify(self, source : str):
        try:
            source_expr = json.loads(source)
        except Exception as e:
            raise Exception(f"Bad Request: incorrect syntax of json request {str(e)}")
        else:
            expr = source_expr.get("formula")
            if expr is None:
                raise Exception("Bad Request: missing formula field")
            else:
                solver_name = source_expr.get("solver")
                if solver_name is None:
                    solver_name = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value)
                solver = self.do_check_solver(solver_name)
                self.get_logger().info(f"Simplify request received. Solver is '{solver_name}' and source formula is '{expr}'")
        return solver.process_simplify(source_expr)

    def do_check(self, source : str):
        try:
            source_expr = json.loads(source)
        except Exception as e:
            raise Exception(f"Bad Request: incorrect syntax of json request {str(e)}")
        else:
            expr = source_expr.get("formula")
            if expr is None:
                raise Exception("Bad Request: missing formula field")
            else:
                subs = source_expr.get("substitution")
                if subs is None:
                    subs = dict()
                solver = self.do_check_solver(symaiconfig.SymAISolvers.BASE.value)
                parser = solver.preprocess(expr)
                tree = parser.expression()
                visitor = SymbolicExpressionGrammarVisitor()
                visitor.setSubstitution(subs)
                formula = solver.postprocess(str(visitor.visit(tree)))
                source_expr["formula"] = formula
                source_expr["is_trigonometric"] = visitor.isTrigonometric()
                source_expr["is_nonlinear"] = visitor.isNonLinear()
                source_expr["vars"] = visitor.getVarList()
                source_expr["substitution"] = visitor.getSubstitution()
                self.get_logger().info(f"Check request received. Source formula is '{expr}'")
        return source_expr