import math

class MathUtils:
    @staticmethod
    def cotan(x):
        return 1 / math.tan(x)

    @staticmethod
    def arccotan(x):
        if x == 0:
            return math.pi / 2
        elif x > 0:
            return math.atan(1 / x)
        else:  # x < 0
            return math.atan(1 / x) + math.pi

    @staticmethod
    def fill_gvars_func(func: dict = None) -> dict:

        if func is None:
            func = dict()
        func["sin"] = math.sin
        func["cos"] = math.cos
        func["tan"] = math.tan
        func["cotan"] = MathUtils.cotan
        func["asin"] = math.asin
        func["acos"] = math.acos
        func["atan"] = math.atan
        func["acotan"] = MathUtils.arccotan
        func["log"] = math.log
        func["lg"] = math.log10
        func["sqrt"] = math.sqrt
        func["exp"] = math.exp
        func["pow"] = math.pow

        return func
