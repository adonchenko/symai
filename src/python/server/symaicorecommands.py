from http import HTTPStatus

from websockets.legacy.server import HTTPResponse

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
            response = conn.getresponse()
        except:
            self.get_logger().error("Error on shutdown expression ",
                                  self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                      symaiconfig.SymAIConfig.EXPRESSION_HOST.value),
                                  " ", int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                               symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
        self.get_logger().info("Shutting down the service....")

    def do_stop(self):
        self.get_logger().info("Stop command received. Session closed.")

    # Loads and saves the file
    # On success returns the structure that has two fields:
    # - filename that is a source file name
    # - content that is a content of this file
    # On error raises an Exception
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
                    raise Exception("Cannot create directory " + d)
            filename = os.path.join(d, res["filename"].strip())
            file_content = str(res["content"])
            try:
                with open(filename, "w") as file:
                    file.write(file_content)
            except:
                raise Exception("Cannot write content to file '" + str(filename) + "'")
        return res

    def do_environment(self, cuuid, data_received):
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
            conn.request('POST', '/api/v1/simplify', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt simplify expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            with open(os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                        cuuid,
                        symaiconfig.SymAIConfig.BASE_ENVIRONMENT.value,
                        res["filename"]), "w") as f:
                f.write(rsp["formula"])

        except Exception as e:
            raise e