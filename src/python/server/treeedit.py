from collections import deque
from extsegammarvisitor import *

class TreeEdit:
    @staticmethod
    def cmp_tok(node, args, kwargs):
        token = ""
        for k, v in kwargs.items():
            if k == "token":
                token = v
                break

        if str(type(node)) == "<class 'antlr4.tree.Tree.TerminalNodeImpl'>":
            if node.symbol.text == token:
                return True
        return False

    @staticmethod
    def find_by_token(tree, tok):
        return TreeEdit.find_by_cond(tree, TreeEdit.cmp_tok, token=tok)

    @staticmethod
    def find_by_cond(tree, cnd, *args, **kwargs):
        if tree is None:
            return None
        stk = deque()
        stk.append(tree)
        while len(stk) > 0:
            n = stk.pop()
            if cnd(n, args, kwargs):
                return n
            if str(type(n)) != "<class 'antlr4.tree.Tree.TerminalNodeImpl'>":
                i = n.getChildCount() - 1
                while i >= 0:
                    c = n.getChild(i)
                    i = i - 1
                    stk.append(c)

        return None

    @staticmethod
    def delete_node(node):
        if node is None:
            return None
        n = node
        c = n.parentCtx
        if c is not None:
            i = 0
            while i < n.getChildCount():
                child = c.getChild(i)
                if child == n:
                    temp = c.getChild(i)
                    temp.parentCtx = None
                    del c.children[i]
                    break
                i = i + 1
        if n.getChildCount() < 1:
            node = node.parentCtx
        return node
