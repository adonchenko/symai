from z3 import *
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from symbolicexpressiongrammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

import symaiexpr
import symaiconfig

class SymAIExpressionZ3(symaiexpr.SymAIExpression):
    def __init__(self):
        super().__init__()
        self.set_solver(symaiconfig.SymAISolvers.Z3.value)

    def postprocess(self, args):
        return (" " + args + " ").replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace("__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" ")

    def preprocess(self, args):
        expr_n = (" " + args + " ").replace(" not ", " _n_o_t_ ").replace("_d_o_t_", "__d__o__t__").strip(" ")
        lexer = ExpressionGrammarLexer(InputStream(expr_n))
        errorListener = SymbolicExpressionGrammarErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(errorListener)
        stream = CommonTokenStream(lexer)
        parser = ExpressionGrammarParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)

        return parser

    def process_body_simplify(self, args):
        visitor = SymbolicExpressionGrammarVisitor()
        tree = args.expression()
        fml = visitor.visit(tree)

        simplify_vars = dict()
        lst = visitor.getVarList()

        for n in lst:
            simplify_vars[n] = Real(n)

        glob_vars = dict()
        glob_vars["simplify"] = z3.simplify
        res = eval("simplify(" + fml + ")", glob_vars, simplify_vars)

        p = self.preprocess(self.postprocess(str(res)))
        visitor = SymbolicExpressionGrammarVisitor()
        tree = p.expression()
        res = visitor.visit(tree)
        return str(res)
