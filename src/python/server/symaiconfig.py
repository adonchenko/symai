import configparser
import os.path
from enum import Enum

class SymAISolvers(Enum):
    SYMPY = "SymPy"
    Z3 = "Z3"
    CVC5= "CVC5"

class SymAIConfig(Enum):
    EXPRESSION = "Expression"
    SYMAICORE = "SymAI"
    TEMP = "tempdir"
    EXPRESSION_HOST="expression_host"
    EXPRESSION_PORT="expression_port"
    EXPRESSION_SOLVER="expression_solver"   # Math package i.e. SymPy, Z3, CVC5
    HOST = "host"
    PORT = "port"
    LOGGERS = "loggers"
    KEYS = "keys"
    HANDLERS = "handlers"
    FORMATTERS = "formatters"
    LOGGER_ROOT = "logger_root"
    LEVEL = "level"
    LOGGER_EXPRESSION = "logger_expression"
    LOGGER_SYMAICORE = "logger_symaicore"
    QUALNAME = "qualname"
    PROPAGATE = "propagate"
    HANDLER_CONSOLEHANDLER = "handler_consoleHandler"
    CLASS = "class"
    FORMATTER = "formatter"
    ARGS = "args"
    FORMATTER_SIMPLEFORMATTER = "formatter_simpleFormatter"
    FORMAT = "format"
    HANDLER_FILE  = "handler_file"
    HANDLER_FILE_SYMAICORE = "handler_file_symaicore"
    INTERVAL = "interval"
    BACKUP_COUNT = "backupCount"

    BASE_TEMP = "/tmpdir"
    BASE_PROPERTIES = "properties"
    BASE_PRECONDITION = "precondition"
    BASE_POSTCONDITION = "postcondition"
    BASE_ENVIRONMENT = "environment"

def create_config(cfg_file, section, cfg):
    """
    Create a config file
    """
    c = configparser.ConfigParser()
    if os.path.exists(cfg_file) :
        c.read(cfg_file)
    else:
        #SymAICore
        c.add_section(SymAIConfig.SYMAICORE.value)
        c.set(SymAIConfig.SYMAICORE.value, SymAIConfig.TEMP.value, "/tmpdir/temp")
        c.set(SymAIConfig.SYMAICORE.value,SymAIConfig.HOST.value, "localhost")
        c.set(SymAIConfig.SYMAICORE.value, SymAIConfig.PORT.value, str(12345))
        c.set(SymAIConfig.SYMAICORE.value,SymAIConfig.EXPRESSION_HOST.value, "localhost")
        c.set(SymAIConfig.SYMAICORE.value, SymAIConfig.EXPRESSION_PORT.value, str(8080))
        #Expression
        c.add_section(SymAIConfig.EXPRESSION.value)
        c.set(SymAIConfig.EXPRESSION.value,SymAIConfig.HOST.value, "localhost")
        c.set(SymAIConfig.EXPRESSION.value, SymAIConfig.PORT.value, str(8080))
        c.set(SymAIConfig.EXPRESSION.value, SymAIConfig.EXPRESSION_SOLVER.value, SymAISolvers.SYMPY.value)
        #Loggers
        c.add_section(SymAIConfig.LOGGERS.value)
        c.set(SymAIConfig.LOGGERS.value, SymAIConfig.KEYS.value, "root, expression, symaicore")
        c.add_section(SymAIConfig.HANDLERS.value)
        c.set(SymAIConfig.HANDLERS.value, SymAIConfig.KEYS.value, "consoleHandler,file,file_symaicore")
        c.add_section(SymAIConfig.FORMATTERS.value)
        c.set(SymAIConfig.FORMATTERS.value, SymAIConfig.KEYS.value, "simpleFormatter")
        c.add_section(SymAIConfig.LOGGER_ROOT.value)
        c.set(SymAIConfig.LOGGER_ROOT.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.LOGGER_ROOT.value, SymAIConfig.HANDLERS.value, "consoleHandler")
        c.add_section(SymAIConfig.LOGGER_EXPRESSION.value)
        c.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.HANDLERS.value, "consoleHandler,file")
        c.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.QUALNAME.value, "expression")
        c.set(SymAIConfig.LOGGER_EXPRESSION.value, SymAIConfig.PROPAGATE.value, "0")

        c.add_section(SymAIConfig.LOGGER_SYMAICORE.value)
        c.set(SymAIConfig.LOGGER_SYMAICORE.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.LOGGER_SYMAICORE.value, SymAIConfig.HANDLERS.value, "consoleHandler,file_symaicore")
        c.set(SymAIConfig.LOGGER_SYMAICORE.value, SymAIConfig.QUALNAME.value, "symaicore")
        c.set(SymAIConfig.LOGGER_SYMAICORE.value, SymAIConfig.PROPAGATE.value, "0")

        c.add_section(SymAIConfig.HANDLER_CONSOLEHANDLER.value)
        c.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.CLASS.value, "StreamHandler")
        c.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.FORMATTER.value, "simpleFormatter")
        c.set(SymAIConfig.HANDLER_CONSOLEHANDLER.value, SymAIConfig.ARGS.value, "(sys.stdout,)")
        c.add_section(SymAIConfig.FORMATTER_SIMPLEFORMATTER.value)
        c.set(SymAIConfig.FORMATTER_SIMPLEFORMATTER.value, SymAIConfig.FORMAT.value, "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        c.add_section(SymAIConfig.HANDLER_FILE.value)
        c.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.CLASS.value, "handlers.TimedRotatingFileHandler")
        c.set(SymAIConfig.HANDLER_FILE.value,SymAIConfig.INTERVAL.value, "midnight")
        c.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.BACKUP_COUNT.value, "5")
        c.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.FORMATTER.value, "simpleFormatter")
        c.set(SymAIConfig.HANDLER_FILE.value, SymAIConfig.ARGS.value , "('/logdir/expression.log',)")

        c.add_section(SymAIConfig.HANDLER_FILE_SYMAICORE.value)
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.CLASS.value, "handlers.TimedRotatingFileHandler")
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.INTERVAL.value, "midnight")
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.BACKUP_COUNT.value, "5")
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.LEVEL.value, "DEBUG")
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.FORMATTER.value, "simpleFormatter")
        c.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.ARGS.value, "('/logdir/symaicore.log',)")

    # merge input data
    if not c.has_section(section):
        c.add_section(section)
    for k in cfg[section]:
        if c.has_option(section, k):
            c.remove_option(section, k)
        c.set(section, k, cfg.get(section, k))
    with open(cfg_file, "w") as c_file:
        c.write(c_file)
    return c
