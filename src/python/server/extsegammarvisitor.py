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