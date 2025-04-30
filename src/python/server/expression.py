#!/usr/bin/python3

"""An HTTP server with REST and json for python 3.

/api/v1/simplify POST request takes an expression from json request body 'formula' field and
         returns either the error code or the expression that has been simplified
         Sample of request: curl -X POST http://localhost:80/api/v1/simplify -d '{"formula":"cos(y+x)**2 + pow(sin(x+y), 2)  + 4"}' -H "Content-Type: application/json"
         Server response: {"formula": "5"}
/api/v1/shutdown GET request stops the server.
"""
import configparser

import symaiconfig
import symaiexpressioncommands
import logging
from logging import config
import sympy
from sympy import *
import argparse
import json
import re
import threading
from email.message import EmailMessage
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import signal

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream
from symbolicexpressiongrammarvisitor import *
from ExpressionGrammar.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.ExpressionGrammarParser import ExpressionGrammarParser
import sys

def _parse_header(content_type):
    m = EmailMessage()
    m["content-type"] = content_type
    return m.get_content_type(), m["content-type"].params

class HTTPRequestHandler(BaseHTTPRequestHandler):
    sc : symaiexpressioncommands.SymAIExpressionCommands
    def do_send_ok_rsp(self, rsp, cmn, res):
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(rsp).encode("utf8"))
        except Exception as e:
            self.sc.get_logger().error(f"{cmn} failed. Error sending response {str(e)}")
        else:
            try:
                self.wfile.write(json.dumps(rsp).encode("utf8"))
            except Exception as e:
                self.sc.get_logger().error(f"{cmn} failed. Error sending response body {str(e)}")
            else:
                self.sc.get_logger().info(f"{cmn} passed with result {res}")

    def do_send_err_rsp(self, rsp):
        self.sc.get_logger().error(rsp)
        self.send_response(HTTPStatus.BAD_REQUEST, rsp)

    def do_POST(self):
        self.sc = symaiexpressioncommands.SymAIExpressionCommands()
        logger = self.sc.get_logger()
        if re.search("/api/v1/check", self.path):
            ctype, pdict = _parse_header(self.headers.get("content-type"))
            if ctype == "application/json":
                length = int(self.headers.get("content-length"))
                rfile_str = self.rfile.read(length).decode("utf8")
                try:
                    res = self.sc.do_check(rfile_str)
                except Exception as e:
                    self.do_send_err_rsp(f"Bad request: {str(e)}")
                else:
                    self.do_send_ok_rsp(res, "check", res)
            else:
                self.do_send_err_rsp("Bad Request: must give data")
        elif re.search("/api/v1/simplify", self.path):
            ctype, pdict = _parse_header(self.headers.get("content-type"))
            if ctype == "application/json":
                length = int(self.headers.get("content-length"))
                rfile_str = self.rfile.read(length).decode("utf8")
                try:
                    res = self.sc.do_simplify(rfile_str)
                except Exception as e:
                    self.do_send_err_rsp(f"Bad request: {str(e)}")
                else:
                    self.do_send_ok_rsp(res, "simplify", res["formula"])
            else:
                self.do_send_err_rsp("Bad Request: must give data")
        elif re.search("/api/v1/solve", self.path):
            ctype, pdict = _parse_header(self.headers.get("content-type"))
            if ctype == "application/json":
                length = int(self.headers.get("content-length"))
                rfile_str = self.rfile.read(length).decode("utf8")
                try:
                    source_expr = json.loads(rfile_str)
                except:
                    logger.error("Bad Request: incorrect syntax of json request")
                    self.send_response(
                        HTTPStatus.BAD_REQUEST, "Bad Request: incorrect syntax of json request"
                    )
                else:
                    expr = source_expr.get("formula")
                    if expr is None:
                        logger.error("Bad Request: missing formula")
                        self.send_response(
                            HTTPStatus.BAD_REQUEST, "Bad Request: missing formula field"
                        )
                    else:
                        try:
                            expr_n = ((((((" " + expr + " ")
                                          .replace(" not ", " _n_o_t_ "))
                                         .replace("!", " not "))
                                        .replace("_d_o_t_", "__d__o__t__"))
                                       .replace(".", "_d_o_t_"))
                                      .strip(" "))

                            lexer = ExpressionGrammarLexer(InputStream(expr_n))
                            errorListener = SymbolicExpressionGrammarErrorListener()
                            lexer.removeErrorListeners()
                            lexer.addErrorListener(errorListener)
                            stream = CommonTokenStream(lexer)
                            parser = ExpressionGrammarParser(stream)
                            parser.removeErrorListeners()
                            parser.addErrorListener(errorListener)

                            tree = parser.expression()

                            visitor = SymbolicExpressionGrammarVisitor()
                            formula = visitor.visit(tree)

                            print(f"before solve: {formula}")
                            try:
                                fml = sympy.solve(formula, simplify=true, dict=true)
                                print(f"Good formula {str(fml)}     ")
                                formula = str(fml)
                            except Exception as e:
                                logger.debug(f"solve({expr} failed {str(e)}")
                                formula = "Unsolvable"
                            formula = (((((" " + formula + " ")
                                          .replace("&", "&&")
                                          .replace("|", "||")
                                          .replace("_d_o_t_", "."))
                                         .replace("__d__o__t__", "_d_o_t_"))
                                        .replace(" not ", "!"))
                                       .replace(" _n_o_t_ ", " not ")).strip(" ")
                        except:
                            logger.error("error processing formula %s" % expr)
                            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR,
                                               "Bad request: error processing formula %s" % (expr))
                        else:
                            self.send_response(HTTPStatus.OK)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()

                            source_expr['formula'] = formula

                            logger.info("simplify %s -> %s" % (expr, formula))
                            self.wfile.write(json.dumps(source_expr).encode("utf8"))
            else:
                logger.error("Bad Request: must give data")
                self.send_response(
                    HTTPStatus.BAD_REQUEST, "Bad Request: must give data"
                )
        else:
            self.send_response(HTTPStatus.FORBIDDEN)

        self.end_headers()

    def do_GET(self):
        if re.search("/api/v1/shutdown", self.path):
            symaiexpressioncommands.SymAIExpressionCommands().do_shutdown()
            # Must process shutdown in another thread or we'll hang
            def kill_me_please():
                self.server.shutdown()
            threading.Thread(target=kill_me_please).start()

            # Send out a 200 before we go
            self.send_response(HTTPStatus.OK)
        else:
            self.send_response(HTTPStatus.BAD_REQUEST)

        self.end_headers()

