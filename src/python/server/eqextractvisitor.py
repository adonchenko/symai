from behvisitor import BehGrammarVisitor
from treeutils import *
from antlr4.tree.Tree import TerminalNodeImpl

class EQExtractorVisitor( BehGrammarVisitor ):
    def __init__(self):
        self.cvals = dict()
        self.vals = dict()
        super().__init__()

    def getCVals(self):
        return self.cvals

    def setCVals(self, cvals):
        self.cvals = cvals

    def addCVal(self, nm, val):
        if nm not in self.cvals.keys():
            self.cvals[nm] = val
    def getVals(self):
        return self.vals

    def setVals(self, vals):
        self.vals = vals

    def addVal(self, nm, val):
        if nm not in self.vals.keys():
            self.vals[nm] = val

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
                is_na = False
                it = ctx.getChild(i)
                if type(it) == TerminalNodeImpl:
                    op = it.getText()
                i = i + 1
                it = ctx.getChild(i)
                r = self.visit(it)
                is_swp = False
                if op == '==':
                    b1, f1 = TreeUtils.get_float(l)
                    b2, f2 = TreeUtils.get_float(r)
                    if b1 and not b2:
                        is_swp = True
                        q = l
                        l = r
                        r = q
                        b1, f1 = TreeUtils.get_float(l)
                        b2, f2 = TreeUtils.get_float(r)
                    if b2 and not b1:
                        self.addCVal(l, r)
                        is_na = True
                    elif not b1 and not b2:
                        self.addVal(l, r)
                        is_na = True
                    if is_swp:
                        q = l
                        l = r
                        r = q
                        # TODO: Going to remove equality expression !!!
                if not is_na and i > 2:
                    res = res + "&&"
                if not is_na:
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
        return self.visitChildren(ctx)

    # Visit a parse tree produced by BehaviorsGrammarParser#expression.
    def visitExpression(self, ctx: BehaviorsGrammarParser.ExpressionContext):
        result = self.visit(ctx.assignmentExpression(0))
        i = 1
        while i < len(ctx.assignmentExpression()):
            result = result + "," + self.visit(ctx.assignmentExpression(i))
            i = i + 1
        return result

################################################################################################

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
                if i > 0:
                    self.addTerminal(s)
            else:
                s =  self.visit(it)

            res = res + s
            i = i + 1
            if i % 3 == 1:
                l = s
            if i % 3 == 0:
                self.addBehavior(l, s)
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
