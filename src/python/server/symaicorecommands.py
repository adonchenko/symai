from http import HTTPStatus
import symaicommands
import symaiconfig
import http.client
import json
import uuid
import os

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
            conn.request('GET', '/api/v1/shutdown', "", headers)
            conn.getresponse()
        except:
            self.get_logger().error("Error on shutdown expression ",
                                  self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                      symaiconfig.SymAIConfig.EXPRESSION_HOST.value),
                                  " ", int(self.get_config().get(symaiconfig.SymAIConfig.SYMAICORE.value,
                                                               symaiconfig.SymAIConfig.EXPRESSION_PORT.value)))
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
            conn.request('POST', '/api/v1/simplify', json.dumps(query), headers)
            response = conn.getresponse()
            if not (response.getcode() == HTTPStatus.OK):
                raise Exception("Attempt simplify expression error Error code " + str(conn.getresponse()))
            rsp = json.loads(response.read().decode())
            with open(os.path.join(symaiconfig.SymAIConfig.BASE_TEMP.value,
                        cuuid,
                        infix,
                        res["filename"]), "w") as f:
                f.write(rsp["formula"])
            self.get_logger().info(f"{infix} command processed. The {infix} formula {rsp["formula"]} saved")
        except Exception as e:
            self.get_logger().error(f"{infix} command processing failed {str(e)}")
            raise e

    def do_ai(self, cuuid, msg:str):
        b = False
        s = str(msg).strip().split()
        if len(s) == 1:
            if not hasattr(self, "ai"):
                setattr(self, "ai", False)
            b = getattr(self, "ai")
        elif len(s) == 2:
            if s[1].lower() == "true" or s[1].lower() == "yes" or s[1].lower() == "1":
                setattr(self, "ai", True)
            else:
                setattr(self, "ai", False)
            b = getattr(self, "ai")
        else:
            raise Exception(f"Incorrect command format {msg}")
        return str(b)
