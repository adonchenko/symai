from BehaviorsGrammar.BehaviorsGrammarParser import BehaviorsGrammarParser
from exprvisitor import ExprGrammarVisitor

class ActGrammarVisitor( ExprGrammarVisitor ):

    def __init__(self):
        self.results = []
        super().__init__()

    def getResults(self):
        return self.results

    def setResults(self, res):
        self.results = res

    def addResults(self, to_add):
        self.results.append(to_add)

    # Visit a parse tree produced by BehaviorsGrammarParser#assignmentExpressionList
    def visitAssignmentExpressionList(self, ctx: BehaviorsGrammarParser.AssignmentExpressionListContext):
        result = self.visit(ctx.getChild(0))
        i = 0
        while i + 2 < ctx.getChildCount():
            i = i + 2
            result = result + ";" + self.visit(ctx.getChild(i))
        return result

    # Visit a parse tree produced by BehaviorsGrammarParser#actions.
    def visitActions(self, ctx: BehaviorsGrammarParser.ActionsContext):
        result = ""
        i = 0
        j = 0
        r = list()
        while i < len(ctx.postfixExpression()):
            t = [self.visit(ctx.postfixExpression(i))]
            if ctx.getChild(i * 4 + j * 2 + 1).getText() == ":" and ctx.getChild(i * 4 + j * 2 + 3).getText() == "->":
                st = self.visit(ctx.logicalOrExpression(j))
                if self.is_float_const(st):
                    if eval(st) == 1 or eval(st):
                        st = "0<1"
                t.append(st)
                j = j + 1
            else:
                t.append(None)
            self.action_has_logical(ctx.assignmentExpressionList(i))
            t.append(self.visitAssignmentExpressionList(ctx.assignmentExpressionList(i)))
            i = i + 1
            self.results.append(t)
            result = result + str(t[0]) + ":"
            if t[1] is not None:
                result = result + str(t[1]) + "->"
            result = result + str(t[2]) + ","
            r.append(t)
        i = 0
        while i < len(r):
            b = False
            s = r[i][0]
            j = 0
            while not b and j < i - 1:
                b = (s == r[j][0])
                j = j + 1
            if b:
                msg = f"Actions. Syntax error. Duplicate action name `{s}`"
                raise Exception(msg)
            i = i + 1
        self.setResults(r)

        return result

    """
    Returns True if particular actions list has a logical expression at the end. 
    Otherwise returns False
    Raises an exception in case of syntax error
    Note: may raise an Exception if logical expression appears more than one time in the list             
    """
    def action_has_logical(self, ctx:BehaviorsGrammarParser.AssignmentExpressionListContext)->bool:
        j = len(ctx.assignmentExpression())
        i = 0
        b = False
        vr = []
        v = self.var_list.copy()
        while i  < j:
            s = str(type(ctx.assignmentExpression(i).getChild(0)))
            if type(ctx.assignmentExpression(i).getChild(0)) == BehaviorsGrammarParser.LogicalOrExpressionContext:
                if b:
                    raise Exception("Syntax error. Postcondition. Logical expression in action appeared two or more times")
                b = True
                if i > j - 1:
                    raise Exception("Syntax error. Postcondition. Logical expression is not a last item")
                self.var_list = []
                for s in vr:
                    if s in self.var_list:
                        raise Exception("Syntax error. Variable '" + s + "' cannot appear both in left side of assignment and in the logical post expression")
                self.var_list = v
            else:
                s = self.visit(ctx.assignmentExpression(i).getChild(0))
                if s in vr:
                    raise Exception("Syntax error. Duplicate name '" + s + "'}")
                vr.append(s)
            i = i + 1
            self.var_list = v

        return b
