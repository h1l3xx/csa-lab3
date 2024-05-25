from alu import ALU
from stack import Stack


class DataPath:
    data: list[int] = None

    data_address: int = None
    data_stack = Stack()
    tos: int = data_stack.peek()
    sos: int = None
    stack_pointer: int = None

    alu: ALU = None

    def __init__(self, memory: list[int]):
        self.data = memory
        self.alu = ALU()
