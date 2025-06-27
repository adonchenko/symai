from http import HTTPStatus

import symaicommands
import symaiconfig
import http.client
import json
import uuid
import os

import re

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from extsegammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

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

    """ Loads and saves file
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

    def do_precondition(self, cuuid, data_received):
        self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_PRECONDITION.value)

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
            self.get_logger().info(f"behaviors command processed. The behaviors saved to {fn}")
            setattr(self, "behaviors", fn)
        except Exception as e:
            self.get_logger().error(f"behaviors command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
            raise e

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
            self.get_logger().info(f"actions command processed. The actions list saved to {fn}")
            setattr(self, "actions", fn)
        except Exception as e:
            self.get_logger().error(f"actions command processing failed {str(e)}")
            try:
                if os.path.exists(fn):
                    os.remove(fn)
            except:
                pass
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
                tree = self.prepare_parser_expr(cnt).behaviorsList()
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
                res = visitor.visit(tree)
                self.get_logger().debug(f"environment successful retrieved. File {fn}")
            except Exception as e:
                self.get_logger().error(f"retrieving environment failed {str(e)} file {fn}")
                raise Exception(f"Cannot retrieve environment")
            return res
        raise Exception("No environments were defined")

    def check_reachability(self, env:str, reach_property:str) -> (bool, str):

        if reach_property is None:
            reach_property = "True"
        if env is None:
            env = ""

        expr = "(" + env + ") && (" + reach_property + ")"

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
            query["formula"] = env
            conn = http.client.HTTPConnection(expression_host,expression_port)
            conn.request('POST', '/api/v1/expression/simplify', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt simplify expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            r_env = rsp["formula"]
            self.get_logger().info(f"check_reachability ( {env}, {reach_property} command processed with {res}.")
        except Exception as e:
            self.get_logger().error(f"check_reachability ( {env}, {reach_property} command processing failed {str(e)}")
            raise e

        return res, r_env

    

    def remove_actions(self, tr, INCLUDE):
        # видалити останній ланцюжок інструкцій в трасі включно чи без поведінки
        while (tr[len(tr) - 1][0] != 'B'):
            tr.pop()
        if INCLUDE > 0:
            tr.pop()
        return tr

    def load_terminal(self, b, bList):
        tt = ""
        # Завантажити поведінкове рівняння
        for equality in bList:
            tt = re.findall(r"(\+*\w+)\((.*?)\)", equality)
            if tt[0][1] == str(b):
                break
        return tt

    def step_modelling(self, x,y, inp_env,a):
        env = inp_env
        print(f"x: {x} y {y} env {inp_env} a {a}")
        return env

    def do_traversalbeh(self, cuuid, data_received):
        # behavior_content, env, actions_content, reach_property
        # 1. Loading parameters, if any incoming were saved. Throwing an exception in case of error
        beh, beh_visitor = self.get_behaviors()
        print(f"Behaviors {beh}")
        act, act_visitor = self.get_actions()
        actions = act_visitor.getResults()
        print(f"Actions: {act} Whole list {actions}")
        prop = self.get_property()
        print(f"Properties {prop}")
        env = self.get_environment()
        print(f"Environment {env}")

        trace = [['B', '0']]
        beh_stack = []

        terminal = re.findall(r"(\+*\w+)\((.*?)\)", beh)
        equations = re.findall(r"\s*([^,]+?)\s*(?=,|$)", beh)
        # завантажити всі термінали - поведінки та інструкцій - з першого рівняння
        # як список пар - мнемоніка інструкції або В та параметр - адреса в сегменті коду
        curBeh = terminal[0][1]
        # поточна поведінка, вибрана як початок обходу
        curPos = 1
        # встановлює початкову позицію терміналу
        # перший в правій частині рівняння - другий у списку
        beh_stack.append([curBeh, curPos])
        # В стек поміщаємо поточну поведінку, як пару, що містить параметр поточної поведінки
        # поточний термінал в поведінці та лічильник дій в поведінці
        stackLen = 1
        # довжина стеку

        print("Before while")
        while stackLen > 0:  # поки стек не порожній обходимо поведінку
            print(f"Pass {curBeh}")
            if curPos >= len(terminal):
                # якщо термінал останній в поведінці
                self.remove_actions(trace, 1)
                # видалити останній ланцюжок дій в трасі включно із поведінкою

                stackLen -= 1
                beh_stack.pop()
                if stackLen > 0:
                    # повертаємось назад по стеку
                    curBeh = beh_stack[stackLen - 1][0]
                    curPos = beh_stack[stackLen - 1][1]
                    equations = list()
                    actions.append(beh)
                    terminal = self.load_terminal(curBeh, equations)
                    # завантажити список терміналів поведінки curBeh
                elif (str(terminal[curPos][0]))[0] == 'B':
                    # якщо наступний термінал є поведінка
                    curBeh = terminal[curPos][1]
                    beh_stack[stackLen - 1][1] = curPos + 1
                    # зберігаємо номер терміналу в стеку
                    stackLen += 1
                    beh_stack.append([curBeh, 1])
                    trace.append(['B', curBeh])

                    # в стек додаємо нову поведінку
                    terminal = self.load_terminal(curBeh, equations)

                    # завантажуємо нове рівняння поведінок (список терміналів)
                    curPos = 1
                else:  # якщо наступний термінал дія

                    if (str(terminal[curPos][0]))[0] == '+':
                        # якщо наступний термінал є альтернатива після +
                        trace = self.remove_actions(trace, 0)

                        env = self.step_modelling(terminal[curPos][0], terminal[curPos][1], env, actions)

                        # моделювання дії

                trace.append([terminal[curPos][0], terminal[curPos][1]])
                """
                if checkReachability(env, prop):
                    print("REACHED:" + str(trace))
                    return

                if visited(terminal[curPos][0], terminal[curPos][1], trace):
                    if check_visited():
                        curPos = nextAlt(curPos, terminal, trace)
                        print("Visited state")
                    else:
                        curPos += 1
                else:
                    curPos += 1
                """
            curPos += 1

            beh_stack[stackLen - 1][1] = curPos
        return trace

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

    def do_symbolic_modelling_step(self, cuuid, environment, precondition, postcondition, prop):
        fml = ""
        if environment is not None and len(environment.strip()) > 0:
            if precondition is None or len(precondition.strip() <= 0):
                fml = environment
            else:
                fml = "(" + environment.strip() + ") && (" + precondition.strip() + "0"
        self.do_calc_formula(fml)
        self.do_calc_formula(prop)

    def do_calc_formula(self, fml):
        attr = dict()
        if hasattr(self, "solver"):
            b = getattr(self, "solver")
        else:
            b = symaiconfig.SymAISolvers.SYMPY.value
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value)
                if s in symaiconfig.SymAISolvers._value2member_map_:
                    b = s
            except:
                b = symaiconfig.SymAISolvers.SYMPY.value
        setattr(self, "solver", b)
        attr["solver"] = b
        attr["formula"] = fml
        

        return