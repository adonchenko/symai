from BehaviorsGrammar.BehaviorsGrammarVisitor import BehaviorsGrammarVisitor
from BehaviorsGrammar.BehaviorsGrammarParser import BehaviorsGrammarParser
from treeutils import TreeUtils
from antlr4.tree.Tree import TerminalNodeImpl
from mathutils import MathUtils

class ExprGrammarVisitor( BehaviorsGrammarVisitor ):
    def __init__(self):
        self.substitution = dict()
        self.var_list = []
        self.hasTrigonometric = False
        self.hasNonLinear = False
        super().__init__()

    def is_float_const(self, vl: str):
        ret = True
        if vl != "True" and vl != "1" and vl != "False":
            try:
                float(vl)
            except ValueError:
                ret = False
        return ret

    def isNonLinear(self):
        return self.hasNonLinear or self.hasTrigonometric

    def isTrigonometric(self):
        return self.hasTrigonometric

    def setSubstitution(self, subs):
        self.substitution = subs

    def getSubstitution(self):
        return self.substitution

    def getVarList(self):
        return self.var_list

    # Visit a parse tree produced by BehaviorsGrammarParser#primaryExpression.
    def visitPrimaryExpression(self, ctx: BehaviorsGrammarParser.PrimaryExpressionContext):
        if ctx.LeftParen() is not None:
            result = self.visit(ctx.expression())
            if result is not None and len(result) > 0:
                result = "(" + result + ")"
        else:
            if ctx.Identifier() is not None:
                result = ctx.Identifier().getText()
            else:
                result = ctx.Constant().getText()
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#postfixExpression.
    def visitPostfixExpression(self, ctx: BehaviorsGrammarParser.PostfixExpressionContext):
        trig_funct = ["sin", "cos", "tan", "cotan", "asin", "acos", "atan", "acotan"]
        nl_funct = ["log", "lg", "sqrt", "exp", "pow"]

        res = ''
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
            else:
                s = self.visit(it)
            i = i + 1
            res = res + s
        func_found = False
        i = res.find("(")
        if i != -1:
            fnm = res[:i].lower().strip()
            if len(fnm) > 0:
                if fnm in trig_funct:
                    res = res.replace(res[:i], fnm, 1)
                    self.hasTrigonometric = True
                    func_found = True
                elif fnm in nl_funct:
                    res = res.replace(res[:i], fnm, 1)
                    self.hasNonLinear = True
                    func_found = True
        # var_list has to be updated
        t, v = TreeUtils.get_float(res)
        if res not in self.var_list and len(res) > 0 and not func_found and not t:
            self.var_list.append(res)
        if self.substitution is not None and len(res) > 0:
            i = 0
            while i < len(self.substitution):
                x = str(self.substitution[i]["name"])
                y = str(self.substitution[i]["value"])
                i = i + 1
                if res.strip() == x:
                    res = y
                    i = len(self.substitution)

        if func_found:
            try:
                gvars = MathUtils.fill_gvars_func()
                lvars = dict()
                s = str(eval(res, gvars, lvars))
            except:
                s = res
            res = s
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#argumentExpressionList.
    def visitArgumentExpressionList(self, ctx: BehaviorsGrammarParser.ArgumentExpressionListContext):
        i = 0
        result = self.visit(ctx.assignmentExpression(i))
        i = i + 1
        while i < len(ctx.assignmentExpression()):
            s = self.visit(ctx.assignmentExpression(i))
            if len(result) > 0 and len(s) > 0:
                result = result + "," + self.visit(ctx.assignmentExpression(i))
            elif len(s) > 0:
                result = s
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#unaryExpression.
    def visitUnaryExpression(self, ctx: BehaviorsGrammarParser.UnaryExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = ""
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
            else:
                s = self.visit(it)
            result = result + s
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#unaryOperator.
    def visitUnaryOperator(self, ctx: BehaviorsGrammarParser.UnaryOperatorContext):
        result = ctx.getChild(0).getText()
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx: BehaviorsGrammarParser.MultiplicativeExpressionContext):
        i = 0
        result = self.visit(ctx.unaryExpression(i))
        i = i + 1
        while ctx.getChild(2 * (i - 1) + 1) is not None:
            op = ctx.getChild(2 * (i - 1) + 1).getText()
            if op == "**":
                self.hasNonLinear = True
            result = result + op
            result = result + self.visit(ctx.unaryExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#additiveExpression.
    def visitAdditiveExpression(self, ctx: BehaviorsGrammarParser.AdditiveExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        i = 1
        while ctx.getChild(2 * (i - 1) + 1) is not None:
            op = ctx.getChild(2 * (i - 1) + 1).getText()
            result = result + op
            result = result + self.visit(ctx.multiplicativeExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#relationalExpression.
    def visitRelationalExpression(self, ctx: BehaviorsGrammarParser.RelationalExpressionContext):
        res = ''
        i = 0
        if i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
            else:
                s = self.visit(it)
            l = s
            i = i + 1
            if i + 1 >= ctx.getChildCount():
                res = s
            op = ''
            while i + 1 < ctx.getChildCount():
                it = ctx.getChild(i)
                if type(it) == TerminalNodeImpl:
                    op = it.getText()
                i = i + 1
                it = ctx.getChild(i)
                r = self.visit(it)
                if len(res) > 0:
                    res = res + "&&"
                res = res + l + op + r
                l = r
                i = i + 1
            #TODO: what if we have a <=b != c ?
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#equalityExpression.
    def visitEqualityExpression(self, ctx: BehaviorsGrammarParser.EqualityExpressionContext):
        res = ''
        i = 0
        if i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
            else:
                s = self.visit(it)
            l = s
            i = i + 1
            if i + 1 >= ctx.getChildCount():
                res = s
            op = ''
            while i + 1 < ctx.getChildCount():
                it = ctx.getChild(i)
                if type(it) == TerminalNodeImpl:
                    op = it.getText()
                i = i + 1
                it = ctx.getChild(i)
                r = self.visit(it)
                if i > 2:
                    res = res + "&&"
                res = res + l + op + r
                l = r
                i = i + 1
            #TODO: what if we have a <=b != c ?

        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx: BehaviorsGrammarParser.LogicalAndExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        i = 1
        while i < len(ctx.equalityExpression()):
            if result is not None and len(result) > 0:
                app = self.visit(ctx.equalityExpression(i))
                if app is not None and app != '':
                    if len(result) > 0:
                        result = result + "&&"
                    result = result + app
            else:
                result = self.visit(ctx.equalityExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx: BehaviorsGrammarParser.LogicalOrExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        i = 1
        while i < len(ctx.logicalAndExpression()):
            if result is not None and len(result) > 0:
                app = self.visit(ctx.logicalAndExpression(i))
                if app is not None and app != '':
                    if len(result) > 0:
                        result = result + "||"
                    result = result + app
            else:
                result = self.visit(ctx.logicalAndExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx: BehaviorsGrammarParser.AssignmentExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        if ctx.logicalOrExpression() is not None:
            result = self.visit(ctx.logicalOrExpression())
        else:
            result = self.visit(ctx.unaryExpression()) + "=" + self.visit(ctx.assignmentExpression())
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx: BehaviorsGrammarParser.AssignmentOperatorContext):
        return ctx.getChild(0).getText()

    # Visit a parse tree produced by BehaviorsGrammarParser#expression.
    def visitExpression(self, ctx: BehaviorsGrammarParser.ExpressionContext):
        result = self.visit(ctx.assignmentExpression(0))
        i = 1
        while i < len(ctx.assignmentExpression()):
            result = result + "," + self.visit(ctx.assignmentExpression(i))
            i = i + 1
        return result
