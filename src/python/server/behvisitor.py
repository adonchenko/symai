from BehaviorsGrammar.BehaviorsGrammarParser import BehaviorsGrammarParser
from exprvisitor import ExprGrammarVisitor
from antlr4.tree.Tree import TerminalNodeImpl

class BehGrammarVisitor( ExprGrammarVisitor ):
    def __init__(self):
        self.behaviors = dict()
        self.terminals = []
        super().__init__()

    def getBehaviors(self):
        return self.behaviors.copy()

    def setBehaviors(self, beh):
        if beh is not None:
            self.behaviors = beh.copy()
        else:
            self.behaviors = dict()

    def addBehavior(self, key, val):
        self.behaviors[key] = val

    def getTerminals(self):
        return self.terminals.copy()

    def setTerminals(self, terms):
        self.terminals = terms

    def addTerminal(self, term):
        self.terminals.append(term)

    # Visit a parse tree produced by BehaviorsGrammarParser#behaviors.
    def visitBehaviors(self, ctx:BehaviorsGrammarParser.BehaviorsContext):
        res = str(self.visit(ctx.system_of_eqs()))
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#system_of_eqs.
    def visitSystem_of_eqs(self, ctx:BehaviorsGrammarParser.System_of_eqsContext):
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
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#eqs.
    def visitEqs(self, ctx:BehaviorsGrammarParser.EqsContext):
        res = ''
        i = 0
        l = ''
        while i < ctx.getChildCount():
            if i % 3== 1:
                self.setTerminals([])
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s  = it.getText()
                if i > 1:
                    self.addTerminal(s)
            else:
                s =  self.visit(it)

            res = res + s
            i = i + 1
            if i % 3 == 1:
                l = s
            if i % 3 == 0:
                self.addBehavior(l, self.getTerminals())
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#prim_name.
    def visitPrim_name(self, ctx:BehaviorsGrammarParser.Prim_nameContext):
        res = ""
        i = 0
        s = ""
        if type(ctx.getChild(i)) == TerminalNodeImpl and ctx.getChild(i).getText() == '!':
            self.addTerminal('!')
            res = res + '!'
            i = i + 1
        while ctx.getChildCount() > i:
            if type(ctx.getChild(i)) == TerminalNodeImpl:
                s = s + ctx.getChild(i).getText()
            else:
                s = s + self.visit(ctx.getChild(i))
            i = i + 1
        self.addTerminal(s)
        res = res + s
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#comp_name.
    def visitComp_name(self, ctx:BehaviorsGrammarParser.Comp_nameContext):
        res = ''
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
                self.addTerminal(s)
            else:
                s = self.visit(it)
            res = res + s
            i = i + 1

        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#postfix_item.
    def visitPostfix_item(self, ctx:BehaviorsGrammarParser.Postfix_itemContext):
        res = ''
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s = it.getText()
                self.addTerminal(s)
            else:
                s = self.visit(it)
            res = res + s
            i = i + 1
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#items_list.
    def visitItems_list(self, ctx:BehaviorsGrammarParser.Items_listContext):
        res = ''
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s  = it.getText()
                self.addTerminal(s)
            else:
                s =  self.visit(it)
            res = res + s
            i = i + 1
        return res

    # Visit a parse tree produced by BehaviorsGrammarParser#par_item.
    def visitPar_item(self, ctx:BehaviorsGrammarParser.Par_itemContext):
        res = ''
        i = 0
        while i < ctx.getChildCount():
            it = ctx.getChild(i)
            if type(it) == TerminalNodeImpl:
                s  = it.getText()
                self.addTerminal(s)
            else:
                s =  self.visit(it)
            res = res + s
            i = i + 1
        return res
