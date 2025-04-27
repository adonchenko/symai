from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from symbolicexpressiongrammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

import sympy

import symaiexpr
import symaiconfig

class SymAIExpressionSymPy(symaiexpr.SymAIExpression):
    def __init__(self):
        super().__init__()
        self.set_solver(symaiconfig.SymAISolvers.SYMPY.value)

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
        return str(sympy.simplify(fml, rational=True, evaluate=True))
"""

expr_n = ((((((" " + expr + " ")
              .replace(" not ", " _n_o_t_ "))
             .replace("!", " not "))
            .replace("_d_o_t_", "__d__o__t__"))
           .replace(".", "_d_o_t_"))
          .strip(" "))

lexer = ExpressionGrammarLexer(InputStream(expr_n))
errorListener = SymbolicExpressionGrammarErrorListener()
lexer.removeErrorListeners()
lexer.addErrorListener(errorListener)
stream = CommonTokenStream(lexer)
parser = ExpressionGrammarParser(stream)
parser.removeErrorListeners()
parser.addErrorListener(errorListener)

tree = parser.expression()
visitor = SymbolicExpressionGrammarVisitor()
formula = visitor.visit(tree)

formula = str(sympy.simplify(formula))
formula = (((((" " + formula + " ")
              .replace("&", "&&")
              .replace("|", "||")
              .replace("_d_o_t_", "."))
             .replace("__d__o__t__", "_d_o_t_"))
            .replace(" not ", "!"))
           .replace(" _n_o_t_ ", " not ")).strip(" ")
except:
logger.error("error processing formula %s" % expr)
self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR,
                   "Bad request: error processing formula %s" % (expr))
else:
self.send_response(HTTPStatus.OK)
self.send_header("Content-Type", "application/json")
self.end_headers()

source_expr['formula'] = formula
logger.info("simplify %s -> %s" % (expr, formula))
self.wfile.write(json.dumps(source_expr).encode("utf8"))
else:
logger.error("Bad Request: must give data")
self.send_response(
    HTTPStatus.BAD_REQUEST, "Bad Request: must give data"
)
"""
