import json
import symaicommands
import symaiconfig
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class SymAIFrontendCommands(symaicommands.SymAICommands):

    def do_shutdown(self):
        self.get_logger().info("Shutdown received")

    def do_get(self, request_handler, request_path):

        request_handler.do_send_ok_rsp(request_path, "Good", "ok")


