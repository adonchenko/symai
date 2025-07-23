from symbolicexpressiongrammarvisitor import *

class ExtSEGrammarVisitor(SymbolicExpressionGrammarVisitor):

    def __init__(self):
        self.results = []
        self.behaviors = dict()
        self.terminals = []
        super().__init__()

    def getResults(self):
        return self.results

    def setResults(self, res):
        self.results = res

    def addResults(self, to_add):
        self.results.append(to_add)

    def getBehaviors(self):
        return self.behaviors

    def setBehaviors(self, beh):
        self.behaviors = beh

    def addBehavior(self, key, val):
        self.behaviors[key] = val

    def getTerminals(self):
        return self.terminals

    def setTerminals(self, terms):
        self.terminals = terms

    def addTerminal(self, term):
        self.terminals.append(term)

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

    # Visit a parse tree produced by ExpressionGrammarParser#actions.
    def visitActionsList(self, ctx:ExpressionGrammarParser.ActionsListContext):
        result = ""
        i = 0
        j = 0
        r = list()
        while i < len(ctx.postfixExpression()):
            t = [self.visit(ctx.postfixExpression(i))]
            if ctx.getChild(i * 4 + j * 2 + 1).getText() == ":" and ctx.getChild(i * 4 + j * 2 + 3).getText() == "->":
                t.append(self.visit(ctx.logicalOrExpression(j)))
                j = j + 1
            else:
                t.append(None)
            t.append(self.visit(ctx.assignmentExpression(i)))
            i = i + 1
            self.results.append(t)
            result = result + str(t[0]) + ":"
            if t[1] is not None:
                result = result + str(t[1]) + "->"
            result = result + str(t[2]) + ","
            r.append(t)
        self.setResults(r)

        return result

    # Visit a parse tree produced by ExpressionGrammarParser#behavior.
    def visitBehavior(self, ctx: ExpressionGrammarParser.BehaviorContext):
        res = str(self.visit(ctx.system_of_eqs()))
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#system_of_eqs.
    def visitSystem_of_eqs(self, ctx: ExpressionGrammarParser.System_of_eqsContext):
        res = ""
        i = 0
        r = []
        while i < len(ctx.eqs()):
            beh = str(self.visit(ctx.getChild(2 * i)))
            res = res + beh + ","
            i = i + 1
            j = beh.find("=")
            head = (beh[:j]).strip()
            tail = (beh[j+1:]).strip()
            r.append([head, tail])
        self.setResults(r)
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#eqs.
    def visitEqs(self, ctx: ExpressionGrammarParser.EqsContext):
        res = str(self.visit(ctx.prim_name()))
        left = res
        res = res + "="
        self.setTerminals([])
        right = str(self.visit(ctx.items_list()))
        term = self.getTerminals()
        self.addBehavior(left, term)
        res = res + right
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#prim_name.
    def visitPrim_name(self, ctx: ExpressionGrammarParser.Prim_nameContext):
        res = ""
        if ctx.Not() is not None:
            res = "!" + res
        if ctx.Identifier() is not None:
            res = res + str(ctx.Identifier().getText())
        if ctx.LeftParen() is not None:
            res = res + "("
        if ctx.argumentExpressionList() is not None:
            res = res + str(self.visit(ctx.argumentExpressionList()))
        if ctx.RightParen() is not None:
            res = res + ")"
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#comp_name.
    def visitComp_name(self, ctx: ExpressionGrammarParser.Comp_nameContext):
        if ctx.Constant() is None:
            res = self.visit(ctx.getChild(0))
        else:
            res = str(ctx.getChild(0).getText())
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#postfix_item.
    def visitPostfix_item(self, ctx: ExpressionGrammarParser.Postfix_itemContext):
        res = str(self.visit(ctx.comp_name()))
        lr = len(res)
        lp = 0
        i = 1
        idx = 0
        idl = 0
        cnt = res
        while i < ctx.getChildCount():
            s = str(ctx.getChild(i).getText())
            if s == ".":
                i = i + 1
                if len(cnt) > 0:
                    self.addTerminal(cnt)
                self.addTerminal(".")
                lp = lr + 1
                res = res + "." + ctx.Identifier(idx).getText()
                i = i + 1
                cnt = res[lr+1:len(res)]
                idx = idx + 1
                lr = len(res)
            elif s == "(":
                i = i + 1
                res = res + "("
                s = str(ctx.getChild(i).getText())
                if s != ")":
                    res = res + str(self.visit(ctx.argumentExpressionList(idl)))
                    idl = idl + 1
                    i = i + 1
                i = i + 1
                res = res + ")"
                lr = len(res)
                cnt = res[lp:lr]
                self.addTerminal(cnt)
                cnt = ""

        if i < 1:
            self.addTerminal(res)
        if len(cnt) > 0:
            self.addTerminal(cnt)
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#additive_item.
    def visitAdditive_item(self, ctx: ExpressionGrammarParser.Additive_itemContext):
        res = ""
        b = False
        for it in ctx.postfix_item():
            if b:
                res = res + "+"
                self.addTerminal("+")
            res = res + str(self.visit(it))
            b = True
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#items_list.
    def visitItems_list(self, ctx: ExpressionGrammarParser.Items_listContext):
        res = ""
        b = False
        for it in ctx.additive_item():
            if b:
                res = res + ";"
            res = res + str(self.visit(it))
            b = True
        return res

    # Visit a parse tree produced by ExpressionGrammarParser#par_item.
    def visitPar_item(self, ctx: ExpressionGrammarParser.Par_itemContext):
        res = ""
        b = False
        for it in ctx.items_list():
            if b:
                res = res + "||"
            res = res + str(self.visit(it))
            b = True
        return res