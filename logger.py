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
        self.log_device = None

    def set_log_filepath(self, log_filepath: str):
        self.log_device = open(log_filepath, 'a')

    def log(self, level: LogLevel, place: Place, message: str):
        assert self.log_device is not None, "Log device is not set"

        self.log_device.write(f"{level.name:<10}{'::':<7}{place.name:<12}{message}\n")
        self.log_device.flush()

    def turn_off(self):
        self.log_device.close()
