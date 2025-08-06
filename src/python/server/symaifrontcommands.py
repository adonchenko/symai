import os
import re
from pathlib import Path
import symaicommands
import symaiconfig

class SymAIFrontendCommands(symaicommands.SymAICommands):

    def do_shutdown(self):
        self.get_logger().info("Shutdown received")

    def do_get(self, request_handler, resource_path):
        ct = "text/html"
        fn = "index.html"
        is_binary = False
        base_path = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                          symaiconfig.SymAIConfig.SYMAIFRONT_RESOURCES.value)
        if resource_path == "/favicon.ico":
            ct = "image/x-icon"
            is_binary = True
            fn = "favicon.ico"
        else:
            if len(resource_path) > 1  and re.search("/symai/*", resource_path):
                froot, fext = os.path.splitext(resource_path)
                fext = fext.lower()
                if len(fext) > 0:
                    if fext == ".html" or fext == ".htm":
                        ct = "text/html"
                    elif fext == ".gif":
                        ct = "image/gif"
                        is_binary = True
                    elif fext == ".jpg" or fext == ".jpeg" :
                        ct = "image/jpeg"
                        is_binary = True
                    elif fext == ".png":
                        ct = "image/png"
                        is_binary = True
                    elif fext == ".tiff":
                        ct = "image/tiff"
                        is_binary = True
                    elif fext == ".ico":
                        ct = "image/x-icon"
                        is_binary = True
                    elif fext == ".svg":
                        ct = "image/svg+xml"
                        is_binary = True
                    elif fext == ".css":
                        ct = "text/css"
                    elif fext == ".csv":
                        ct = "text/csv"
                    elif fext == ".js":
                        ct = "text/javascript"
                    elif fext == ".text" or fext == ".txt":
                        ct = "text/plain"
                    elif fext == ".xml":
                        ct = "text/xml"

                fn = resource_path[7:]
            else:
                fn = "index.html"
                ct = "text/html"

        fn = Path(os.path.join(base_path, fn))
        if fn.exists() and fn.is_file():
            filename = fn
        else:
            filename = os.path.join(base_path, "index.html")
            ct = "text/html"
            is_binary = False
        if not is_binary:
            subs = dict()
            subs["FRONTEND_HOST"] = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                          symaiconfig.SymAIConfig.SYMAIFRONT_HOST.value)
            subs["FRONTEND_PORT"] = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                          symaiconfig.SymAIConfig.SYMAIFRONT_PORT.value)
            subs["CORE_HOST"] = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                      symaiconfig.SymAIConfig.SYMAICORE_HOST.value)
            subs["CORE_PORT"] = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                                      symaiconfig.SymAIConfig.SYMAICORE_PORT.value)

            f = open(filename, "r")
            cnt = f.read()
            cnt.format(**subs)
            cnt = bytes(cnt, 'utf-8')
        else:
            f = open(filename, "rb")
            cnt = f.read()
        return cnt, ct
