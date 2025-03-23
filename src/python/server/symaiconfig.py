import configparser
import os.path
from enum import Enum

class SymAIConfig(Enum):
    EXPRESSION = "Expression"
    HOST = "hosh"
    PORT = "port"
    LOGGERS = "loggers"
    KEYS = "keys"
    HANDLERS = "handlers"
    FORMATTERS = "formatters"
    LOGGER_ROOT = "logger_root"
    LEVEL = "level"
    LOGGER_EXPRESSION = "logger_expression"
    QUALNAME = "qualname"
    PROPAGATE = "propagate"
    HANDLER_CONSOLEHANDLER = "handler_consoleHandler"
    CLASS = "class"
    FORMATTER = "formatter"
    ARGS = "args"
    FORMATTER_SIMPLEFORMATTER = "formatter_simpleFormatter"
    FORMAT = "format"
    HANDLER_FILE  = "handler_file"
    INTERVAL = "interval"
    BACKUP_COUNT = "backupCount"

def create_config(cfg_file, host, port):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_file):
        #Expression
        config.add_section(SymAIConfig.EXPRESSION.value)
        config.set(SymAIConfig.EXPRESSION.value,SymAIConfig.HOST.value, host)
        config.set(SymAIConfig.EXPRESSION.value, SymAIConfig.PORT.value, str(port))
        #Loggers
        config.add_section(SymAIConfig.LOGGERS.value)
        config.set(SymAIConfig.LOGGERS.value, SymAIConfig.KEYS.value, "root, expression")
        config.add_section(SymAIConfig.HANDLERS.value)
        config.set(SymAIConfig.HANDLERS.value, SymAIConfig.KEYS.value, "consoleHandler,file")
        config.add_section(SymAIConfig.FORMATTERS.value)
        config.set(SymAIConfig.FORMATTERS.value, SymAIConfig.KEYS.value, "simpleFormatter")
        config.add_section(SymAIConfig.LOGGER_ROOT.value)
        config.set(SymAIConfig.LOGGER_ROOT.value, SymAIConfig.LEVEL.value, "DEBUG")
        config.set(SymAIConfig.LOGGER_ROOT.value, SymAIConfig.HANDLERS.value, "consoleHandler")
        config.add_section(SymAIConfig.LOGGER_EXPRESSION.value)
        config.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.LEVEL.value, "DEBUG")
        config.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.HANDLERS.value, "consoleHandler,file")
        config.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.QUALNAME.value, "expression")
        config.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.PROPAGATE.value, "0")
        config.add_section(SymAIConfig.HANDLER_CONSOLEHANDLER.value)
        config.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.CLASS.value, "StreamHandler")
        config.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.LEVEL.value, "DEBUG")
        config.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.FORMATTER.value, "simpleFormatter")
        config.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.ARGS.value, "(sys.stdout,)")
        config.add_section(SymAIConfig.FORMATTER_SIMPLEFORMATTER.value)
        config.set(SymAIConfig.FORMATTER_SIMPLEFORMATTER.value, SymAIConfig.FORMAT.value, "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        config.add_section(SymAIConfig.HANDLER_FILE.value)
        config.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.CLASS.value, "handlers.TimedRotatingFileHandler")
        config.set(SymAIConfig.HANDLER_FILE.value,SymAIConfig.INTERVAL.value, "midnight")
        config.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.BACKUP_COUNT.value, "5")
        config.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.LEVEL.value, "DEBUG")
        config.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.FORMATTER.value, "simpleFormatter")
        config.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.ARGS.value , "('expression.log',)")

        with open(cfg_file, "w") as c_file:
            config.write(c_file)
    else:
        config.read(cfg_file)
    return config
