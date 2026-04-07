from collections import deque
from http import HTTPStatus

import symaicommands
import symaiconfig
import http.client
import json
import uuid
from itertools import tee
import os
from mathutils import MathUtils

from eqextractvisitor import EQExtractorVisitor
from symbolicexpressiongrammarvisitor import *
from actvisitor import *
from behvisitor import *

from enum import Enum

from treeedit import TreeEdit
from treeutils import TreeUtils

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
    def get_temp_dir(self)->str:
        s = None
        if self.get_config() is not None:
            s = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,symaiconfig.SymAIConfig.TEMP.value)
        if s is None or len(s) < 1:
            s = symaiconfig.SymAIConfig.BASE_TEMP.value

        return s

    def set_temp_dir(self, td):
        if self.get_config() is not None:
            self.config.set(symaiconfig.SymAIConfig.SYMAICORE.value,symaiconfig.SymAIConfig.TEMP.value, td)

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
        self.remove_directory_tree(os.path.join(self.get_temp_dir(),
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
            d = os.path.join(self.get_temp_dir(),
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

    def do_reset(self, cuuid, msg:str):
        s = ""
        names = ["ai", "behaviors", "debug", "inverted", "actions", "environment", "property", "trace_file", "solver", "inverted", "max_models", "reenter_count"]

        for nm in names:
            if hasattr(self, str(nm)):
                delattr(self, str(nm))

        self.remove_directory_tree(os.path.join(self.get_temp_dir(),
                                                str(cuuid)))
        return s

    def do_behaviors(self, cuuid, data_received):
        if data_received is None or len(data_received.strip()) < 1:
            res = dict()
            cnt = ""
            fname = ""
            if hasattr(self, "behaviors"):
                cnt, v = self.get_behaviors()
                fname = getattr(self, "behaviors")
            res["content"] = cnt
            fname = os.path.basename(fname)
            if len(fname) < 1:
                fname = "behaviors.beh"
            res["filename"] = fname
            res = json.dumps(res)
            self.get_logger().info(f"behaviors command processed. Retrieved behaviors list is {cnt}")
        else:
            try:
                res = json.loads(data_received)
                if "filename" not in res.keys():
                    res["filename"] = "behaviors.beh"
                    data_received = json.dumps(res)
            except Exception as e:
                self.get_logger().error(f"behaviors command processing failed {str(e)}")
                raise e
            cnt = self.do_get_file(cuuid,
                                   symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                                   data_received)
            fn = os.path.join(self.get_temp_dir(),
                              cuuid,
                              symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                              cnt["filename"])
            try:
                tree = TreeUtils.prepare_parser_beh(cnt["content"]).behaviors()
                visitor = BehGrammarVisitor()
                res = visitor.visit(tree)
                with open(fn, "w") as f:
                    f.write(res)
                self.get_logger().info(f"behaviors command processed. The behaviors list saved to {fn}")
                setattr(self, "behaviors", fn)
                res = ""
            except Exception as e:
                self.get_logger().error(f"behaviors command processing failed {str(e)}")
                try:
                    if os.path.exists(fn):
                        os.remove(fn)
                except:
                    pass
                raise e
        return res

    def get_debug(self):
        if hasattr(self, "debug"):
            fn = getattr(self, "debug")
        else:
            cfg = self.get_config()
            try:
                fn = cfg.get(symaiconfig.SymAIConfig.SYMAICORE.value,
                              symaiconfig.SymAIConfig.SYMAICORE_DEBUG.value)
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
            setattr(self,"debug", fn)

        return fn

    def invert_one_action(self, name, expr):
        tree = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
        visitor = SymbolicExpressionGrammarVisitor()
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
            tr =  TreeUtils.prepare_parser_beh(r).assignmentExpression()
            v = SymbolicExpressionGrammarVisitor()
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
                i = rs.find("=")

                # it = iter(rs)
                # inv = (next(it))
                # inv = l + "=" + rs[str(inv)]
                inv = l + "=" + rs[i+1:]
                subsn = [{"name": nm, "value": l}]
                tr = TreeUtils.prepare_parser_beh(inv).assignmentExpression()
                v = SymbolicExpressionGrammarVisitor()
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
            fn = os.path.join(self.get_temp_dir(),
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
                    if len(ra) < 2:
                        if len(ra) < 1:
                            continue
                        else:
                            t, e = TreeUtils.check_const(ra[0])
                            if t and e:
                                del ra[0]
                                continue

                    r = []
                    for s in ra:
                        if len(s) > 0:
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
        if data_received is None or len(data_received.strip()) < 1:
            cnt = ""
            fname = ""
            if hasattr(self, "actions"):
                cnt, v = self.get_actions()
                fname = getattr(self, "actions")
            rs = dict()
            rs["content"] = cnt
            fname = os.path.basename(fname)
            if len(fname) < 1:
                fname = "actions.act"
            rs["filename"] = fname
            res = json.dumps(rs)
            self.get_logger().info(f"actions command processed. Retrieved actions list is {cnt}")
        else:
            try:
                res = json.loads(data_received)
                if "filename" not in res.keys():
                    res["filename"] = "actions.act"
                    data_received = json.dumps(res)
            except Exception as e:
                self.get_logger().error(f"actions command processing failed {str(e)}")
                raise e
            cnt = self.do_get_file(cuuid,
                               symaiconfig.SymAIConfig.BASE_ACTIONS.value,
                               data_received)
            fn = os.path.join(self.get_temp_dir(),
                              cuuid,
                              symaiconfig.SymAIConfig.BASE_ACTIONS.value,
                              cnt["filename"])
            try:
                tree = TreeUtils.prepare_parser_beh(cnt["content"]).actions()
                visitor = ActGrammarVisitor()
                res = visitor.visit(tree)
                with open(fn, "w") as f:
                    f.write(res)
                setattr(self, "actions", fn)
                self.invert_actions(cuuid, visitor, fn)

                self.get_logger().info(f"actions command processed. The actions list saved to {fn}")
                res = ""
            except Exception as e:
                self.get_logger().error(f"actions command processing failed {str(e)}")
                try:
                    if os.path.exists(fn):
                        os.remove(fn)
                except:
                    pass
                delattr(self, "actions")
                raise e
        return res

    def do_environment(self, cuuid, data_received):
        if data_received is None or len(data_received.strip()) < 1:
            res = dict()
            cnt = ""
            fname = "environment.env"
            if hasattr(self, "environment"):
                cnt = self.get_environment()
                fname = getattr(self, "environment")
            res["content"] = cnt
            fname = os.path.basename(fname)
            res["filename"] = fname
            res = json.dumps(res)
            self.get_logger().info(f"environment command processed. Retrieved environment expression is {cnt}")
        else:
            try:
                res = json.loads(data_received)
                if "filename" not in res.keys():
                    res["filename"] = "environment.env"
                    data_received = json.dumps(res)
            except Exception as e:
                self.get_logger().error(f"environment command processing failed {str(e)}")
                raise e
            res = self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value)

            fn = os.path.join(self.get_temp_dir(),
                              cuuid,
                              symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value,
                              res["filename"])
            try:
                with open(fn, "w") as f:
                    f.write(res["content"])
                self.get_logger().info(f"environment command processed. The environment saved to {fn}")
                setattr(self, "environment", fn)
                res = ""
            except Exception as e:
                self.get_logger().error(f"environment command processing failed {str(e)}")
                try:
                    if os.path.exists(fn):
                        os.remove(fn)
                except:
                    pass
                raise e
        return res

    def do_property(self, cuuid, data_received):
        if data_received is None or len(data_received.strip()) < 1:
            res = dict()
            cnt = ""
            fname = "properties.prop"
            if hasattr(self, "property"):
                cnt = self.get_property()
                fname = getattr(self, "property")
            res["content"] = cnt
            fname = os.path.basename(fname)
            res["filename"] = fname
            res = json.dumps(res)
            self.get_logger().info(f"property command processed. Retrieved environment expression is {cnt}")
        else:
            try:
                res = json.loads(data_received)
                if "filename" not in res.keys():
                    res["filename"] = "properties.prop"
                    data_received = json.dumps(res)
            except Exception as e:
                self.get_logger().error(f"property command processing failed {str(e)}")
                raise e
            res = self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_PROPERTIES.value)

            fn = os.path.join(self.get_temp_dir(),
                              cuuid,
                              symaiconfig.SymAIConfig.BASE_PROPERTIES.value,
                              res["filename"])
            try:
                with open(fn, "w") as f:
                    f.write(res["content"])
                self.get_logger().info(f"property command processed. The property saved to {fn}")
                setattr(self, "property", fn)
                res = ""
            except Exception as e:
                self.get_logger().error(f"property command processing failed {str(e)}")
                try:
                    if os.path.exists(fn):
                        os.remove(fn)
                except:
                    pass
                raise e
        return res

    def get_behaviors(self):
        if hasattr(self, "behaviors"):
            fn = getattr(self, "behaviors")
            try:
                f = open(fn, "r")
                cnt = f.read()
                p = TreeUtils.prepare_parser_beh(cnt)
                tree = p.behaviors()
                visitor = BehGrammarVisitor()
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
                tree = TreeUtils.prepare_parser_beh(cnt).actions()
                visitor = ActGrammarVisitor()
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
                tree = TreeUtils.prepare_parser_beh(cnt).expression()
                visitor = SymbolicExpressionGrammarVisitor()
                res = visitor.visit(tree).replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace(
                    "__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" ")
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
                tree = TreeUtils.prepare_parser_beh(cnt).expression()
                visitor = BehGrammarVisitor()
                cnt = visitor.visit(tree)
                # tree = TreeUtils.prepare_parser_beh(s).expression()
                # res = visitor.visit(tree).replace("&", "&&").replace("|", "||").replace("_d_o_t_", ".").replace("__d__o__t__", "_d_o_t_").replace(" not ", "!").replace(" _n_o_t_ ", " not ").strip(" ")
                self.get_logger().debug(f"environment successful retrieved. File {fn}")
                res = cnt
                cvals, vals, en = TreeUtils.get_vars_using_assignment(cnt)
                if len(cvals) > 0 and len(vals) > 0 and len(en) == 0:
                    gvals = MathUtils.fill_gvars_func()
                    is_changed = True
                    while is_changed:
                        is_changed = False
                        to_del = []
                        for it in vals.keys():
                            st = vals[str(it)]
                            if len(st) > 0:
                                try:
                                    r = eval(st, gvals, cvals)
                                    k = str(it)
                                    to_del.append(k)
                                    cvals[k] = r
                                    is_changed = True
                                except Exception as e:
                                    s = st
                        for it in to_del:
                            vals.pop(str(it))
                    if en is None:
                        en = ""
                    for it in cvals.keys():
                        if len(en) > 0:
                            en = en + " && "
                        en = en + str(it) + " == " + str(cvals[str(it)])
                    for it in vals.keys():
                        if len(en) > 0:
                            en = en + " && "
                        en = en + str(it) + " == " + str(vals[str(it)])

                    res = en
            except Exception as e:
                self.get_logger().error(f"retrieving environment failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve environment")
            return res
        raise Exception("No environments were defined")

    def check_reachability(self, env:str, reach_property:str):

        if reach_property is None or len(reach_property) < 0:
            reach_property = "True"
        if env is None:
            env = ""
        self.get_logger().debug(f"check_reachability started env is {env} reach_property is {reach_property}")
        expr, ic, r = self.prepare_condition(env)
        self.get_logger().debug("Here expr is " + expr)
        tr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
        v = EQExtractorVisitor()
        tail = v.visit(tr)
        cvals = v.getCVals()
        vals = v.getVals()
        if len(vals) > 0:
            gvars = MathUtils.fill_gvars_func()
            cv = dict()
            for idx in cvals:
                _, cv[idx] = TreeUtils.get_float(cvals[idx])
            b = True
            while b:
                b = False
                td = ""
                for i in vals:
                    try:
                        s = eval(vals[i], gvars, cv)
                        td = i
                        cv[i] = s
                        b = True
                    except:
                        pass
                    if b:
                        break
                try:
                    vals.pop(td)
                except:
                    pass
            #res, r_env
            r_env = ""
            for i in cv:
                if len(r_env) > 0:
                    r_env = r_env + "&&"
                r_env = r_env + str(i) + "==" + str(cv[i])
            for i in vals:
                if len(r_env) > 0:
                    r_env = r_env + "&&"
                r_env = r_env + str(i) + "==" + str(vals[i])
            if len(tail) > 0:
                if len(r_env) > 0:
                    r_env = r_env + "&&"
                r_env =r_env + str(tail)
            # Here we should reinterpret the reach_property and return true or false or contivue of executing
            if len(vals) <= 0:
                # Here we should reinterpret the reach_property and return true or false
                res = True
                s, ic, r = self.prepare_condition(reach_property)
                s = s.replace("&&"," and ").replace("||"," or ")
                b = False
                try:
                    res = eval(s, gvars, cv)
                    b = True
                except:
                    pass
                if b:
                    return res, r_env
            expr = r_env
        # SyntaxError: Raised if the provided string is not a valid Python expression (e.g., mismatched parentheses, or trying to use a statement like if or variable assignment =).
        # NameError: Raised if the expression refers to a variable, function, or class name that is not defined in the available scope.
        # TypeError: Raised when an operation is performed on a value of an inappropriate type (e.g., trying to divide a list by an integer).
        # ValueError: Raised when a function within the evaluated expression receives an invalid value, even if the argument type is correct (e.g., a math function receiving an input outside its domain).
        # ZeroDivisionError: Raised if the expression attempts division by zero.
        # KeyError or IndexError: Can be raised if the expression attempts to access a non-existent key in a dictionary or an invalid index in a sequence.
        #
        if v.isTrigonometric() or v.isNonLinear():
            # trying to process it as an exact expression. Otherwise return an error
            raise Exception("Non-linear functions are not allowed for symbolic calculation of the environment expression '" + env + "'")
        if reach_property is not None and len(reach_property) > 0:
            s, ic, r = self.prepare_condition(reach_property)
            if len(s) > 0:
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
            rsp = response.read()
            rsp = rsp.decode()
            rsp = json.loads(rsp)
            r_env = rsp["formula"]
            self.get_logger().info(f"check_reachability ( {env}, {reach_property} ) command processed with {res}.")
        except Exception as e:
            self.get_logger().error(f"check_reachability ( {env}, {reach_property} ) command processing failed {str(e)}")
            raise e

        return res, r_env

    def prepare_condition(self, cnd:str):
        p =  TreeUtils.prepare_parser_beh(cnd)
        tree = p.assignmentExpression()
        v = SymbolicExpressionGrammarVisitor()
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
                    t = float(str(s))
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

        glob_vars = dict()
        int_vars = dict()
        res_vars = dict()
        if subst is not None:
            for it in subst:
                int_vars[it] = float(subst[it])
                res_vars[it] = float(subst[it])

        for fml in expr:
            if fml != "1":
                s = fml.split("=")
                exec(fml, glob_vars, int_vars)
                res_vars[s[0].strip()] = int_vars[s[0].strip()]
                if subst is not None:
                    int_vars = dict()
                    for it in subst:
                        int_vars[it] = float(subst[it])

        for v in res_vars.keys():
            int_vars[v] = res_vars[v]

        i = False
        env_exp  = ""
        for it in int_vars:
            if i:
                env_exp = env_exp + " && "
            env_exp = env_exp + "(" + str(it) + " == " +  str(int_vars[it]) + ")"
            i = True

        return env_exp

    def negate_relational_expr(self, expr: str)->str :
        tr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
        tokens = TreeEdit.find_all_by_tokens(tr, ["<", ">", "=", "!=", "==", ">=", "<="])
        for it in tokens:
            s = it.getText()
            match s:
                case "<": s = ">"
                case "<=": s = ">="
                case ">": s = "<"
                case ">=": s = "<="
                case default: s = s
            it.symbol.text = s

        v = SymbolicExpressionGrammarVisitor()
        s = v.visit(tr)
        tr = TreeUtils.prepare_parser_beh(s).assignmentExpression()
        v = SymbolicExpressionGrammarVisitor()
        res = v.visit(tr).replace("&", "&&").replace("|", "||")

        return res

    '''
    Removes all variables included into vals vars list from expr expression
    '''
    def do_remove_vars(self, expr, vals):
        is_cnt = True
        while is_cnt:
            is_cnt = False
            if vals is None or len(vals) < 1 or expr is None or len(expr) < 1:
                expr = ""
                break
            etr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
            tokens = TreeEdit.find_all_by_tokens(etr, ["<", ">", "=", "!=", "==", ">=", "<="])
            it = 0
            while it < len(tokens):
                v = SymbolicExpressionGrammarVisitor()
                v.visit(tokens[it].parentCtx)
                vrs = v.var_list
                b = False
                if len(vrs) > 0:
                    for vn in vals:
                        if b:
                            break
                        for j in vrs:
                            if vn == j:
                                b = True
                                break
                    if b:
                        # parent node of node it must be removed from tree
                        p = tokens[it].parentCtx
                        l = p.getChildCount()
                        if l == 3:
                            while p.getChildCount() > 0:
                                p.children[0].parentCtx = None
                                del p.children[0]
                            TreeEdit.delete_node(p)
                            is_cnt = True
                        else:
                            i = 1
                            while i < l:
                                if p.getChild(i) == tokens[it]:
                                    is_cnt = True
                                    TreeEdit.delete_node(tokens[it])
                                    q = p.getChild(i)
                                    TreeEdit.delete_node(q)
                                    if i == 1:
                                        q = p.getChild(0)
                                        TreeEdit.delete_node(q)
                                    if p.getChildCount() == 0:
                                        TreeEdit.delete_node(p)
                                    break
                if is_cnt:
                    break
                it = it + 1
            v = SymbolicExpressionGrammarVisitor()
            expr = v.visit(etr).replace("&", "&&").replace("|", "||")
            if expr is None:
                expr = ""
            else:
                if len(expr) < 1:
                    expr = ""
                    break
                etr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
                expr = v.visit(etr).replace("&", "&&").replace("|", "||")

        return expr

    def do_replace(self, to_replace : str, subst = None):
        res = to_replace
        if res is None:
            res = ""
        if subst is not None and len(res) > 0:
            tr = TreeUtils.prepare_parser_beh(res).assignmentExpression()
            v = SymbolicExpressionGrammarVisitor()
            if subst is not None:
                v.setSubstitution(subst)
            s = v.visit(tr)
            tr = TreeUtils.prepare_parser_beh(s).assignmentExpression()
            v = SymbolicExpressionGrammarVisitor()
            res = v.visit(tr).replace("&", "&&").replace("|", "||")
        return res

    def do_replace_and_simplify(self, to_simplify: str, subst = None) -> str:
        if to_simplify is None or len(to_simplify) < 1:
            return ""
        fml = self.do_replace(to_simplify, subst)
        ic, vl = TreeUtils.check_const(fml)
        if ic:
            fml = str(vl)
        elif fml != "":
            headers = {'Content-type': 'application/json'}
            try:
                # Make an HTTP request for check
                expression_host = str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                            symaiconfig.SymAIConfig.EXPRESSION_HOST.value))
                expression_port = int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                            symaiconfig.SymAIConfig.EXPRESSION_PORT.value))
                # Make an HTTP request for simplifying expression
                conn = http.client.HTTPConnection(expression_host, expression_port)
                query = dict()
                slvr = self.get_solver()
                query["solver"] = slvr
                query["formula"] = fml
                conn.request('POST', '/api/v1/expression/simplify', json.dumps(query), headers)
                response = conn.getresponse()
                if not (response.getcode() == HTTPStatus.OK):
                    raise Exception(
                        f"Attempt to recalculate environment error {str(conn.getresponse())} {response.reason}")
                rsp = json.loads(response.read().decode())
                fml = rsp["formula"]
            except Exception as e:
                self.get_logger().error(f"do_simplify({to_simplify})  method processing failed {str(e)}")
                raise e

        return fml

    def do_inverse(self, expr:str, v :str = None) -> str:
        nexpr = expr
        res = v
        if v is None:
            i = expr.strip().find("=")
            if i == -1:
                if expr != "1":
                    raise Exception(f"Incorrect expression {expr} for inverse ")
                else:
                    l = expr[:i].strip()
                    res = l
                    r = expr[i + 1:].strip()
                    tr = TreeUtils.prepare_parser_beh(r).assignmentExpression()
                    v = SymbolicExpressionGrammarVisitor()
                    v.visit(tr)
                    vl = v.getVarList()
                    if l in vl:
                        i = 0
                        nm = l + str(i)
                        while nm in vl:
                            i = i + 1
                            nm = l + str(i)
                        nexpr = nm + "=" + r

        headers = {'Content-type': 'application/json'}
        # Make an HTTP request to inverse equation
        expression_host = str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                    symaiconfig.SymAIConfig.EXPRESSION_HOST.value))
        expression_port = int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                    symaiconfig.SymAIConfig.EXPRESSION_PORT.value))
        conn = http.client.HTTPConnection(expression_host, expression_port)
        query = dict()
        query["formula"] = nexpr
        if res is not None:
            query["target"] = res
        slvr = self.get_solver()
        query["solver"] = slvr
        conn.request('POST', '/api/v1/expression/inverse', json.dumps(query), headers)
        response = conn.getresponse()
        if not (response.getcode() == HTTPStatus.OK):
            raise Exception(f"Attempt to inverse expression error {str(conn.getresponse())}")
        rsp = json.loads(response.read().decode())
        rs = rsp["inverse"]
        return rs

    def prep_replacement(self, cvals):
        cvals_rpl = []
        for n in cvals.keys():
            cvals_rpl.append({"name": n, "value": str(cvals[n])})
        return cvals_rpl

    def do_sm_subst_step(self, env, expr, cnd):
        if expr is not None and expr == "1":
            return env

        left = ""
        right = ""
        s = expr.split("=")
        if len(s) > 1:
            left = s[0]
            right = s[1]
        is_add = False
        cvals, vals, en = TreeUtils.get_vars_using_assignment(env)
        if en is None or len(en) < 1:
            # Going with concrete values, e is a resulting env
            b = True
            for it in vals.keys():
                ret, t = TreeUtils.check_const(vals[str(it)])
                if not ret:
                    b = False
                    break
            if b:
                cv = dict()
                lvars = dict()
                b = False
                for it in cvals.keys():
                    lvars[str(it)] = cvals[str(it)]
                    cv[str(it)] = cvals[str(it)]
                    if str(it) == left:
                        b = True
                gvars = MathUtils.fill_gvars_func()
                try:
                    cv[left] = eval(right,  gvars, cv)
                except NameError as e:
                    self.get_logger().error(f"traversalbeh expr {expr} env {env} cnd {cnd} NameError error {e}" )
                    raise e
                except TypeError as e:
                    self.get_logger().error(f"traversalbeh TypeError error {e}")
                    raise e
                except ValueError as e:
                    self.get_logger().error(f"traversalbeh ValueError error {e}")
                    raise e
                except ZeroDivisionError as e:
                    self.get_logger().error(f"traversalbeh ZeroDivisionError error {e}")
                    raise e
                e = ""
                if not b:
                    e = left + " == " + right
                for it in cv:
                    if len(e) > 0:
                        e = e + " && "
                    e = e + str(it) + " == " + str(cv[str(it)])
                return e
        tr = TreeUtils.prepare_parser_beh(right).assignmentExpression()
        v = SymbolicExpressionGrammarVisitor()
        s = v.visit(tr)
        vl = v.getVarList()
        if not left in vl:
            is_add = True
        if len(expr) > 0:
            tr = TreeUtils.prepare_parser_beh(expr).assignmentExpression()
            v = SymbolicExpressionGrammarVisitor()
            s = v.visit(tr)
            vl = v.getVarList()
        if len(expr) < 1 or not left in vl:
            is_add = True

        pref = ""
        cv = cvals
        if left in cvals.keys():
            cv = dict()
            if len(cvals.keys()) == 1:
                pref = cnd
            else:
                for it in cvals.keys():
                    if it != left:
                        cv[it] = cvals[it]

        # Doing inversions in vals, if any
        vl = dict()
        for k in vals.keys():
            # 1. Inversion by left, if any is possible
            tr = TreeUtils.prepare_parser_beh(k + "=" + vals[k]).assignmentExpression()
            v = SymbolicExpressionGrammarVisitor()
            v.visit(tr)
            vls = v.getVarList()
            if left in vls:
                s = self.do_inverse(k + "=" + vals[k], left)
                i = s.find("=")
                vl[left] = s[i + 1:]
            else:
                vl[k] = vals[k]
            # 2. Replacements by vl and then by cl, if any available
            if len(en) > 0:
                sen_rpl = self.prep_replacement(vl)
                sen = self.do_replace(en, sen_rpl)
                sen_rpl = self.prep_replacement(cv)
                sen = self.do_replace(sen, sen_rpl)
                # 3. replacements in en and check new en, if sat
                should_remove, sen = self.check_reachability(sen, "")
                should_remove = not should_remove
                if not should_remove:
                    en = sen
                else:
                    # 4. Remove left vars if new en is not sat and is not empty
                    rmv = [left]
                    st = en
                    en = self.do_remove_vars(st, rmv)