def signal_handler(signal, frame):
    logger = logging.getLogger("expression")
    logger.info("Signal INT caught")
    sys.exit(0)

def main():
    sc = symaiexpressioncommands.SymAIExpressionCommands()

    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument( "-p", "--port", dest="port", default = 8080, required = false, type=int, help="Listening port for an expressions HTTP Server")
    parser.add_argument("-i", "--ip", dest = "ip", default = "localhost", required = false, help="Expressions HTTP Server IP")
    parser.add_argument("-c", "--config", dest="config", default="/properties/symai.ini", required=false, help="Configuration file name of expression HTTP Server")
    parser.add_argument("-s", "--solver", dest="solver", default=symaiconfig.SymAISolvers.SYMPY.value, required=false, help="A solver package name")

    args = parser.parse_args()

    cfg = configparser.ConfigParser()
    cfg.add_section(symaiconfig.SymAIConfig.EXPRESSION.value)
    cfg.set(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.HOST.value, args.ip)
    cfg.set(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.PORT.value, str(args.port))
    cfg.set(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.EXPRESSION_SOLVER.value, str(args.solver))

    cfg = symaiconfig.create_config(args.config, symaiconfig.SymAIConfig.EXPRESSION.value, cfg)
    logging.config.fileConfig(args.config)
    logger = logging.getLogger("expression")
    signal.signal(signal.SIGINT, signal_handler)
    sc.set_config(cfg)
    sc.set_logger(logger)
    httpd = ThreadingHTTPServer((str(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.HOST.value)), int(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.PORT.value))), HTTPRequestHandler)
    logger.info("HTTP Server Running On %s:%s ..........." % (cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.HOST.value), int(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.PORT.value))))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
