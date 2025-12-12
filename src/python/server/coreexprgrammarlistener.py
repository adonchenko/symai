from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser
from ExpressionGrammar.ExpressionGrammarListener import ExpressionGrammarListener

class CoreExpressionGrammarListener(ExpressionGrammarListener):

    def __init__(self):
        self.cvals = dict()
        self.vals = dict()
        self.rval = ""
        self.lval = ""

        super().__init__()

    # Enter a parse tree produced by ExpressionGrammarParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:ExpressionGrammarParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:ExpressionGrammarParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#postfixExpression.
    def enterPostfixExpression(self, ctx:ExpressionGrammarParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#postfixExpression.
    def exitPostfixExpression(self, ctx:ExpressionGrammarParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#argumentExpressionList.
    def enterArgumentExpressionList(self, ctx:ExpressionGrammarParser.ArgumentExpressionListContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#argumentExpressionList.
    def exitArgumentExpressionList(self, ctx:ExpressionGrammarParser.ArgumentExpressionListContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#unaryExpression.
    def enterUnaryExpression(self, ctx:ExpressionGrammarParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#unaryExpression.
    def exitUnaryExpression(self, ctx:ExpressionGrammarParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#unaryOperator.
    def enterUnaryOperator(self, ctx:ExpressionGrammarParser.UnaryOperatorContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#unaryOperator.
    def exitUnaryOperator(self, ctx:ExpressionGrammarParser.UnaryOperatorContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:ExpressionGrammarParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:ExpressionGrammarParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:ExpressionGrammarParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:ExpressionGrammarParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#relationalExpression.
    def enterRelationalExpression(self, ctx:ExpressionGrammarParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#relationalExpression.
    def exitRelationalExpression(self, ctx:ExpressionGrammarParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#equalityExpression.
    def enterEqualityExpression(self, ctx:ExpressionGrammarParser.EqualityExpressionContext):
        self.lval = ""
        self.rval = ""
        print("Start")

    # Exit a parse tree produced by ExpressionGrammarParser#equalityExpression.
    def exitEqualityExpression(self, ctx:ExpressionGrammarParser.EqualityExpressionContext):
        print("Exit")


    # Enter a parse tree produced by ExpressionGrammarParser#logicalAndExpression.
    def enterLogicalAndExpression(self, ctx:ExpressionGrammarParser.LogicalAndExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#logicalAndExpression.
    def exitLogicalAndExpression(self, ctx:ExpressionGrammarParser.LogicalAndExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#logicalOrExpression.
    def enterLogicalOrExpression(self, ctx:ExpressionGrammarParser.LogicalOrExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#logicalOrExpression.
    def exitLogicalOrExpression(self, ctx:ExpressionGrammarParser.LogicalOrExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#assignmentExpression.
    def enterAssignmentExpression(self, ctx:ExpressionGrammarParser.AssignmentExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#assignmentExpression.
    def exitAssignmentExpression(self, ctx:ExpressionGrammarParser.AssignmentExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#assignmentOperator.
    def enterAssignmentOperator(self, ctx:ExpressionGrammarParser.AssignmentOperatorContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#assignmentOperator.
    def exitAssignmentOperator(self, ctx:ExpressionGrammarParser.AssignmentOperatorContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#expression.
    def enterExpression(self, ctx:ExpressionGrammarParser.ExpressionContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#expression.
    def exitExpression(self, ctx:ExpressionGrammarParser.ExpressionContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#assignmentExpressionList.
    def enterAssignmentExpressionList(self, ctx:ExpressionGrammarParser.AssignmentExpressionListContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#assignmentExpressionList.
    def exitAssignmentExpressionList(self, ctx:ExpressionGrammarParser.AssignmentExpressionListContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#actionsList.
    def enterActionsList(self, ctx:ExpressionGrammarParser.ActionsListContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#actionsList.
    def exitActionsList(self, ctx:ExpressionGrammarParser.ActionsListContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#behavior.
    def enterBehavior(self, ctx:ExpressionGrammarParser.BehaviorContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#behavior.
    def exitBehavior(self, ctx:ExpressionGrammarParser.BehaviorContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#system_of_eqs.
    def enterSystem_of_eqs(self, ctx:ExpressionGrammarParser.System_of_eqsContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#system_of_eqs.
    def exitSystem_of_eqs(self, ctx:ExpressionGrammarParser.System_of_eqsContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#eqs.
    def enterEqs(self, ctx:ExpressionGrammarParser.EqsContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#eqs.
    def exitEqs(self, ctx:ExpressionGrammarParser.EqsContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#prim_name.
    def enterPrim_name(self, ctx:ExpressionGrammarParser.Prim_nameContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#prim_name.
    def exitPrim_name(self, ctx:ExpressionGrammarParser.Prim_nameContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#comp_name.
    def enterComp_name(self, ctx:ExpressionGrammarParser.Comp_nameContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#comp_name.
    def exitComp_name(self, ctx:ExpressionGrammarParser.Comp_nameContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#postfix_item.
    def enterPostfix_item(self, ctx:ExpressionGrammarParser.Postfix_itemContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#postfix_item.
    def exitPostfix_item(self, ctx:ExpressionGrammarParser.Postfix_itemContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#additive_item.
    def enterAdditive_item(self, ctx:ExpressionGrammarParser.Additive_itemContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#additive_item.
    def exitAdditive_item(self, ctx:ExpressionGrammarParser.Additive_itemContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#items_list.
    def enterItems_list(self, ctx:ExpressionGrammarParser.Items_listContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#items_list.
    def exitItems_list(self, ctx:ExpressionGrammarParser.Items_listContext):
        pass


    # Enter a parse tree produced by ExpressionGrammarParser#par_item.
    def enterPar_item(self, ctx:ExpressionGrammarParser.Par_itemContext):
        pass

    # Exit a parse tree produced by ExpressionGrammarParser#par_item.
    def exitPar_item(self, ctx:ExpressionGrammarParser.Par_itemContext):
        pass