#        if len(pref) > 0:
#            pref = pref + " && "

        if is_add:
            sen_rpl = self.prep_replacement(vl)
            sen = self.do_replace(right, sen_rpl)
            sen_rpl = self.prep_replacement(cv)
            right = self.do_replace(sen, sen_rpl)
            pref = pref + left + " == " + right

        #
        for it in cv.keys():
            if len(en) > 0:
                en = en + " && "
            en = en + it + " == " + str(cv[it])
        if len(pref) > 0:
            if len(en) > 0:
                en = en + " && "

            env = en + pref

        env = self.do_replace_and_simplify(env)

        return env

    def do_sm_substitution(self, env, expr, cnd):

       # Next 2 lines are going to be removed
       cvals, vals, en = TreeUtils.get_vars_using_assignment(env)
       is_const = True

       num_expr = len(expr)
       pf = ""
       if num_expr > 0:
           pe = TreeUtils.prepare_parser_beh(expr[-1])
           ev = ActGrammarVisitor()
           has_log = ev.action_has_logical(pe.assignmentExpressionList())

           if has_log:
               s = pe.assignmentExpressionList()[num_expr - 1]
               if s == "1":
                   s = "True"
               if len(expr) > 1 and len(s) > 0:
                   pf = s + " && "
               num_expr = num_expr - 1

           i = 0
           while i < num_expr:
               env = self.do_sm_subst_step(env, expr[i], pf + cnd)
               i = i + 1

       for it in vals.keys():
           vals[it] = str(vals[it])
       return env, is_const, vals

    def step_modelling(self, ctx, act):
        act_visitor = ctx["act_visitor"]
        cnd = ""
        a = act_visitor.getResults()
        for r in a:
            if r[0] == act:
                cnd = str(r[1])
                pe = TreeUtils.prepare_parser_beh(r[2])
                ev = ActGrammarVisitor()
                if ev.action_has_logical(pe.assignmentExpressionList()):
                    st = r[2].split(";")
                    lg = st[-1]
                    if len(lg) == 1 and lg == "1":
                        return ctx, True
                    if len(lg) > 0:
                        ret, tt = TreeUtils.check_const(lg)
                        if ret and tt:
                           cnd = cnd
                        elif len(cnd) > 0:
                            cnd = "(" + lg + ") && (" + cnd + ")"
                        else:
                            cnd = lg
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
            if act in ctx["inverted_actions"].keys():
                expr = ctx["inverted_actions"][act]
            else:
                expr = []
            ctx["environment"], is_const, variables = self.do_sm_substitution(ctx["environment"], expr, cnd)

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
        if not hasattr(self, "trace_file"):
            ctx["trace_file"] = (os.path.splitext(getattr(self, "behaviors"))[0]) + ".trx"

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
                    fn = os.path.join( self.get_temp_dir(),
                                       ctx["cuuid"],
                                       symaiconfig.SymAIConfig.BASE_TRACE.value,
                                       symaiconfig.SymAIConfig.BASE_TRACE_FILE.value)
                ctx["trace_file"] = fn
                if type(ctx["trace"]) == "<class 'str'>":
                    ctx["trace"] = str(self.dump_trace(trace))
                if type(ctx["environment_trace"]) == "<class 'str'>":
                    ctx["environment_trace"] = str(self.dump_trace(env_trace))
                with open(fn, "w") as f:
                    f.write(str(self.dump_trace(trace)) + "\n" + str(self.dump_trace(env_trace)) + "\n")
            else:
                fn = ctx["trace_file"]
                if type(ctx["trace"]) == "<class 'str'>":
                    ctx["trace"] = ctx["trace"] + "\n" + str(self.dump_trace(trace))
                if type(ctx["environment_trace"]) == "<class 'str'>":
                    ctx["environment_trace"] = ctx["environment_trace"] + "\n" + str(self.dump_trace(env_trace))

                with open(fn, "a+") as f:
                    f.write(str(self.dump_trace(trace)) + "\n" + str(self.dump_trace(env_trace)) +"\n")

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

    def dump_concrete_trace(self, trace)->str:
        res = "["
        b = False
        for it in trace:
            if b:
                res = res + ","
            cvals, vals, ret = TreeUtils.get_vars_using_assignment(str(it))
            res = res + "["
            b1 = False
            if cvals is not None:
                for i in cvals.keys():
                    if b1:
                        res = res + ","
                    res = res + '{"' + i + '":' + str(cvals[i]) + '}'
                    b1 = True
            res = res + "]"
            b = True
        res = res + "]"

        return res

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
            b = True
            if data_received is not None:
                s = data_received.strip()
                if len(s) > 0 and s != "remove":
                    raise Exception(f"Incorrect trace command parameter {data_received}")
                else:
                    if s == "remove" and hasattr(self, "trace_file"):
                        path = getattr(self, "trace_file")
                        if path is not None:
                            if os.path.isfile(path):
                                self.get_logger().debug(f"Deleting the '{path}' file.")
                                os.remove(path)
                            setattr(self, "trace_file", None)
                        b = False
            if b and hasattr(self, "trace_file"):
                r = ""
                fn = getattr(self, "trace_file")
                try:
                    if fn is not None and len(fn.strip()) > 0:
                        f = open(fn, "r")
                        r = f.read()
                except:
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
            with open(os.path.join(self.get_temp_dir(),
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

    def get_ai(self):
        msg = ""
        b = False
        if hasattr(self, "ai"):
            b = getattr(self, "ai")
        else:
            try:
                msg = self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.AI.value)
                if msg is not None:
                    if msg.lower() == "true" or msg.lower() == "yes" or msg.lower() == "1":
                        b = True
                msg = ""
                setattr(self, "ai", b)
            except Exception as e:
                msg = str(e)
        return b, msg

    def do_ai(self, cuuid, msg:str):
        b, s = self.get_ai()
        if s != "":
            raise Exception(s)

        s = str(msg).strip().split()
        if len(s) < 1:
            if not hasattr(self, "ai"):
                setattr(self, "ai", b)
            return str(b)
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

    def parse_traversalbeh_data(self, cuuid, data_received, ctx):
        if "behaviors" not in ctx or len(ctx["behaviors"]) <= 0:
            raise Exception("No behaviors were defined")
        behaviors = ctx["beh_visitor"].getBehaviors()
        beh = None
        slvr = self.get_solver()

        if data_received is not None and len(data_received) > 0:
            try:
                dr = json.loads(data_received.replace("'", '"'))
            except Exception as e:
                self.get_logger().error(f"Incorrect input `{data_received}` JSON data {str(e)}`")
                raise Exception(f"Incorrect input `{data_received}` JSON data {str(e)}`")
            if "behavior" in dr:
                beh = dr["behavior"]
                if dr["behavior"] not in behaviors.keys():
                    raise Exception(f"Incorrect behavior {beh}")
            if "solver" in dr:
                if type(dr["solver"]) != str:
                    raise Exception("Incorrect solver name")
                if dr["solver"] in symaiconfig.SymAISolvers._value2member_map_:
                    setattr(self, "solver", dr["solver"])
                else:
                    raise Exception("Incorrect solver name '" + dr["solver"] + "'")
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
                                fn = False
                        except:
                            fn = False
                except:
                    fn = False

                setattr(self, "debug", fn)
        if beh is None:
            beh = next(iter(behaviors))
        return ctx, beh, slvr

    def do_traversalbeh(self, cuuid, data_received):
        yield "ok start traversal behaviors"
        self.get_logger().info(f"traversal behaviors started {data_received}")
        try:
            ctx = self.do_load_traversal_data(cuuid, data_received)
            yield "ok input data retrieved"
            # Processing
            self.get_logger().debug(f"traversal behaviors input data retrieved")
            behaviors = ctx["beh_visitor"].getBehaviors()
            actions = ctx["act_visitor"].getResults()

            # Parsing incoming data
            ctx, cur_beh, slvr = self.parse_traversalbeh_data(cuuid, data_received, ctx)

            yield "ok trace start"
            env_trace = deque([])
            trace = deque([])

            # Selecting an appropriate behavior to process.
            # AI can be used here for initial cur_beh selection
            # Now choosing the first behavior by default
            trace.append(cur_beh)
            env_trace.append(ctx["environment"])

            # Setting up start trace values and context
            ctx["trace"] = trace
            ctx["environment_trace"] = env_trace

            setattr(self, "stop", False)

            for s in self.process_one_behavior(behaviors[cur_beh], ctx, None):
                yield s

            # Finalizing
            yield "ok trace end"
            yield "ok end traversal behaviors"
            self.get_logger().info("traversal behaviors finished")
        except Exception as e:
            self.get_logger().error(f"traversal behaviors failed with {e}")
            yield f"nok Traversal behaviors failed {e}"

    def process_one_behavior(self, beh, ctx, it_tail):
        environment = ctx["environment"]
        prop = ctx["property"]
        trace = ctx["trace"].copy()
        env_trace = ctx["environment_trace"].copy()
        behaviors = ctx["beh_visitor"].getBehaviors()
        actions = ctx["act_visitor"].getResults()
        tail = []
        if not (it_tail is None):
            it_tail, it = tee(it_tail)
            while True:
                try:
                    term = next(it)
                    tail.append(term)
                except StopIteration:
                    # Now we are breaking here. But we should somehow process all alternatives
                    break
        # Split behavior to set of alternates
        alts = []
        sentence = []
        cnt_b = 0
        for term in beh:
            match term:
                case "+":
                    if cnt_b == 0:
                        # Append tail to sentence here!!!
                        sentence = sentence + tail
                        alts.append(sentence)
                        sentence = []
                        continue
                    sentence.append(term)
                case "(":
                    cnt_b = cnt_b + 1
                    sentence.append(term)
                case ")":
                    if cnt_b > 0:
                        cnt_b = cnt_b - 1
                    sentence.append(term)
                case default:
                    sentence.append(term)
        if len(sentence) > 0:
            # Append tail to sentence here!!!
            sentence = sentence + tail
            alts.append(sentence)

        # Process each behavior alternate and make trace
        for a_beh in alts:
            sentence = []
            state = 0
            cnt_b = 0
            i = iter(a_beh)
            ctx["trace"] = trace.copy()
            ctx["environment_trace"] = env_trace.copy()
            ctx["environment"] = env_trace[-1]
            term = ""
            while True:
                try:
                    if state == 2:
                        tr = ctx["trace"].copy()
                        env_tr = ctx["environment_trace"].copy()
                        tr.append(term)
                        env_tr.append(ctx["environment"])

                        if tr.count(term) > ctx["reenter_count"] > 0:
                            tr.append("REENTERED")
                            env_tr.append(ctx["environment"])
                            # Well. We're visited this {term} term more than expected number of times
                        else:
                            ctx["trace"] = tr.copy()
                            ctx["environment_trace"] = env_tr.copy()
                            ctx["environment"] = env_tr[-1]
                            for s in self.process_one_behavior(sentence, ctx, i):
                                yield s
                        ctx["trace"] = tr.copy()
                        ctx["environment_trace"] = env_tr.copy()
                        ctx["environment"] = env_tr[-1]
                        state = 0
                    term = next(i)
                    if getattr(self, "stop"):
                        break
                    if state == 1:
                        # "(" was found previously
                        if term == ")":
                            if cnt_b > 0:
                                cnt_b = cnt_b - 1
                            else:
                                state = 2
                        elif term == "(":
                            cnt_b = cnt_b + 1
                        if state != 2:
                            sentence.append(term)
                        else:
                            term = "("
                            for s in sentence:
                                term = term + s
                            term = term + ")"
                    else:
                        match term:
                            case "(":
                                state = 1
                                cnt_b = 0
                                # Behaviors processing would be here
                                continue
                            case "+":
                                # Here should be a trace rollback
                                ctx["trace"] = trace.copy()
                                ctx["environment_trace"] = env_trace.copy()
                                ctx["environment"] = env_trace[-1]
                                continue
                            case ".":
                                continue
                            case default:
                                if self.is_action(actions, term):
                                    ctx, is_sat = self.step_modelling(ctx, term)
                                    if is_sat:
                                        tr = ctx["trace"].copy()
                                        env_tr = ctx["environment_trace"].copy()
                                        tr.append(term)
                                        env_tr.append(ctx["environment"])
                                        res, ctx["environment"] = self.check_reachability(ctx["environment"], ctx["property"])
                                        if res:
                                            is_reached = True
                                            try:
                                                idx = tr.index("REACHED")
                                                del tr[idx]
                                                del env_tr[idx]
                                            except ValueError:
                                                pass
                                            tr.append("REACHED")
                                            env_tr.append(ctx["environment"])
                                        else:
                                            is_reached = False
                                        yield f"ok trace {self.dump_trace(tr)}"
                                        yield f"ok environment {self.dump_trace(env_tr)}"
                                        yield f"ok values {self.dump_concrete_trace(env_tr)}"
                                        ctx = self.append_trace(ctx, tr, env_tr)
                                        ctx["trace"] = tr.copy()
                                        ctx["environment_trace"] = env_tr.copy()
                                        ctx["environment"] = env_tr[-1]
                                    else:
                                        break
                                else :
                                    sentence = self.find_behavior(behaviors, term)
                                    if sentence is not None:
                                        state = 2
                                    else:
                                        raise Exception(f"Unknown term {term}")
                except StopIteration:
                    # Now we are breaking here. But we should somehow process all alternatives
                    break

