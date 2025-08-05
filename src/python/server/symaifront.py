#!/usr/bin/python3

"""An HTTP server that supports frontend for SymAI. Implemented using python 3.

/api/v1/system/shutdown GET request stops the server.
/symai/<path-to-page> GET request to get a desired page. If page is absent, the index.html will be returned
"""
import configparser

import symaiconfig
import symaifrontcommands
import logging
from logging import config
import argparse
import re
import threading
from email.message import EmailMessage
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import signal

import sys

def _parse_header(content_type):
    m = EmailMessage()
    m["content-type"] = content_type
    return m.get_content_type(), m["content-type"].params

class HTTPRequestHandler(BaseHTTPRequestHandler):
    sc : symaifrontcommands.SymAIFrontendCommands = symaifrontcommands.SymAIFrontendCommands()

    def log_message(self, format, *args):
        return

    def do_send_err_rsp(self, rsp):
        self.sc.get_logger().error(rsp)
        try:
            self.send_response(HTTPStatus.BAD_REQUEST, rsp)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
        except Exception as e:
            pass

    def do_GET(self):
        if re.search("/api/v1/system/shutdown", self.path):
            self.sc.do_shutdown()
            # Must process shutdown in another thread or we'll hang
            def kill_me_please():
                self.server.shutdown()
            threading.Thread(target=kill_me_please).start()

            # Send out a 200 before we go
            try:
                self.send_header("Content-Type", "text/html")
                self.end_headers()
            except Exception as e:
                pass
        elif re.search("/symai/*", self.path):
            try:
                s  = self.sc.do_get(self, self.path)
                print(f"{s}")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(s.encode('utf-8'))
                self.sc.get_logger().info(f"Processed GET {self.path}")
            except Exception as e:
                self.sc.get_logger().error(f"Error {e}")
                self.do_send_err_rsp(f"Error {e}")
        else:
            self.do_send_err_rsp(f"Bad request GET {self.path}")

def signal_handler(signal, frame):
    logger = logging.getLogger("frontend")
    logger.info("Signal INT caught")
    sys.exit(0)

def main():
    sc = symaifrontcommands.SymAIFrontendCommands()

    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument( "-p", "--port", dest="port", default = 8000, required = False, type=int, help="Listening port for a frontend HTTP Server")
    parser.add_argument("-i", "--ip", dest = "ip", default = "localhost", required = False, help="Frontend HTTP Server IP")
    parser.add_argument("-c", "--config", dest="config", default="/properties/symai.ini", required=False, help="Configuration file name of frontend HTTP Server")
    parser.add_argument("-ch", "--corehost", dest="core_host", default="localhost", required=False, help="A SymAI Core host name or IP address")
    parser.add_argument("-cp", "--coreport", dest="core_port", default=12345, required = False, type=int, help="A SymAI Core port no")
    parser.add_argument("-r", "--resources", dest="resources", default="/resources", required=False, help="Frontend HTTP server resources path")

    args = parser.parse_args()

    cfg = configparser.ConfigParser()
    cfg.add_section(symaiconfig.SymAIConfig.SYMAIFRONT.value)
    cfg.set(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAIFRONT_HOST.value, args.ip)
    cfg.set(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAIFRONT_PORT.value, str(args.port))
    cfg.set(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAICORE_PORT.value, str(args.core_port))
    cfg.set(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAICORE_HOST.value,args.core_host)
    cfg.set(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAIFRONT_RESOURCES.value, args.resources)

    cfg = symaiconfig.create_config(args.config, symaiconfig.SymAIConfig.SYMAIFRONT.value, cfg)
    logging.config.fileConfig(args.config)
    logger = logging.getLogger("frontend")
    signal.signal(signal.SIGINT, signal_handler)
    sc.set_config(cfg)
    sc.set_logger(logger)
    httpd = ThreadingHTTPServer(
        (str(cfg.get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                     symaiconfig.SymAIConfig.SYMAIFRONT_HOST.value)),
         int(cfg.get(symaiconfig.SymAIConfig.SYMAIFRONT.value, symaiconfig.SymAIConfig.SYMAIFRONT_PORT.value))),
        HTTPRequestHandler)
    logger.info("SymAI Frontend HTTP Server Running On %s:%s ..........." % (cfg.get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                                      symaiconfig.SymAIConfig.SYMAIFRONT_HOST.value),
                                                              int(cfg.get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                                          symaiconfig.SymAIConfig.SYMAIFRONT_PORT.value))))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
