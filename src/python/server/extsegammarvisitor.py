from symbolicexpressiongrammarvisitor import *

class ExtSEGrammarVisitor(SymbolicExpressionGrammarVisitor):

    def __init__(self):
        self.results = []
        super().__init__()

    def getResults(self):
        return self.results

    def setResults(self, res):
        self.results = res

    # Visit a parse tree produced by ExpressionGrammarParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:ExpressionGrammarParser.PrimaryExpressionContext):
        if ctx.LeftParen() is not None:
            result = "(" + self.visit(ctx.expression()) + ")"
        else:
            if ctx.Identifier() is not None:
                result = ctx.Identifier().getText()
            else:
                result = ctx.Constant().getText()
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#postfixExpression.
    def visitPostfixExpression(self, ctx:ExpressionGrammarParser.PostfixExpressionContext):
        trig_funct=["sin", "cos", "tan", "catan","asin", "acos", "atan", "acatan"]
        nl_funct=["log", "ln", "sqrt", "exp, diff"]
        tmp_arg_list_start = self.arg_list_start
        tmp_arg_list_cnt = self.arg_list_cnt
        tmp_arg_list_fin = self.arg_list_fin
        self.arg_list_start = "("
        self.arg_list_cnt = ","
        self.arg_list_fin = ")"

        result = self.visit(ctx.primaryExpression())
        if result.lower().strip() in trig_funct and len(ctx.children) > 1:
            if ctx.getChild(1).getText() == '(':
                self.hasTrigonometric = True
        elif result.lower().strip() in nl_funct and len(ctx.children) > 1:
            if ctx.getChild(1).getText() == '(':
                self.hasNonLinear = True
        # CVC5: Here should be if And, Or Xor or Not
        # Z3: and or xor not
        # sympy: and or not
        elif  result.lower().strip() == "or" and  ctx.getChild(1).getText() == '(':
            self.arg_list_start = "("
            self.arg_list_cnt = ") || ("
            self.arg_list_fin = ")"
            result = ""
        elif result.lower().strip() == "and" and ctx.getChild(1).getText() == '(':
            self.arg_list_start = "("
            self.arg_list_cnt = ") && ("
            self.arg_list_fin = ")"
            result = ""
        elif result.lower().strip() == "not" and ctx.getChild(1).getText() == '(':
            self.arg_list_start = "! ("
            self.arg_list_cnt = ") & ! ("
            self.arg_list_fin = ")"
            result = ""

        i = 1
        j = 0
        while i < len(ctx.children):
            if len(ctx.children) > i + 1:
                if ctx.getChild(i).getText() == '.':
                    result = result + '.'
                    i = i + 1
                    result = result + ctx.getChild(i).getText()
                else:
                    if ctx.getChild(i).getText() == '(':
                        result = result + self.arg_list_start + self.visit(ctx.argumentExpressionList(j)) + self.arg_list_fin
                        j = j + 1
                        i = i + 1
            i = i + 1
        self.arg_list_cnt = tmp_arg_list_cnt
        self.arg_list_start = tmp_arg_list_start
        self.arg_list_fin = tmp_arg_list_fin
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#argumentExpressionList.
    def visitArgumentExpressionList(self, ctx:ExpressionGrammarParser.ArgumentExpressionListContext):
        i = 0
        result = self.visit(ctx.assignmentExpression(i))
        i = i + 1
        while i < len(ctx.assignmentExpression()):
            result = result + self.arg_list_cnt + self.visit(ctx.assignmentExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#unaryExpression.
    def visitUnaryExpression(self, ctx:ExpressionGrammarParser.UnaryExpressionContext):
        result = self.visit(ctx.postfixExpression()).strip()
        # Variables and substitutions. Should be processed in unaryExpression
        if not (result[0:1].isdigit()) and result.find("(") < 0 and result.find("_d_o_t_") < 0:
            if result.strip() not in self.var_list and result.lower() != "true" and result.lower() != "false":
                self.var_list.append(result.strip())
            if self.substitution is not None:
                i = 0
                while i < len(self.substitution):
                    x = str(self.substitution[i]["name"])
                    y = str(self.substitution[i]["value"])
                    i = i + 1
                    if result.strip() == x:
                        result = y
                        i = len(self.substitution)

        if ctx.unaryOperator() is not None:
            op = ctx.unaryOperator().getText()
            if op == '!':
                result = " ! (" + result + ")"
            else:
                result = op + result
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#unaryOperator.
    def visitUnaryOperator(self, ctx:ExpressionGrammarParser.UnaryOperatorContext):
        result = ctx.getChild(0).getText()
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:ExpressionGrammarParser.MultiplicativeExpressionContext):
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

    # Visit a parse tree produced by ExpressionGrammarParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:ExpressionGrammarParser.AdditiveExpressionContext):
        i = 0
        result = self.visit(ctx.multiplicativeExpression(i))
        i = i + 1
        while ctx.getChild(2 * (i - 1) + 1) is not None:
            op = ctx.getChild(2 * (i - 1) + 1).getText()
            result = result + op
            result = result + self.visit(ctx.multiplicativeExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#relationalExpression.
    def visitRelationalExpression(self, ctx:ExpressionGrammarParser.RelationalExpressionContext):
        i = 0
        result = self.visit(ctx.additiveExpression(i))
        first = ""
        while i + 1 < len(ctx.additiveExpression()):
            if i > 0:
                result = "(" + result + ") && (" + first
            second = self.visit(ctx.additiveExpression(i + 1))
            result = result + ctx.getChild(2*i + 1).getText() + second
            if i > 0:
                result = result + ")"
            first = second
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#equalityExpression.
    def visitEqualityExpression(self, ctx:ExpressionGrammarParser.EqualityExpressionContext):
        i = 0
        result = self.visit(ctx.relationalExpression(i))
        i = i + 1
        while ctx.getChild(2 * (i - 1) + 1) is not None:
            if i > 1:
                result = "(" + result + ")"
            op = ctx.getChild(2 * (i - 1) + 1).getText()
            if op == "!=":
                result = "! ((" + result + ") == (" + self.visit(ctx.relationalExpression(i)) + "))"
            else:
                result = "(" + result + ")" + op + self.visit(ctx.relationalExpression(i))
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:ExpressionGrammarParser.LogicalAndExpressionContext):
        result = self.visit(ctx.equalityExpression(0))
        i = 1
        while i < len(ctx.equalityExpression()):
            if i == 1:
                result = "(" + result + ")"
            result = result + " && (" + self.visit(ctx.equalityExpression(i)) + ")"
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:ExpressionGrammarParser.LogicalOrExpressionContext):
        result = self.visit(ctx.logicalAndExpression(0))
        i = 1
        while i < len(ctx.logicalAndExpression()):
            if i == 1:
                result = "(" + result + ")"
            result = result + " || (" + self.visit(ctx.logicalAndExpression(i)) + ")"
            i = i + 1
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:ExpressionGrammarParser.AssignmentExpressionContext):
        if ctx.logicalOrExpression() is not None:
            result = self.visit(ctx.logicalOrExpression())
        else:
            result = self.visit(ctx.unaryExpression()) + "=" + self.visit(ctx.assignmentExpression())
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:ExpressionGrammarParser.AssignmentOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ExpressionGrammarParser#expression.
    def visitExpression(self, ctx:ExpressionGrammarParser.ExpressionContext):
        result = self.visit(ctx.assignmentExpression(0))
        i = 1
        while i < len(ctx.assignmentExpression()):
            result = result + "," + self.visit(ctx.assignmentExpression(i))
            i = i + 1
        return result

 # Visit a parse tree produced by ExpressionGrammarParser#expressionList.
    def visitExpressionList(self, ctx:ExpressionGrammarParser.ExpressionListContext):
        result = self.visit(ctx.assignmentExpression(0))
        self.results.append(result)
        i = 1
        while i < len(ctx.assignmentExpression()):
            beh = self.visit(ctx.assignmentExpression(i))
            self.results.append(beh)
            result = result + "," + beh
            i = i + 1
        result = result + ","
        return result

    # Visit a parse tree produced by ExpressionGrammarParser#actions.
    def visitActions(self, ctx:ExpressionGrammarParser.ActionsContext):
        result = []
        i = 0
        j = 0
        while i < len(ctx.postfixExpression()):
            t = []
            t.append(self.visit(ctx.postfixExpression(i)))
            if ctx.getChild(i * 4 + j * 2 + 1).getText() == ":" and ctx.getChild(i * 4 + j * 2 + 3).getText() == "->":
                t.append(self.visit(ctx.logicalOrExpression(j)))
                j = j + 1
            else:
                t.append(None)
            t.append(self.visit(ctx.assignmentExpression(i)))
            i = i + 1
            result.append(t)

        return result
