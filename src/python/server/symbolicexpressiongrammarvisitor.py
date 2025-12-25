from antlr4.tree.Tree import TerminalNodeImpl

from BehaviorsGrammar.BehaviorsGrammarVisitor import BehaviorsGrammarVisitor
from BehaviorsGrammar.BehaviorsGrammarParser import BehaviorsGrammarParser

from mathutils import *

class SymbolicExpressionGrammarVisitor(BehaviorsGrammarVisitor):

    def __init__(self):
        self.arg_list_start = "("
        self.arg_list_cnt = ","
        self.arg_list_fin = ")"
        self.substitution = dict()
        self.var_list = []
        self.hasTrigonometric = False
        self.hasNonLinear = False
        self.replEQ = False
        super().__init__()

    def is_float_const(self, vl : str):
        ret = True
        if vl != "True" and vl != "1" and vl != "False":
            try:
                float(vl)
            except ValueError:
                ret = False

        return ret

    def isEQ(self):
        if self.replEQ is None:
            self.replEQ = False

        return self.replEQ

    def setIsEq(self, val):
        self.replEQ = val

    def isNonLinear(self):
        return self.hasNonLinear or self.hasTrigonometric

    def isTrigonometric(self):
        return self.hasTrigonometric

    def setSubstitution(self, subs):
        self.substitution = subs

    def getSubstitution(self) :
        return self.substitution

    def getVarList(self):
        return self.var_list

    # Visit a parse tree produced by BehaviorsGrammarParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:BehaviorsGrammarParser.PrimaryExpressionContext):
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
    def visitPostfixExpression(self, ctx:BehaviorsGrammarParser.PostfixExpressionContext):
        trig_funct=["sin", "cos", "tan", "cotan","asin", "acos", "atan", "acotan"]
        nl_funct=["log", "lg", "sqrt", "exp", "pow"]
        tmp_arg_list_start = self.arg_list_start
        tmp_arg_list_cnt = self.arg_list_cnt
        tmp_arg_list_fin = self.arg_list_fin
        self.arg_list_start = "("
        self.arg_list_cnt = ","
        self.arg_list_fin = ")"

        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        if result is None:
            return ""
        func_found = False
        if result.lower().strip() in trig_funct and len(ctx.children) > 1:
            if ctx.getChild(1).getText() == '(':
                self.hasTrigonometric = True
                result = result.lower().strip()
                func_found = True
        elif result.lower().strip() in nl_funct and len(ctx.children) > 1:
            if ctx.getChild(1).getText() == '(':
                self.hasNonLinear = True
                result = result.lower().strip()
                func_found = True
        # CVC5: Here should be if And, Or Xor or Not eq
        # Z3: and or xor not eq
        # sympy: and or not eq ne
        elif  result.lower().strip() == "or" and len(ctx.children) > 1 and  ctx.getChild(1).getText() == '(':
            self.arg_list_start = ""
            self.arg_list_cnt = " | "
            self.arg_list_fin = ""
            result = ""
        elif result.lower().strip() == "and" and ctx.getChild(1).getText() == '(':
            self.arg_list_start = ""
            self.arg_list_cnt = " & "
            self.arg_list_fin = ""
            result = ""
        elif result.lower().strip() == "eq" and ctx.getChild(1).getText() == '(':
            self.arg_list_start = ""
            self.arg_list_cnt = " == "
            self.arg_list_fin = ""
            result = ""
        elif result.lower().strip() == "ne" and ctx.getChild(1).getText() == '(':
            self.arg_list_start = ""
            self.arg_list_cnt = " != "
            self.arg_list_fin = ""
            result = ""
        elif result.lower().strip() == "not" and len(ctx.children) > 1 and ctx.getChild(1).getText() == '(':
            self.arg_list_start = "!("
            self.arg_list_cnt = ") & !("
            self.arg_list_fin = ")"
            result = ""
        elif ctx.getChildCount() > 1:
            self.arg_list_start = "("
            self.arg_list_cnt = ","
            self.arg_list_fin = ")"

        i = 1
        while i < ctx.getChildCount():
            t = type(ctx.getChild(i))
            s = ctx.getChild(i)
            if s is None:
                return ""
            if t == TerminalNodeImpl:
                s = s.getText()
                if s == ".":
                    i = i + 1
                    s = ctx.getChild(i).getText()
                    result = result + "." + s
                elif s == "(":
                    result = result + self.arg_list_start
                    i = i + 1
                    t = type(ctx.getChild(i))
                    if t == TerminalNodeImpl and s == ")":
                        result = result + self.arg_list_fin
                    else:
                        s = self.visit(ctx.getChild(i))
                        if s is None:
                            result = ""
                        else:
                            result = result + s + self.arg_list_fin
                        i = i + 1
            i = i + 1
        # var_list has to be updated
        if result not in self.var_list and len(result) > 0:
            if not self.is_float_const(result):
                    self.var_list.append(result)
        if self.substitution is not None and len(result) > 0:
            i = 0
            while i < len(self.substitution):
                x = str(self.substitution[i]["name"])
                y = str(self.substitution[i]["value"])
                i = i + 1
                if result.strip() == x:
                    result = y
                    i = len(self.substitution)

        self.arg_list_cnt = tmp_arg_list_cnt
        self.arg_list_start = tmp_arg_list_start
        self.arg_list_fin = tmp_arg_list_fin
        if func_found:
            try:
                gvars = MathUtils.fill_gvars_func()
                lvars = dict()
                s = str(eval(result, gvars, lvars))
            except:
                s = result
            result = s
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#argumentExpressionList.
    def visitArgumentExpressionList(self, ctx:BehaviorsGrammarParser.ArgumentExpressionListContext):
        i = 0
        result = self.visit(ctx.assignmentExpression(i))
        i = i + 1
        while i < len(ctx.assignmentExpression()):
            s = self.visit(ctx.assignmentExpression(i))
            if len(result) > 0 and len(s) > 0:
                result = result + self.arg_list_cnt + self.visit(ctx.assignmentExpression(i))
            elif len(s) > 0:
                result = s
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#unaryExpression.
    def visitUnaryExpression(self, ctx:BehaviorsGrammarParser.UnaryExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.postfixExpression()).strip()

        if ctx.unaryOperator() is not None:
            op = ctx.unaryOperator().getText()
            if op == '!':
                result = " Not(" + result + ")"
            else:
                result = op + result
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#unaryOperator.
    def visitUnaryOperator(self, ctx:BehaviorsGrammarParser.UnaryOperatorContext):
        result = ctx.getChild(0).getText()
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:BehaviorsGrammarParser.MultiplicativeExpressionContext):
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
    def visitAdditiveExpression(self, ctx:BehaviorsGrammarParser.AdditiveExpressionContext):
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
    def visitRelationalExpression(self, ctx:BehaviorsGrammarParser.RelationalExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        i = 0
        result = self.visit(ctx.getChild(0))
        first = ""
        while i + 1 < len(ctx.additiveExpression()):
            if i > 0:
                result = "And(" + result + ", (" + first
            second = self.visit(ctx.additiveExpression(i + 1))
            result = result + ctx.getChild(2*i + 1).getText() + second
            if i > 0:
                result = result + "))"
            first = second
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#equalityExpression.
    def visitEqualityExpression(self, ctx:BehaviorsGrammarParser.EqualityExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        i = 0
        result = self.visit(ctx.getChild(0))
        if result is None or (len(result) == 1 and result not in self.var_list and not self.is_float_const(result)):
            return ""
        i = i + 1
        if ctx.getChildCount() < i + 1:
            return result
        while ctx.getChild(2 * (i - 1) + 1) is not None:
            if i > 1 and len(result) > 0:
                result = "(" + result + ")"
            op = ctx.getChild(2 * (i - 1) + 1).getText()
            pref = ""
            postf = ""
            if op == "!=":
                pref = "Not("
                postf = ")"
            if len(result) > 0:
                if self.isEQ():
                    result = pref + "Eq(" + result + "," + self.visit(ctx.relationalExpression(i) ) + ")" + postf
                else:
                    result = pref + result + "==" + self.visit(ctx.relationalExpression(i))  + postf
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:BehaviorsGrammarParser.LogicalAndExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        i = 1
        while i < len(ctx.equalityExpression()):
            if result is not None and len(result) > 0:
                app = self.visit(ctx.equalityExpression(i))
                if app is not None and len(app) > 0:
                    result = "And(" + result + "," + app + ")"
            else:
                result = self.visit(ctx.equalityExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:BehaviorsGrammarParser.LogicalOrExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        result = self.visit(ctx.getChild(0))
        i = 1
        while i < len(ctx.logicalAndExpression()):
            if result is not None and len(result) > 0:
                app = self.visit(ctx.logicalAndExpression(i))
                if app is not None and len(app) > 0:
                    result = "Or(" + result + "," + app + ")"
            else:
                result = self.visit(ctx.logicalAndExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:BehaviorsGrammarParser.AssignmentExpressionContext):
        if ctx.getChildCount() < 1:
            return ""
        if ctx.logicalOrExpression() is not None:
            result = self.visit(ctx.logicalOrExpression())
        else:
            result = self.visit(ctx.unaryExpression()) + "=" + self.visit(ctx.assignmentExpression())
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:BehaviorsGrammarParser.AssignmentOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by BehaviorsGrammarParser#expression.
    def visitExpression(self, ctx:BehaviorsGrammarParser.ExpressionContext):
        result = self.visit(ctx.assignmentExpression(0))
        i = 1
        while i < len(ctx.assignmentExpression()):
            result = result + "," + self.visit(ctx.assignmentExpression(i))
            i = i + 1
        return result
