import json

class SymAIExpression:

    def __init__(self):
        self.solver = None

    def get_solver(self):
        return self.solver

    def set_solver(self, slvr):
        self.solver = slvr

    def postprocess(self, args):
        raise Exception("postprocess method is not implemented yet")

    def preprocess(self, args):
        raise Exception("preprocess method is not implemented yet")

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
            res = self.postprocess_simplify(self.process_body_simplify(self.preprocess_simplify(expr)))
            source_expr["formula"] = res
            return source_expr

