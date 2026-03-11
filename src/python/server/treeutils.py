from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from symbolicexpressiongrammarerrorlistener import *
from BehaviorsGrammar.BehaviorsGrammarLexer import BehaviorsGrammarLexer
from BehaviorsGrammar.BehaviorsGrammarParser import BehaviorsGrammarParser

class TreeUtils:

    @staticmethod
    def check_const(vl : str):
        t = False
        try:
            s = str(eval(vl))
            vl = s
            ret = True
        except :
            ret = False
        if vl == "True" or vl == "1":
            t = True
        elif vl == "False":
            t = False
        else:
            try:
                t = float(vl)
                if t == 0:
                    ret = False
                else:
                    ret = True
            except ValueError:
                ret = False
            except Exception:
                ret = False

        return ret, t

    @staticmethod
    def get_float(s: str):
        try:
            my_float = float(str(eval(s)))
            return True, my_float
        except ValueError:
            return False, 0
        except NameError as e:
            return False, 0
        except TypeError as e:
            return False, 0
        except ZeroDivisionError as e:
            return False, 0
        except Exception:
            return False, 0

    @staticmethod
    def prepare_parser_beh(inp: str) -> BehaviorsGrammarParser:
        lexer = BehaviorsGrammarLexer(InputStream(inp))
        error_listener = SymbolicExpressionGrammarErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        stream = CommonTokenStream(lexer)
        parser = BehaviorsGrammarParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        return parser

    @staticmethod
    def get_vars_using_assignment(expr: str)->tuple[dict, dict, str]:
        from eqextractvisitor import EQExtractorVisitor
        tr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
        v = EQExtractorVisitor()
        tail = v.visit(tr)
        cvals = v.getCVals()
        cv = dict()
        for it in cvals.keys():
            t, f = TreeUtils.get_float(cvals[str(it)])
            if t:
                cv[str(it)] = f
            else:
                cv[it] = cvals[str(it)]
        vals = v.getVals()
        return cv, vals, tail

