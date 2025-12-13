from collections import deque
from antlr4.tree.Tree import TerminalNodeImpl

class TreeEdit:
    @staticmethod
    def cmp_tok(node, args, kwargs):
        token = ""
        for k, v in kwargs.items():
            if k == "token":
                token = v
                break

        if type(node) == TerminalNodeImpl:
            if node.symbol.text == token:
                return True
        return False

    @staticmethod
    def compare_tokens(node, args, kwargs):
        tokens = []
        for k, v in kwargs.items():
            if k == "tokens":
                tokens = v
                break

        if type(node) == TerminalNodeImpl:
            if node.symbol.text in tokens:
                return True
        return False

    @staticmethod
    def find_all_by_tokens(tree, tok):
        return TreeEdit.find_all_by_cond(tree, TreeEdit.compare_tokens, tokens=tok)

    @staticmethod
    def find_one_by_tokens(tree, tok):
        return TreeEdit.find_one_by_cond(tree, TreeEdit.compare_tokens, tokens=tok)

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
            if type(n) != TerminalNodeImpl:
                i = n.getChildCount() - 1
                while i >= 0:
                    c = n.getChild(i)
                    i = i - 1
                    stk.append(c)

        return None

    @staticmethod
    def find_all_by_cond(tree, cnd, *args, **kwargs):
        res = []
        if tree is not None:
            stk = deque()
            stk.append(tree)
            while len(stk) > 0:
                n = stk.pop()
                if cnd(n, args, kwargs):
                    res.append(n)
                if type(n) != TerminalNodeImpl:
                    i = n.getChildCount() - 1
                    while i >= 0:
                        c = n.getChild(i)
                        i = i - 1
                        stk.append(c)

        return res

    @staticmethod
    def find_one_by_cond(tree, cnd, *args, **kwargs):
        res = []
        if tree is not None:
            stk = deque()
            stk.append(tree)
            while len(stk) > 0:
                n = stk.pop()
                if cnd(n, args, kwargs):
                    return n
                if type(n) != TerminalNodeImpl:
                    i = n.getChildCount() - 1
                    while i >= 0:
                        c = n.getChild(i)
                        i = i - 1
                        stk.append(c)

        return res

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
