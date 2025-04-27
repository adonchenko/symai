import symaiconfig
from configparser import ConfigParser
from logging import Logger

class SymAICommands:
    config:ConfigParser
    logger:Logger

    def set_config(self, cfg : ConfigParser):
        if not hasattr(SymAICommands, "config"):
            SymAICommands.config = cfg

    def get_config(self)->ConfigParser:
        return  SymAICommands.config

    def set_logger(self,lgr : Logger):
        if not hasattr(SymAICommands, "logger"):
            SymAICommands.logger = lgr

    def get_logger(self)->Logger:
        return SymAICommands.logger
