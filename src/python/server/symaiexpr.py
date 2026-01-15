from symbolicexpressiongrammarvisitor import *

from treeutils import *

class SymAIExpression:

    def __init__(self):
        self.solver = None
        self.max_models = 10

    def get_solver(self):
        return self.solver

    def set_solver(self, slvr):
        self.solver = slvr

    def get_max_models(self):
        return self.max_models

    def set_max_models(self, m : int):
        self.max_models = m

    def postprocess(self, args):
        parser = TreeUtils.prepare_parser_beh(args)
        visitor = SymbolicExpressionGrammarVisitor()
        tree = parser.expression()

        fml = visitor.visit(tree)

        return (" " + fml + " ").replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace("__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" ")

    def preprocess(self, args):
        expr_n = (" " + args + " ").replace(" not ", " _n_o_t_ ").replace("_d_o_t_", "__d__o__t__").strip("\\ ")
        parser = TreeUtils.prepare_parser_beh(expr_n)
        return parser

    def process_body(self, args):
        raise Exception("postprocess method is not implemented yet")

    def preprocess_simplify(self, args):
        return self.preprocess(args)

    def postprocess_simplify(self, args):
        return self.postprocess(args)

    def process_body_simplify(self, args):
        return self.process_body(args)

    def process_simplify(self, source_expr):
        expr = source_expr.get("formula")
        if expr is None:
            raise Exception("Bad Request: missing formula field")
        else:
            cvals, vals, tail = TreeUtils.get_vars_using_assignment(expr)
            for it in vals:
                if len(tail) > 0:
                    tail = tail + "&&"
                tail = tail + str(it) + "==" + str(vals[it])

            if len(tail) > 0:
                rf = self.postprocess_simplify(self.process_body_simplify(self.preprocess_simplify(tail)))
            else:
                rf = ""

            for it in cvals.keys():
                if len(rf) > 0:
                    rf = rf + "&&"
                rf = rf + str(it) + "==" + str(cvals[it])

            source_expr["formula"] = rf
            return source_expr

    def preprocess_check(self, args):
        return self.preprocess(args)

    def postprocess_check(self, args):
        args.pop("visitor")
        args.pop("tree")

        parser = self.preprocess_check(args["formula"])
        subs = args.get("substitution")
        if subs is None:
            subs = dict()
        tree = parser.expression()
        visitor = SymbolicExpressionGrammarVisitor()
        visitor.setSubstitution(subs)
        fml = str(visitor.visit(tree))
        args["formula"] = self.postprocess(fml)
        return self.process_simplify(args)

    def process_body_check(self, args):
        return self.process_body(args)

    def process_check(self, source_expr):
        expr = source_expr.get("formula")
        if expr is None:
            raise Exception("Bad Request: missing formula field in check request")
        else:
            cvals, vals, tail = TreeUtils.get_vars_using_assignment(expr)
            for it in vals:
                if len(tail) > 0:
                    tail = tail + "&&"
                tail = tail + str(it) + "==" + str(vals[it])
            parser = self.preprocess_check(tail)

            subs = source_expr.get("substitution")
            if subs is None:
                subs = dict()
            # Here we should merge cvals and subst!!!!
            tree = parser.expression()
            visitor = SymbolicExpressionGrammarVisitor()
            visitor.setSubstitution(subs)
            fml = str(visitor.visit(tree))
            formula = self.postprocess(fml)
            source_expr["formula"] = formula
            source_expr["is_trigonometric"] = visitor.isTrigonometric()
            source_expr["is_nonlinear"] = visitor.isNonLinear()
            source_expr["vars"] = visitor.getVarList()
            source_expr["substitution"] = visitor.getSubstitution()
            source_expr["visitor"] = visitor
            source_expr["tree"] = tree
            source_expr = self.process_body_check(source_expr)
            res = self.postprocess_check(source_expr)
            rf = ""
            for it in cvals.keys():
                if len(rf) > 0:
                    rf = rf + "&&"
                rf = rf + str(it) + "==" + str(cvals[it])
            res["formula"] = rf
            return res

    def preprocess_inverse(self, args):
        return self.preprocess(args)

    def postprocess_inverse(self, args):
        args.pop("visitor")
        args.pop("tree")
        inv = args.pop("inverse")
        k = args.get("target")
        s = k + " = " + inv.get(k)
        args["inverse"] = s
        return args

    def process_body_inverse(self, args):
        return self.process_body(args)

    def process_inverse(self, source_expr):
        expr = source_expr.get("formula")
        if expr is None:
            raise Exception("Bad Request: missing formula field in inverse request")
        else:
            s = expr.split("=")[0]
            t = expr[len(s) + 1:]
            t = "(" + t + ") - " + s
            parser = self.preprocess_inverse(t + '-' + s)
            source_expr.pop("formula")
            source_expr["formula"] = t
            if "target" not in source_expr.keys():
                source_expr["target"] = s

            subs = source_expr.get("substitution")
            if subs is None:
                subs = dict()
            tree = parser.expression()
            visitor = SymbolicExpressionGrammarVisitor()
            visitor.setSubstitution(subs)
            visitor.visit(tree)
            vars = visitor.getVarList()
            if vars is None or len(vars) > 0:
                if "target" not in source_expr.keys():
                    source_expr["target"] = vars[0]
            source_expr["tree"] = tree
            source_expr["visitor"] = visitor

            source_expr = self.process_body_inverse(source_expr)
            source_expr["formula"] = expr
            return self.postprocess_inverse(source_expr)
