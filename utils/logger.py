from enum import Enum


class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    DEBUG = 3


class Place(Enum):
    INTER = 0
    INSTR = 1
    ALU = 2
    SYSTEM = 3
    INPUT = 4
    OUTPUT = 5


class Logger:
    def __init__(self):
        self.log_file = None

    def set_log_filepath(self, log_filepath: str):
        self.log_file = open(log_filepath, "a")

    def log(self, level: LogLevel, place: Place, message: str):
        self.log_file.write(f"{level.name:<10}{'::':<7}{place.name:<12}{message}\n")
        self.log_file.flush()
