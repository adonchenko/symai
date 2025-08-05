import os
from pathlib import Path
import symaicommands
import symaiconfig

class SymAIFrontendCommands(symaicommands.SymAICommands):

    def do_shutdown(self):
        self.get_logger().info("Shutdown received")

    def do_get(self, request_handler, resource_path):
        base_path = self.get_config().get(symaiconfig.SymAIConfig.SYMAIFRONT.value,
                                          symaiconfig.SymAIConfig.SYMAIFRONT_RESOURCES.value)
        fn = Path(os.path.join(base_path, resource_path[7:]))
        if fn.exists() and fn.is_file():
            filename = os.path.join(base_path, resource_path[7:])
        else:
            filename = os.path.join(base_path, "index.html")
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

        return cnt


