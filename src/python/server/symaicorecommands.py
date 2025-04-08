import symaiconfig
from configparser import ConfigParser
from logging import Logger
import http.client
import json
import uuid
import os

class SymAICoreParam:

    def __init__(self):
        self.session_uuid = uuid.uuid4()

    def get_uuid(self):
        return self.session_uuid

class SymAICoreCommands:

    def set_config(self, cfg : ConfigParser):
        if not hasattr(SymAICoreCommands, "config"):
            SymAICoreCommands.config = cfg

    def get_config(self)->ConfigParser:
        return  self.config

    def set_logger(self,lgr : Logger):
        if not hasattr(SymAICoreCommands, "logger"):
            SymAICoreCommands.logger = lgr

    def get_logger(self)->Logger:
        return self.logger

    def do_shutdown(self):
        headers = {'Content-type': 'application/json'}
        try:
            conn = http.client.HTTPConnection(
                str(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                        symaiconfig.SymAIConfig.EXPRESSION_HOST.value)),
                int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                        symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
            conn.request('GET', '/api/v1/shutdown', "", headers)
            # response = conn.getresponse()
        except:
            self.get_logger().error("Error on shutdown expression ",
                                  self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                      symaiconfig.SymAIConfig.EXPRESSION_HOST.value),
                                  " ", int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                               symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
        self.get_logger().info("Shutting down the service....")

    def do_stop(self):
        self.get_logger().info("Stop command received. Session closed.")

    def do_get_file(self, pref, mid, data_received):
        try:
            res = json.loads(data_received.replace("'", '"'))
        except:
            self.get_logger().error("Incorrect input JSON data " + data_received)
            raise Exception("Incorrect input JSON data " + data_received)
        if res["filename"] is None or len(res["filename"].strip()) == 0:
            self.get_logger().error("Incorrect JSON data. Field 'filename' is empty.")
            raise Exception("Incorrect JSON data. Field 'filename' is empty.")
        elif res["content"] is None or len(res["content"].strip()) == 0:
            self.get_logger().error("Incorrect JSON data. Field 'content' is empty.")
            raise Exception("Incorrect JSON data. Field 'content' is empty.")
        else:
            filename = os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                                    pref,
                                    mid,
                                    res["filename"].strip())
            file_content = bytes(data_received["content"])
            try:
                with open(f"{filename}", 'wb') as file:
                    file.write(file_content)
            except:
                self.get_logger().error("Cannot write content to file '" + str(filename) + "'")
                raise Exception("Cannot write content to file '" + str(filename) + "'")

