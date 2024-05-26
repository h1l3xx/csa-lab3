from alu import ALU
from stack import Stack


class DataPath:
    data: list[int] = None

    data_address: int = None
    data_stack = None
    tos: int = None
    sos: int = None
    data_size = None
    alu: ALU = None

    def __init__(self, memory: list[int], stack_size: int):
        self.data_stack = Stack(stack_size)
        self.data = memory
        self.data_size = len(memory)
        self.alu = ALU()

    def set_tos(self):
        self.tos = self.data_stack.peek()