from http import HTTPStatus

import symaicommands
import symaiconfig
import http.client
import json
import uuid
import os

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from extsegammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser

class SymAICoreParam:

    def __init__(self):
        self.session_uuid = uuid.uuid4()

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

    def do_behaviors(self, cuuid, data_received):
        self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_BEHAVIORS.value)

    def get_behaviors(self, cuuid, data_received):
        # Loading
        cnt = self.do_get_file(cuuid,
                               symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                               data_received)
        try:
            lexer = ExpressionGrammarLexer(InputStream(cnt))
            errorListener = SymbolicExpressionGrammarErrorListener()
            lexer.removeErrorListeners()
            lexer.addErrorListener(errorListener)
            stream = CommonTokenStream(lexer)
            parser = ExpressionGrammarParser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(errorListener)

            tree = parser.expressionList()

            visitor = ExtSEGrammarVisitor()
            res = visitor.visit(tree)
            with open(os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                        cuuid,
                        symaiconfig.SymAIConfig.BASE_BEHAVIORS.value,
                        cnt["filename"]), "w") as f:
                f.write(res)
            self.get_logger().info(f"behaviors command processed. The behaviors saved")
        except Exception as e:
            self.get_logger().error(f"behaviors command processing failed {str(e)}")
            raise e

    def do_environment(self, cuuid, data_received):
        self.get_and_simplify(cuuid, data_received, symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value)

    def get_and_simplify(self, cuuid, data_received, infix):
        # Loading
        res = self.do_get_file(cuuid,
                               symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value,
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

    def do_solver(self, cuuid, msg:str):
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

    def do_max_models(self, cuuid, msg:str):
        b = 10  # default value of solver max models
        if hasattr(self, "max_models"):
            b = getattr(self, "max_models")
        else:
            try:
                s = self.get_config().get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.SOLVER_MAX_MODELS.value)
                if s.isnumeric():
                   b = int(s)
            except:
                b = 10

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