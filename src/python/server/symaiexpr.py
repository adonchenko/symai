from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from symbolicexpressiongrammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

class SymAIExpression:

    def __init__(self):
        self.solver = None

    def get_solver(self):
        return self.solver

    def set_solver(self, slvr):
        self.solver = slvr

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

    def process_body(self, args):
        raise Exception("postprocess method is not implemented yet")

    def preprocess_simplify(self, args):
        return self.preprocess(args)

    def postprocess_simplify(self, args):
        return self.postprocess(args)

    def process_body_simplify(self, args):
        return self.process_body(args)

    def process_simplify(self, source_expr):
        expr = source_expr.get("formula")
        if expr is None:
            raise Exception("Bad Request: missing formula field")
        else:
            res = self.postprocess_simplify(self.process_body_simplify(self.preprocess_simplify(expr)))
            source_expr["formula"] = res
            return source_expr

    def preprocess_check(self, args):
        return self.preprocess(args)

    def postprocess_check(self, args):
        args.pop("visitor")
        return args

    def process_body_check(self, args):
        return self.process_body(args)

    def process_check(self, source_expr):
        expr = source_expr.get("formula")
        if expr is None:
            raise Exception("Bad Request: missing formula field in check request")
        else:
            parser = self.preprocess_check(expr)

            subs = source_expr.get("substitution")
            if subs is None:
                subs = dict()
            tree = parser.expression()
            visitor = SymbolicExpressionGrammarVisitor()
            visitor.setSubstitution(subs)
            fml = str(visitor.visit(tree))
            formula = self.postprocess(fml)
            source_expr["formula"] = formula
            source_expr["is_trigonometric"] = visitor.isTrigonometric()
            source_expr["is_nonlinear"] = visitor.isNonLinear()
            source_expr["vars"] = visitor.getVarList()
            source_expr["substitution"] = visitor.getSubstitution()
            source_expr["visitor"] = visitor

            source_expr = self.process_body_check(source_expr)
            return self.postprocess_check(source_expr)
