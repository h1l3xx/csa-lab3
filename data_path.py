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
    input_buffer_size: int = 0
    input_buffer: list[str] = None
    output_buffer: list[str] = None

    def __init__(self, memory: list[int], stack_size: int):
        self.data_stack = Stack(stack_size)
        self.data = memory
        self.data_size = len(memory)
        self.alu = ALU()
        self.input_buffer = []
        self.output_buffer = []

    def set_tos(self):
        self.tos = self.data_stack.peek()
