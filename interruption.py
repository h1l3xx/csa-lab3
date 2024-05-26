from enum import Enum


class InterruptionType(Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    HLT = "HLT"
    ERROR = "ERROR"


class Interruption:
    def __init__(self, interruption_type: InterruptionType, message: str = ''):
        self.interruption_type = interruption_type
        self.message = message

    def __str__(self):
        return f"Interruption: {self.interruption_type.name}" + (f" {self.message}" if self.message != "" else "")

    def __repr__(self):
        return str(self)