from collections import deque
from http import HTTPStatus

import symaicommands
import symaiconfig
import http.client
import json
import uuid
from itertools import tee
import os

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from extsegammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser
from enum import Enum

class SymAIDebugCommands(Enum):
    NEXT = "next"
    STOP = "stop"
    RUN = "run"

class SymAICoreParam:

    def __init__(self):
        self.session_uuid = uuid.uuid4()
        self.actions = None
        self.behaviors = None
        self.environment = None
        self.property = None

    def get_uuid(self):
        return self.session_uuid

class SymAICoreCommands(symaicommands.SymAICommands):

    def remove_directory_tree(self, start_directory: str):
        """Recursively and permanently removes the specified directory, all of its
        subdirectories, and every file contained in any of those folders."""
        if os.path.exists(start_directory):
            for name in os.listdir(start_directory):
                path = os.path.join(start_directory, name)
                if os.path.isfile(path):
                    self.get_logger().debug(f"Deleting the '{path}' file.")
                    os.remove(path)
                else:
                    self.remove_directory_tree(path)
            self.get_logger().debug(f"Deleting the empty '{start_directory}' directory.")
            os.rmdir(start_directory)

    def do_shutdown(self):
        headers = {'Content-type': 'application/json'}
        try:
            conn = http.client.HTTPConnection(
                str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                        symaiconfig.SymAIConfig.EXPRESSION_HOST.value)),
                int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                        symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
            conn.request('GET', '/api/v1/system/shutdown', "", headers)
            conn.getresponse()
        except Exception as e:
            self.get_logger().error(f"Error on shutdown expression module {str(e)}")
        self.get_logger().info("Shutting down the service....")

    def do_stop(self, cuuid : str):
        self.remove_directory_tree(os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                                    str(cuuid)))

    """ Loads and saves the file
     The file path $TEPM_PATH/pref/mid/<filename> will be created, if it is not present
     Here $TEMP_PATH is a base temporary catalogue path; pref and mid are strings.
     data_received is a JSON structure in following format:
     { "filename":<filename>, "content":<content>}
     Here <filename> is a quoted string that represents a desired filename;
     <content> is a quoted string that represents a file content
    
     On success returns the structure that has two fields:
     - filename that is a source file name
     - content that is a content of this file
     On error raises an Exception 
     """
    def do_get_file(self, pref, mid, data_received):
        try:
            res = json.loads(data_received.replace("'", '"'))
        except Exception as e:
            self.get_logger().error("Incorrect input JSON data " + data_received + " " + str(e))
            raise Exception("Incorrect input JSON data " + data_received)
        if res["filename"] is None or len(res["filename"].strip()) == 0:
            self.get_logger().error("Incorrect JSON data. Field 'filename' is empty.")
            raise Exception("Incorrect JSON data. Field 'filename' is empty.")
        elif res["content"] is None or len(res["content"].strip()) == 0:
            self.get_logger().error("Incorrect JSON data. Field 'content' is empty.")
            raise Exception("Incorrect JSON data. Field 'content' is empty.")
        else:
            d = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                                    pref,
                                    mid)
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except:
                    raise Exception(f"Cannot create directory {d}")
            filename = os.path.join(d, res["filename"].strip())
            file_content = str(res["content"])
            try:
                with open(filename, "w") as file:
                    file.write(file_content)
            except:
                raise Exception("Cannot write content to file '" + str(filename) + "'")
        return res

    def prepare_parser_expr(self, inp : str)->ExpressionGrammarParser :
        lexer = ExpressionGrammarLexer(InputStream(inp))
        error_listener = SymbolicExpressionGrammarErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        stream = CommonTokenStream(lexer)
        parser = ExpressionGrammarParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        return parser

    def do_behaviors(self, cuuid, data_received):
        cnt = self.do_get_file(cuuid,
                               symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                               data_received)
        fn = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                          cuuid,
                          symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                          cnt["filename"])
        try:
            tree = self.prepare_parser_expr(cnt["content"]).behavior()
            visitor = ExtSEGrammarVisitor()
            res = visitor.visit(tree)
            with open(fn, "w") as f:
                f.write(res)
            self.get_logger().info(f"behaviors command processed. The behaviors list saved to {fn}")
            setattr(self, "behaviors", fn)
        except Exception as e:
            self.get_logger().error(f"behaviors command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            raise e

    def get_debug(self):
        if hasattr(self, "debug"):
            fn = getattr(self, "debug")
        else:
            try:
                fn = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.SYMAICORE_DEBUG.value)
                try:
                    fn = bool(fn)
                except:
                    try:
                        i = int(fn)
                        if i == 1:
                            fn = True
                        else:
                            fn = False
                    except:
                        fn = False
            except:
                fn = False
            c = self.get_config()
            c.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.SYMAICORE_DEBUG.value, str(fn))
            self.set_config(c)
        setattr(self,"debug", fn)

        return fn

    def invert_one_action(self, name, expr):
        tree = self.prepare_parser_expr(expr).assignmentExpression()
        visitor = ExtSEGrammarVisitor()
        a = visitor.visit(tree)
        i = a.strip().find("=")
        if i == -1:
            if a != "1":
                raise Exception(f"Incorrect action description {a}")
            else:
                res = a
        else:
            headers = {'Content-type': 'application/json'}
            l = a[:i].strip()
            r = a[i+1:].strip()
            tr = self.prepare_parser_expr(r).assignmentExpression()
            v = ExtSEGrammarVisitor()
            v.visit(tr)
            vl = v.getVarList()
            if l in vl:
                i = 0
                nm = l + str(i)
                while nm in vl:
                    i = i + 1
                    nm = l + str(i)
                nexpr = nm + "=" + r
                # Make an HTTP request to inverse equation
                expression_host = str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                            symaiconfig.SymAIConfig.EXPRESSION_HOST.value))
                expression_port = int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                            symaiconfig.SymAIConfig.EXPRESSION_PORT.value))
                conn = http.client.HTTPConnection(expression_host, expression_port)
                query = dict()
                query["formula"] = nexpr
                slvr = self.get_solver()
                query["solver"] = slvr
                conn.request('POST', '/api/v1/expression/inverse', json.dumps(query), headers)
                response = conn.getresponse()
                if not (response.getcode() == HTTPStatus.OK):
                    raise Exception(f"Attempt to inverse expression error {str(conn.getresponse())}")
                rsp = json.loads(response.read().decode())
                rs = rsp["inverse"]
                it = iter(rs)
                inv = (next(it))
                inv = l + "=" + rs[inv]
                subsn = [{"name": nm, "value": l}]
                tr = self.prepare_parser_expr(inv).assignmentExpression()
                v = ExtSEGrammarVisitor()
                v.setSubstitution(subsn)
                res = v.visit(tr)
            else:
                res = a
            res = a
        return res

    def invert_actions(self, cuuid, visitor, fname):
        res = dict()
        if hasattr(self, "inverted"):
            fn = getattr(self, "inverted")
        elif hasattr(self, "actions"):
            fn = getattr(self, "actions") + ".inv"
        else:
            fn = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                              cuuid,
                              symaiconfig.SymAIConfig.BASE_ACTIONS.value,
                              fname + ".inv")
        try:
            rs = visitor.getResults()
            with open(fn, "w") as f:
                for act in rs:
                    nm = act[0]
                    expr = act[2]
                    ra = expr.split(";")
                    r = []
                    for s in ra:
                        r.append(self.invert_one_action(nm, s)) # TODO: What if no inversions needed!!!
                        #r.append(s)
                    res[nm]  = r
                    f.write(f"{nm}:{res[nm]}\n")
            self.get_logger().debug(f"Inverted actions saved to {fn}")
            setattr(self,"inverted", fn)
            setattr(self, "inverted_actions", res)
        except Exception as e:
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            raise e
        return res

    def do_actions(self, cuuid, data_received):
        cnt = self.do_get_file(cuuid,
                               symaiconfig.SymAIConfig.BASE_ACTIONS.value,
                               data_received)
        fn = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                          cuuid,
                          symaiconfig.SymAIConfig.BASE_ACTIONS.value,
                          cnt["filename"])
        try:
            tree = self.prepare_parser_expr(cnt["content"]).actionsList()
            visitor = ExtSEGrammarVisitor()
            res = visitor.visit(tree)
            with open(fn, "w") as f:
                f.write(res)
            setattr(self, "actions", fn)
            self.invert_actions(cuuid, visitor, fn)
            self.get_logger().info(f"actions command processed. The actions list saved to {fn}")
        except Exception as e:
            self.get_logger().error(f"actions command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            delattr(self, "actions")
            raise e

    def do_environment(self, cuuid, data_received):
        res = self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value)

        fn = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                          cuuid,
                          symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value,
                          res["filename"])
        try:
            with open(fn, "w") as f:
                f.write(res["content"])
            self.get_logger().info(f"environment command processed. The environment saved to {fn}")
            setattr(self, "environment", fn)
        except Exception as e:
            self.get_logger().error(f"environment command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            raise e

    def do_property(self, cuuid, data_received):
        res = self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_PROPERTIES.value)
        fn = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                          cuuid,
                          symaiconfig.SymAIConfig.BASE_PROPERTIES.value,
                          res["filename"])
        try:
            with open(fn, "w") as f:
                f.write(res["content"])
            self.get_logger().info(f"property command processed. The property saved to {fn}")
            setattr(self, "property", fn)
        except Exception as e:
            self.get_logger().error(f"property command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            raise e

    def get_behaviors(self):
        if hasattr(self, "behaviors"):
            fn = getattr(self, "behaviors")
            try:
                f = open(fn, "r")
                cnt = f.read()
                tree = self.prepare_parser_expr(cnt).behavior()
                visitor = ExtSEGrammarVisitor()
                res = visitor.visit(tree)
                self.get_logger().debug(f"behaviors successful retrieved. File {fn}")
            except Exception as e:
                self.get_logger().error(f"retrieving behaviors failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve behaviors")
            return res, visitor
        raise Exception("No behaviors were defined")

    def get_actions(self):
        if hasattr(self, "actions"):
            fn = getattr(self, "actions")
            try:
                f = open(fn, "r")
                cnt = f.read()
                tree = self.prepare_parser_expr(cnt).actionsList()
                visitor = ExtSEGrammarVisitor()
                res = visitor.visit(tree)
                self.get_logger().debug(f"actions successful retrieved. File {fn}")
            except Exception as e:
                self.get_logger().error(f"retrieving actions failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve actions")
            return res, visitor
        raise Exception("No actions were defined")

    def get_property(self):
        if hasattr(self, "property"):
            fn = getattr(self, "property")
            try:
                f = open(fn, "r")
                cnt = f.read()
                tree = self.prepare_parser_expr(cnt).expression()
                visitor = ExtSEGrammarVisitor()
                res = visitor.visit(tree)
                self.get_logger().debug(f"property successful retrieved. File {fn}")
            except Exception as e:
                self.get_logger().error(f"retrieving property failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve property")
            return res
        raise Exception("No properties were defined")

    def get_environment(self):
        if hasattr(self, "environment"):
            fn = getattr(self, "environment")
            try:
                f = open(fn, "r")
                cnt = f.read()
                tree = self.prepare_parser_expr(cnt).expression()
                visitor = ExtSEGrammarVisitor()
                s = visitor.visit(tree)
                tree = self.prepare_parser_expr(s).expression()
                res = visitor.visit(tree).replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace("__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" ")
                self.get_logger().debug(f"environment successful retrieved. File {fn}")
            except Exception as e:
                self.get_logger().error(f"retrieving environment failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve environment")
            return res
        raise Exception("No environments were defined")

    def check_reachability(self, env:str, reach_property:str):

        if reach_property is None:
            reach_property = "True"
        if env is None:
            env = ""

        expr, ic, r = self.prepare_condition(env)
        if reach_property is not None and len(reach_property) > 0:
            s, ic, r = self.prepare_condition(reach_property)
            expr = expr + " && " + s

        headers = {'Content-type': 'application/json'}
        try:
            # Make an HTTP request for check
            expression_host = str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                    symaiconfig.SymAIConfig.EXPRESSION_HOST.value))
            expression_port = int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                          symaiconfig.SymAIConfig.EXPRESSION_PORT.value))
            conn = http.client.HTTPConnection(expression_host,expression_port)
            query = dict()
            query["formula"] = expr
            slvr = self.get_solver()
            query["solver"] = slvr
            conn.request('POST', '/api/v1/expression/check', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt check expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            res = rsp["satisfiable"]
            query.pop("formula")
            # Simplifying formula of environment
            query["formula"] = env
            conn = http.client.HTTPConnection(expression_host,expression_port)
            conn.request('POST', '/api/v1/expression/simplify', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt to simplify expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            r_env = rsp["formula"]
            self.get_logger().info(f"check_reachability ( {env}, {reach_property} ) command processed with {res}.")
        except Exception as e:
            self.get_logger().error(f"check_reachability ( {env}, {reach_property} ) command processing failed {str(e)}")
            raise e

        return res, r_env

    def prepare_condition(self, cnd:str):
        p =  self.prepare_parser_expr(cnd)
        tree = p.assignmentExpression()
        v = ExtSEGrammarVisitor()
        s = v.visit(tree)
        vl = v.getVarList()
        is_const = False
        r = False
        if vl is None or len(vl) <= 0:
            is_const = True
            s = str(eval(s))
            if s == "True" or s == "1":
                r = True
            elif s == "False":
                r = False
            else:
                try:
                    t = float(s)
                    if t == 0:
                        r = False
                    else:
                        r = True
                except ValueError:
                    r = False

            res = str(r)
        else:
            res = "((" + cnd + ")" + "!= 0)"
            if cnd.find("=") >= 0 or cnd.find("!") >= 0 or cnd.find(">") >= 0 or cnd.find("<") >= 0:
                res = "(" + cnd + ")"
        return res, is_const, r

    def do_recalc_const(self, expr, subst):

        env_exp = ""
        for fml in expr:
            int_vars = dict()
            if fml != "1":
                glob_vars = dict()
                s = fml.split("=")
                int_vars[s[0]] = s[1]
                for it in subst:
                    int_vars[it] = float(subst[it])

                exec(fml, glob_vars, int_vars)
            else:
                for it in subst:
                    int_vars[it] = float(subst[it])

            i = False
            env_exp  = ""
            for it in int_vars:
                if i:
                    env_exp = env_exp + " && "
                env_exp = env_exp + "(" + str(it) + " == " +  str(int_vars[it]) + ")"
                i = True

        return env_exp

    def do_sm_substitution(self, env, expr):

        is_const = False
        variables = ""
        headers = {'Content-type': 'application/json'}
        try:
            # Make an HTTP request for check
            expression_host = str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                        symaiconfig.SymAIConfig.EXPRESSION_HOST.value))
            expression_port = int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                        symaiconfig.SymAIConfig.EXPRESSION_PORT.value))
            conn = http.client.HTTPConnection(expression_host, expression_port)
            query = dict()
            slvr = self.get_solver()
            query["solver"] = slvr
            query["formula"] = env
            query["maxmodels"] = "10"

            # TODO: Environment recalculation here !!!
            conn.request('POST', '/api/v1/expression/check', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception(f"Attempt to recalculate environment error {str(conn.getresponse())} {response.reason}")
            rsp = json.loads(response.read().decode())
            env = rsp["formula"]
            if rsp["satisfiable"]:
                if len(rsp["model"]) == 1:
                    # We have only one model. So it is const solution
                    is_const = True
                    variables = next(iter(rsp["model"]))
                    env = self.do_recalc_const(expr, variables)
                else:
                    p = self.prepare_parser_expr(env)
                    tree = p.assignmentExpression()
                    v = ExtSEGrammarVisitor()
                    s =  expr.split("=")
                    if len(s) > 1:
                        d = dict()
                        d[s[0]] = s[1]
                        v.setSubstitution(d)
                        s = v.visit(tree)
                        p = self.prepare_parser_expr(s)
                        tree = p.assignmentExpression()
                        v = ExtSEGrammarVisitor()
                        env = v.visit(tree)
                        # TODO: Add replacements for other cases else !!!

        except Exception as e:
            self.get_logger().error(f"do_sm_substitution method processing failed {str(e)}")
            raise e
        return env, is_const, variables

    def step_modelling(self, ctx, act):
        act_visitor = ctx["act_visitor"]
        cnd = ""
        a = act_visitor.getResults()
        for r in a:
            if r[0] == act:
                cnd = str(r[1])
                break
        s, is_const, r = self.prepare_condition(cnd)
        # Here r is mark. If !r, we should continue calculations. Else we should change the environment
        b = False
        if (not is_const and not (r or s == True)) or (is_const and (s == "True" or s == "1")):
            #
            # TODO: Here should be placed checking for linearity and call for approximation of source expr
            # if (not is_const and not (r or s == True))
            #

            b, s = self.check_reachability(ctx["environment"], cnd)
        if b:
            expr = ctx["inverted_actions"][act]
            ctx["environment"], is_const, variables = self.do_sm_substitution(ctx["environment"], expr)

        return ctx, b

    def do_load_traversal_data(self, cuuid, data_received):
        if data_received is not None and len(data_received) > 0:
            dr = json.loads(data_received)
        else:
            if data_received is None:
                pass
            dr = dict()

        # Loading parameters, if any incoming were saved. Throwing an exception in case of error
        # Returns the context dictionary in case of success. Raises an exception in case or error
        ctx = dict()
        ctx["cuuid"] = cuuid

        if hasattr(self, "trace_file"):
            ctx["trace_file"] = getattr(self, "trace_file")

        beh, beh_visitor = self.get_behaviors()
        ctx["behaviors"] = beh
        ctx["beh_visitor"] = beh_visitor

        act, act_visitor = self.get_actions()
        ctx["actions"] = act
        ctx["act_visitor"] = act_visitor
        ctx["inverted_actions"] = self.invert_actions(cuuid, act_visitor, "actions")

        prop = self.get_property()
        ctx["property"] = prop

        env = self.get_environment()
        ctx["environment"] = env

        try:
            if "reenter_count" in dr:
                ctx["reenter_count"] = dr["reenter_count"]
            else:
                ctx["reenter_count"] = self.get_reenter_count()
            ctx["reenter_count"] = int(ctx["reenter_count"])
        except:
            ctx["reenter_count"] = 1

        return ctx

    def is_action(self, actions, term):
        for a in actions:
            if str(a[0]) == str(term):
                return True
        return False

    def find_behavior(self, behaviors, term):
        for bh in behaviors:
            if str(bh) == str(term):
                return behaviors[bh]
        return None

    def append_trace(self, ctx, trace, env_trace):
        fn = ""
        try:
            if "trace" not in ctx or ctx["trace"] is None or "trace_file" not in ctx:
                if "trace_file" in ctx:
                    fn = ctx["trace_file"]
                else:
                    fn = os.path.join( symaiconfig.SymAIConfig.BASE_TEMP.value,
                                       ctx["cuuid"],
                                       symaiconfig.SymAIConfig.BASE_TRACE.value,
                                       symaiconfig.SymAIConfig.BASE_TRACE_FILE.value)
                ctx["trace_file"] = fn
                ctx["trace"] = str(self.dump_trace(trace))
                ctx["env_trace"] = str(self.dump_trace(env_trace))
                with open(fn, "w") as f:
                    f.write(str(self.dump_trace(trace)) + "\n" + str(self.dump_trace(env_trace)) + "\n")
            else:
                fn = ctx["trace_file"]
                ctx["trace"] = ctx["trace"] + "\n" + str(self.dump_trace(trace))
                ctx["env_trace"] = ctx["env_trace"] + "\n" + str(self.dump_trace(env_trace))

                with open(fn, "a+") as f:
                    f.write(str(self.dump_trace(trace)) + "\n" + str(self.dump_trace(env_trace)))

            self.get_logger().info(f"trace saved to {fn}")
        except Exception as e:
            self.get_logger().error(f"saving trace processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
                ctx["trace"] = None
                ctx["trace_file"] = None
            except:
                pass
            raise e
        return ctx

    def dump_trace(self, trace) -> str:
        res = "["
        b =  False
        for it in trace:
            if b:
                res = res + ","
            res = res + " " + str(it)
            b = True
        res = res + " ]"
        return res

    def do_traversalbeh(self, cuuid, data_received):
        yield "ok start traversal behaviors"
        self.get_logger().info(f"traversal behaviors started {data_received}")
        slvr = None
        try:
            ctx = self.do_load_traversal_data(cuuid, data_received)
            yield "ok input data retrieved"
            # Processing
            self.get_logger().debug(f"traversal behaviors input data retrieved")
            behaviors = ctx["beh_visitor"].getBehaviors()
            actions = ctx["act_visitor"].getResults()

            # Parsing incoming data
            is_first = True
            if data_received is not None and len(data_received) > 0:
                try:
                    dr = json.loads(data_received.replace("'", '"'))
                except Exception as e:
                    self.get_logger().error(f"Incorrect input `{data_received}` JSON data {str(e)}`")
                    raise Exception(f"Incorrect input `{data_received}` JSON data {str(e)}`")
                if "behavior" in dr:
                    if dr["behavior"] in behaviors:
                        is_first = False
                if "solver" in dr:
                    slvr = self.get_solver()
                    self.do_solver(cuuid, dr["solver"])
                if "debug" in dr:
                    try:
                        fn = dr["debug"]
                        try:
                            fn = bool(fn)
                        except:
                            try:
                                i = int(fn)
                                if i == 1:
                                    fn = True
                                else:
                                    fn = False
                            except:
                                fn = False
                    except:
                        fn = False

                    setattr(self, "debug", fn)
            else:
                dr = dict()
            if len(behaviors) > 0 and is_first:
                dr["behavior"] = next(iter(behaviors))

            yield "ok trace start"
            env_trace = deque([])
            trace = deque([])
            beh_stack = deque([])

            if len(behaviors) <= 0:
                raise Exception("No behaviors were defined")
            else:
                # Selecting an appropriate behavior to process.
                # AI can be used here for initial cur_beh selection
                # Now choosing the first behavior by default
                cur_beh = dr["behavior"]
                cur_alt = 1
                it = iter(behaviors[cur_beh])
                it, cit = tee(it)
                beh_stack.append([cur_beh,cit, behaviors[cur_beh], cur_alt, ctx["environment"]])
                trace.append(cur_beh)
                env_trace.append(ctx["environment"])
                setattr(self, "stop", False)
                is_reached = False
                while not getattr(self, "stop"):
                    try:
                        term = next(it)
                        match term:
                            case ".":
                                continue
                            case "+":
                                while len(trace) > cur_alt:
                                    trace.pop()
                                    ctx["environment"] = env_trace.pop()
                                continue
                            case "(":
                                cnt_in = 0
                                beh_inner = [term]
                                nm = term
                                while True:
                                    term = next(it)
                                    beh_inner.append(term)
                                    nm = nm + term
                                    if term == "(":
                                        cnt_in = cnt_in + 1
                                        continue
                                    if term == ")":
                                        if cnt_in <= 0:
                                            break
                                        cnt_in = cnt_in - 1

                                it, cit = tee(it)
                                it = iter(beh_inner)
                                term = next(it)
                                trace.append(nm)
                                env_trace.append(ctx["environment"])
                                cur_alt = len(trace)
                                beh_stack.append([nm, cit, beh_inner, cur_alt, ctx["environment"]])
                                continue
                            case ")":
                                if len(beh_stack) > 1:
                                    r = beh_stack.pop()
                                    cb = r[0]
                                    it = r[1]
                                    ctr = r[2]
                                    cur_alt = r[3]
                                    e = r[4]
                                else:
                                    setattr(self, "stop", True)
                                    break
                            case default:
                                cb = self.find_behavior(behaviors, term)
                                if self.is_action(actions, term):
                                    ctx, is_sat = self.step_modelling(ctx, term)
                                    if is_sat:
                                        trace.append(term)
                                        res, ctx["environment"] = self.check_reachability(ctx["environment"], ctx["property"])
                                        env_trace.append(ctx["environment"])
                                        cur_alt = len(trace)
                                        if res:
                                            is_reached = True
                                        else:
                                            is_reached = False
                                        """
                                        if res:
                                            trace.append("REACHED")
                                            env_trace.append(ctx["environment"])
                                            # if trace.count("REACHED") > 2:
                                            #    break
                                        """
                                    else:
                                        continue
                                elif cb is not None:
                                    it, cit = tee(it)
                                    if trace.count(term) > ctx["reenter_count"]  > 0:
                                        trace.append(term)
                                        env_trace.append(ctx["environment"])
                                        trace.append("REENTERED")
                                        env_trace.append(ctx["environment"])
                                        cur_alt = len(trace)
                                        # Well. We're visited {term}
                                        continue
                                    else:
                                        beh_stack.append([term, cit, behaviors[term], cur_alt, ctx["environment"]])
                                        it = iter(behaviors[term])
                                        trace.append(term)
                                        env_trace.append(ctx["environment"])
                                        cur_alt = len(trace)
                                        continue
                                else:
                                    trace.append(term)
                                    env_trace.append(ctx["environment"])
                                    raise Exception(f"Unknown term {term}")
                        if is_reached:
                            try:
                                idx = trace.index("REACHED")
                                del trace[idx]
                                del env_trace[idx]
                            except ValueError:
                                pass
                            trace.append("REACHED")
                            env_trace.append(ctx["environment"])
                            is_reached = False
                        yield f"ok trace {self.dump_trace(trace)}"
                        yield f"ok environment trace {self.dump_trace(env_trace)}"
                        ctx = self.append_trace(ctx, trace, env_trace)
                    except StopIteration:
                        if len(beh_stack) > 1:
                            r = beh_stack.pop()
                            cb = r[0]
                            it = r[1]
                            ctr = r[2]
                            cur_alt = r[3]
                            e = r[4] ## TODO: HERE IS IT! Environment SHOULD NOT BE CHANGED
                        else:
                            setattr(self, "stop", True)
                            break
            # Finalizing
            yield "ok trace end"
            yield "ok end traversal behaviors"
            self.get_logger().info("traversal behaviors finished")
        except Exception as e:
            self.get_logger().error(f"traversal behaviors failed with {e}")
            yield f"nok Traversal behaviors failed {e}"
        finally:
            if slvr is not None:
                self.do_solver(cuuid, slvr)

    def do_rsp_traversalbeh(self, cuuid, data_received):
        if data_received is not None and len(data_received) > 0 and self.get_debug():
            s = str(data_received).strip(" \t").lower()
            match s:
                case SymAIDebugCommands.NEXT.value:
                    return False
                case SymAIDebugCommands.STOP.value:
                    setattr(self, "stop", True)
                    return True
                case SymAIDebugCommands.RUN.value:
                    setattr(self, "debug", False)
                    return False
        else:
            return self.get_debug()

    def do_trace(self, cuuid, data_received):
        try:
            r = ""
            if data_received is not None:
                s = data_received.trim()
                if s != "remove":
                    raise Exception(f"Incorrect trace command parameter {data_received}")
                else:
                    if hasattr(self, "trace_file"):
                        path = getattr(self, "trace_file")
                        if path is not None:
                            if os.path.isfile(path):
                                self.get_logger().debug(f"Deleting the '{path}' file.")
                                os.remove(path)
                            setattr(self, "trace_file", None)
            else:
                if hasattr(self, "trace"):
                    r = getattr(self, "trace")
                    if r is None:
                        r = ""
        except Exception as e:
            raise e
        return r

    def get_and_simplify(self, cuuid, data_received, infix):
        # Loading
        res = self.do_get_file(cuuid,
                               infix,
                               data_received)
        # checking and simplifying content
        headers = {'Content-type': 'application/json'}
        try:
            # Make an HTTP request for simplifying
            conn = http.client.HTTPConnection(
                str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                          symaiconfig.SymAIConfig.EXPRESSION_HOST.value)),
                int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                          symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
            query = dict()
            query["formula"] = res["content"].strip()
            if hasattr(res, "solver"):
                slvr = res.get("solver")
            else:
                slvr = self.get_solver()
            query["solver"] = slvr
            conn.request('POST', '/api/v1/expression/simplify', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt simplify expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            with open(os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                        cuuid,
                        infix,
                        res["filename"]), "w") as f:
                f.write(rsp["formula"])
            self.get_logger().info(f"{infix} command processed. The {infix} formula {rsp.get('formula')} saved")
        except Exception as e:
            self.get_logger().error(f"{infix} command processing failed {str(e)}")
            raise e
        res["formula"] = rsp["formula"]
        return res

    def do_ai(self, cuuid, msg:str):
        b = False
        if hasattr(self, "ai"):
            b = getattr(self, "ai")
        else:
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.AI.value)
                if s is not None:
                    if s.lower() == "true" or s.lower() == "yes" or s.lower() == "1":
                        b = True
            except:
                b = False
        s = str(msg).strip().split()
        is_flush = False
        if len(s) == 1:
            if not hasattr(self, "ai"):
                setattr(self, "ai", b)
            b = getattr(self, "ai")
        elif len(s) == 2:
            if s[1].lower() == "flush":
                is_flush = True
            elif s[1].lower() == "true" or s[1].lower() == "yes" or s[1].lower() == "1":
                setattr(self, "ai", True)
            else:
                setattr(self, "ai", False)
            b = getattr(self, "ai")
        elif len(s) == 3:
            if s[2].lower() == "flush":
                is_flush = True
                if s[1].lower() == "true" or s[1].lower() == "yes" or s[1].lower() == "1":
                    setattr(self, "ai", True)
                elif s[1].lower() == "false" or s[1].lower() == "no" or s[1].lower() == "0":
                    setattr(self, "ai", False)
                else:
                    raise Exception(f"Incorrect command format {msg}")
            elif s[1].lower() == "flush":
                is_flush = True
                if s[2].lower() == "true" or s[2].lower() == "yes" or s[2].lower() == "1":
                    setattr(self, "ai", True)
                elif s[2].lower() == "false" or s[2].lower() == "no" or s[2].lower() == "0":
                    setattr(self, "ai", False)
                else:
                    raise Exception(f"Incorrect command format {msg}")
            else:
                raise Exception(f"Incorrect command format {msg}")
            b = getattr(self, "ai")
        else:
            raise Exception(f"Incorrect command format {msg}")
        if is_flush:
            cfg = self.get_config()
            cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value,
                    symaiconfig.SymAIConfig.AI.value, str(b))
            symaiconfig.create_config(symaiconfig.get_config_file(),
                                      symaiconfig.SymAIConfig.SYMAICORE.value, cfg)
        return str(b)

    def do_debug(self, cuuid, msg:str):
        b = False
        if hasattr(self, "debug"):
            b = getattr(self, "debug")
        else:
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.SYMAICORE_DEBUG.value)
                if s is not None:
                    if s.lower() == "true" or s.lower() == "yes" or s.lower() == "1":
                        b = True
            except:
                b = False
        s = str(msg).strip().split()
        is_flush = False
        if len(s) == 1:
            if not hasattr(self, "debug"):
                setattr(self, "debug", b)
            b = getattr(self, "debug")
        elif len(s) == 2:
            if s[1].lower() == "flush":
                is_flush = True
            elif s[1].lower() == "true" or s[1].lower() == "yes" or s[1].lower() == "1":
                setattr(self, "debug", True)
            else:
                setattr(self, "debug", False)
            b = getattr(self, "debug")
        elif len(s) == 3:
            if s[2].lower() == "flush":
                is_flush = True
                if s[1].lower() == "true" or s[1].lower() == "yes" or s[1].lower() == "1":
                    setattr(self, "debug", True)
                elif s[1].lower() == "false" or s[1].lower() == "no" or s[1].lower() == "0":
                    setattr(self, "debug", False)
                else:
                    raise Exception(f"Incorrect command format {msg}")
            elif s[1].lower() == "flush":
                is_flush = True
                if s[2].lower() == "true" or s[2].lower() == "yes" or s[2].lower() == "1":
                    setattr(self, "debug", True)
                elif s[2].lower() == "false" or s[2].lower() == "no" or s[2].lower() == "0":
                    setattr(self, "debug", False)
                else:
                    raise Exception(f"Incorrect command format {msg}")
            else:
                raise Exception(f"Incorrect command format {msg}")
            b = getattr(self, "debug")
        else:
            raise Exception(f"Incorrect command format {msg}")
        if is_flush:
            cfg = self.get_config()
            cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value,
                    symaiconfig.SymAIConfig.SYMAICORE_DEBUG.value, str(b))
            symaiconfig.create_config(symaiconfig.get_config_file(),
                                      symaiconfig.SymAIConfig.SYMAICORE.value, cfg)
        return str(b)

    def get_solver(self)->str:

        if hasattr(self, "solver"):
            b = getattr(self, "solver")
        else:
            b = symaiconfig.SymAISolvers.SYMPY.value
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value)
                if s in symaiconfig.SymAISolvers._value2member_map_:
                    b = s
            except:
                b = symaiconfig.SymAISolvers.Z3.value
        return b

    def do_solver(self, cuuid, msg:str):
        b = self.get_solver()
        is_flush = False
        s = msg.strip().split()
        if len(s) == 1:
            if hasattr(self, "solver"):
                b = getattr(self, "solver")
        elif len(s) == 2:
            if s[1] in symaiconfig.SymAISolvers._value2member_map_:
                b = s[1]
            elif s[1].lower() == "flush":
                is_flush = True
            else:
                raise Exception(f"Incorrect value {s[1]}")
        elif len(s) == 3:
            if s[1].lower() == "flush":
                is_flush = True
                if s[2] in symaiconfig.SymAISolvers._value2member_map_:
                    b = s[2]
                else:
                    raise Exception(f"Incorrect command format {msg}")
            elif s[2].lower() == "flush":
                is_flush = True
                if s[1] in symaiconfig.SymAISolvers._value2member_map_:
                    b = s[1]
                else:
                    raise Exception(f"Incorrect command format {msg}")
            else:
                raise Exception(f"Incorrect command format {msg}")
        else:
            raise Exception(f"Incorrect command format {msg}")
        setattr(self, "solver", b)
        if is_flush:
            cfg = self.get_config()
            cfg.set(symaiconfig.SymAIConfig.EXPRESSION.value,
                                  symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value, b)
            symaiconfig.create_config(symaiconfig.get_config_file(), symaiconfig.SymAIConfig.EXPRESSION.value, cfg)
        return str(b)

    def get_max_models(self)->int:
        b = 10  # default value of solver max models
        if hasattr(self, "max_models"):
            b = getattr(self, "max_models")
        else:
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value,
                                          symaiconfig.SymAIConfig.SOLVER_MAX_MODELS.value)
                if s.isnumeric():
                    b = int(s)
            except:
                b = 10
        return b

    def do_max_models(self, cuuid, msg:str):
        b = self.get_max_models()

        is_flush = False
        s = msg.strip().split()
        if len(s) == 1:
            if hasattr(self, "max_models"):
                b = getattr(self, "max_models")
        elif len(s) == 2:
            if s[1].lower() == "flush":
                is_flush = True
                try:
                    int(self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value,
                                          symaiconfig.SymAIConfig.SOLVER_MAX_MODELS.value))
                except:
                    b = 10
            else:
                try:
                    b = int(s[1])
                except:
                    raise Exception(f"Incorrect value {s[1]}")
        elif len(s) == 3:
            if s[1].lower() == "flush":
                is_flush = True
                try:
                    b = str(int(s[2]))
                except:
                    raise Exception(f"Incorrect command format {msg}")
            elif s[2].lower() == "flush":
                is_flush = True
                try:
                    b = str(int(s[1]))
                except:
                    raise Exception(f"Incorrect command format {msg}")
            else:
                raise Exception(f"Incorrect command format {msg}")
        else:
            raise Exception(f"Incorrect command format {msg}")

        setattr(self, "max_models", b)
        if is_flush:
            cfg = self.get_config()
            cfg.set(symaiconfig.SymAIConfig.EXPRESSION.value,
                                  symaiconfig.SymAIConfig.SOLVER_MAX_MODELS.value, str(b))
            symaiconfig.create_config(symaiconfig.get_config_file(), symaiconfig.SymAIConfig.EXPRESSION.value, cfg)
        return str(b)

    def get_reenter_count(self)->int:
        b = 1  # default value of reenter count
        if hasattr(self, "reenter_count"):
            b = getattr(self, "reenter_count")
        else:
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                          symaiconfig.SymAIConfig.BEHAVIORS_REENTER_COUNT.value)
                if s.isnumeric():
                    b = int(s)
            except:
                b = 1
        return b

    def do_reenter_count(self, cuuid, msg:str):
        b = self.get_reenter_count()

        is_flush = False
        s = msg.strip().split()
        if len(s) == 1:
            if hasattr(self, "reenter_count"):
                b = getattr(self, "reenter_count")
        elif len(s) == 2:
            if s[1].lower() == "flush":
                is_flush = True
                try:
                    int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                          symaiconfig.SymAIConfig.BEHAVIORS_REENTER_COUNT.value))
                except:
                    b = 1
            else:
                try:
                    b = int(s[1])
                except:
                    raise Exception(f"Incorrect value {s[1]}")
        elif len(s) == 3:
            if s[1].lower() == "flush":
                is_flush = True
                try:
                    b = str(int(s[2]))
                except:
                    raise Exception(f"Incorrect command format {msg}")
            elif s[2].lower() == "flush":
                is_flush = True
                try:
                    b = str(int(s[1]))
                except:
                    raise Exception(f"Incorrect command format {msg}")
            else:
                raise Exception(f"Incorrect command format {msg}")
        else:
            raise Exception(f"Incorrect command format {msg}")

        setattr(self, "reenter_count", b)
        if is_flush:
            cfg = self.get_config()
            cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value,
                                  symaiconfig.SymAIConfig.BEHAVIORS_REENTER_COUNT.value, str(b))
            symaiconfig.create_config(symaiconfig.get_config_file(), symaiconfig.SymAIConfig.SYMAICORE.value, cfg)
        return str(b)
