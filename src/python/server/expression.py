#!/usr/bin/python3

"""An HTTP server with REST and json for python 3.

/api/v1/simplify POST request takes an expression from json request body 'formula' field and
         returns either the error code or the expression that has been simplified
         Sample of request: curl -X POST http://localhost:80/api/v1/simplify -d '{"formula":"cos(y+x)**2 + pow(sin(x+y), 2)  + 4"}' -H "Content-Type: application/json"
         Server response: {"formula": "5"}
/api/v1/shutdown GET request stops the server.
"""
from antlr4.error.Errors import ParseCancellationException

import symaiconfig
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
from ExpressionGrammar.antlr4.ExpressionGrammarLexer import ExpressionGrammarLexer
from ExpressionGrammar.antlr4.ExpressionGrammarParser import ExpressionGrammarParser
import sys
from antlr4.error.ErrorListener import *

class SymbolicExpressionGrammarErrorListener( ErrorListener ):

    def __init__(self):
        super(SymbolicExpressionGrammarErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception("Syntax error appeared on symbol '" + offendingSymbol + "' " + msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        raise Exception("Ambiguity error appeared during parsing")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        raise Exception("Error appeared during parsing")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        raise Exception("Oh no!!")


def _parse_header(content_type):
    m = EmailMessage()
    m["content-type"] = content_type
    return m.get_content_type(), m["content-type"].params

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        logger = logging.getLogger("expression")
        if re.search("/api/v1/simplify", self.path):
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

                            formula = str(sympy.simplify(formula))
                            formula = (((((" " + formula + " ")
                                       .replace("&","&&")
                                       .replace("|","||")
                                       .replace("_d_o_t_", "."))
                                       .replace("__d__o__t__", "_d_o_t_"))
                                       .replace(" not ", "!"))
                                       .replace(" _n_o_t_ ", " not ")).strip(" ")
                        except:
                            logger.error("error processing formula %s" % expr)
                            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR, "Bad request: error processing formula %s" % (expr))
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
        logger = logging.getLogger("expression")
        logger.info("Shutdown received")
        if re.search("/api/v1/shutdown", self.path):
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
    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument( "-p", "--port", dest="port", default = 8080, required = false, type=int, help="Listening port for an expressions HTTP Server")
    parser.add_argument("-i", "--ip", dest = "ip", default = "localhost", required = false, help="Expressions HTTP Server IP")
    parser.add_argument("-c", "--config", dest="config", default="/properties/expression.ini", required=false, help="Configuration file name fo HTTP Server")

    args = parser.parse_args()

    cfg = symaiconfig.create_config(args.config, args.ip, args.port)
    logging.config.fileConfig(args.config)
    logger = logging.getLogger("expression")
    signal.signal(signal.SIGINT, signal_handler)
    httpd = ThreadingHTTPServer((str(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.HOST.value)), int(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.PORT.value))), HTTPRequestHandler)
    logger.info("HTTP Server Running On %s:%s ..........." % (cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.HOST.value), int(cfg.get(symaiconfig.SymAIConfig.EXPRESSION.value, symaiconfig.SymAIConfig.PORT.value))))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
