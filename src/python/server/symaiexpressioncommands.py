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
                solver_name = source_expr.get("solver")
                if solver_name is None:
                    solver_name = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value)
                self.get_logger().info(f"Check request received. Source formula is '{expr}. Solver is '{solver_name}'")

                solver = self.do_check_solver(solver_name)
                return solver.process_check(source_expr)

    def do_inverse(self, source : str):
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
                self.get_logger().info(f"Inverse request received. Source formula is '{expr}. Solver is '{solver_name}'")

                solver = self.do_check_solver(solver_name)
                return solver.process_inverse(source_expr)
