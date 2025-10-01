from extsegammarvisitor import *
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from treeedit import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

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

        return ret, t

    @staticmethod
    def get_float(s: str):
        try:
            my_float = float(s)
            return True, my_float
        except ValueError:
            return False, 0

    @staticmethod
    def extract_eq_values_def(tree):
        values = dict()
        concrete_values = dict()
        if str(type(tree)) == "<class 'ExpressionGrammar.ExpressionGrammarParser.ExpressionGrammarParser.EqualityExpressionContext'>":
            if tree is not None:
                i = 1
                is_deleted = False
                vt = ExtSEGrammarVisitor()
                first_arg = vt.visit(tree.getChild(0))
                while i < tree.getChildCount():
                    pvt = vt.var_list
                    vt.var_list = []
                    second_arg = vt.visit(tree.getChild(i + 1))
                    b1, f1 = TreeUtils.get_float(first_arg)
                    b2, f2 = TreeUtils.get_float(second_arg)
                    if b1 and not b2:
                        q = first_arg
                        first_arg = second_arg
                        second_arg = q
                        q = b1
                        b1 = b2
                        b2 = q
                        q = f1
                        f1 = f2
                        f2 = q
                        pvt = vt.var_list
                    if b2 and (first_arg in pvt or len(pvt) == 0):
                        concrete_values[first_arg] = f2
                    else:
                        values[first_arg] = second_arg
                    if str(type(
                            tree.getChild(i))) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>" and tree.getChild(
                            i).getText() == "==":
                        is_deleted = True
                        tree.children[i - 1].parentCtx = None
                        del tree.children[i - 1]
                        tree.children[i - 1].parentCtx = None
                        del tree.children[i - 1]
                    else:
                        i = i + 2
                        is_deleted = False
                    pvt = vt.var_list
                    first_arg = second_arg
                if is_deleted:
                    tree.children[i - 1].parentCtx = None
                    del tree.children[i - 1]
        return values, concrete_values

    @staticmethod
    def is_empty_node(node):
        ret = False
        t = type(node)
        if  t == ExpressionGrammarParser.AssignmentExpressionContext or \
            t == ExpressionGrammarParser.ArgumentExpressionListContext or \
            t == ExpressionGrammarParser.ExpressionContext or \
            t == ExpressionGrammarParser.EqualityExpressionContext or \
            t == ExpressionGrammarParser.EqualityExpressionContext or \
            t == ExpressionGrammarParser.LogicalAndExpressionContext or \
            t == ExpressionGrammarParser.LogicalOrExpressionContext or \
            t == ExpressionGrammarParser.PostfixExpressionContext or \
            t == ExpressionGrammarParser.PrimaryExpressionContext or \
            t == ExpressionGrammarParser.RelationalExpressionContext or \
            t == ExpressionGrammarParser.UnaryExpressionContext:
            if node.getChildCount() == 0:
                ret = True
            elif node.getChildCount() == 1:
                ret = TreeUtils.is_empty_node(node.getChild(0))
            elif node.getChildCount() == 2:
                t1 = type(node.getChild(0))
                t2 = type(node.getChild(1))
                if str(t1) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>" and \
                   str(t2) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>" and \
                   node.getChild(0).getText() == "(" and \
                   node.getChild(1).getText() == ")":
                    return True
            elif node.getChildCount() == 3:
                t1 = type(node.getChild(0))
                t2 = type(node.getChild(2))
                if str(t1) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>" and \
                   str(t2) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>" and \
                   node.getChild(0).getText() == "(" and \
                   node.getChild(2).getText() == ")":
                    ret = TreeUtils.is_empty_node(node.getChild(1))

        return ret

    @staticmethod
    def prepare_parser_expr(inp : str)->ExpressionGrammarParser :
        lexer = ExpressionGrammarLexer(InputStream(inp))
        error_listener = SymbolicExpressionGrammarErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        stream = CommonTokenStream(lexer)
        parser = ExpressionGrammarParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        return parser

    @staticmethod
    def get_vars_using_assignment(expr:str):
        if expr is None or expr == "":
            return dict(), dict(), ""
        res = ""
        tr = TreeUtils.prepare_parser_expr(expr).assignmentExpressionList()

        cval = dict()
        val = dict()
        is_continue = True
        while is_continue:
            is_continue = True
            n = TreeEdit.find_by_token(tr, "==")

            if n is None:
                is_continue = False
                continue
            to_del = n.parentCtx # Here _definitely_ a == b

            # Collect concrete variable values
            if str(type(
                    to_del)) == "<class 'ExpressionGrammar.ExpressionGrammarParser.ExpressionGrammarParser.EqualityExpressionContext'>":

                values, concrete_values = TreeUtils.extract_eq_values_def(to_del)
                val.update(values)
                cval.update(concrete_values)
                TreeEdit.delete_node(to_del)
                v = ExtSEGrammarVisitor()
                s = v.visit(tr)
                if s == "":
                    res = ""
                    break
                tr1 = TreeUtils.prepare_parser_expr(s).assignmentExpressionList()
                v1 = ExtSEGrammarVisitor()
                s1 = v1.visit(tr1)
                if s1 == "":
                    res = ""
                    break

                res = s1.replace("&", "&&").replace("|", "||")

                tr = TreeUtils.prepare_parser_expr(res).assignmentExpression()

        return cval, val, res

    @staticmethod
    def find_vars_by_name(node, args, kwargs):
        varlist = None
        for k, v in kwargs.items():
            if k == "varlist":
                varlist = v
                break
        if varlist is None:
            return False # Input parameter is absent, result is False
        # Found or not found mark should be returned here
        # inside postfixExpression:
        # primaryExpression (should be Identifier) "(" argumentsExpressionList? ")"
        return False

    @staticmethod
    def rm_all_vars(tree, varlist):

        if varlist is not None and tree is not None:
            n = TreeEdit.find_by_cond(tree, TreeUtils.find_var_by_name, varlist=varlist)
            while n is not None:
                node = n.parentCtx
                t =  type(node)
                while node is not None and hasattr(node, "parentCtx") and t != ExpressionGrammarParser.LogicalAndExpressionContext and t != ExpressionGrammarParser.LogicalOrExpressionContext:
                    node = node.parentCtx
                if hasattr(node, "children"):
                    is_deleted = False
                    # Checking children(s) for existing one of var and deleting ones those were found
        return tree

