from Singleton import Singleton
import logging

class Logger(Singleton):
    _logger = None

    @classmethod
    def init(cls):
        cls._logger = logging.getLogger("icao")
        cls._logger.setLevel(logging.DEBUG)  # Set the logging level for the logger
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s - %(message)s')

        fh = logging.FileHandler("icao.log", mode="w")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        cls._logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        cls._logger.addHandler(ch)

    @classmethod
    def debug(cls, msg:str): cls._logger.debug(msg)

    @classmethod
    def info(cls, msg: str): cls._logger.info(msg)

    @classmethod
    def warning(cls, msg: str): cls._logger.warning(msg)

    @classmethod
    def error(cls, msg: str): cls._logger.error(msg)

    @classmethod
    def critical(cls, msg: str): cls._logger.critical(msg)

# Ensure the instance is created during class definition
Logger._instance = Logger()