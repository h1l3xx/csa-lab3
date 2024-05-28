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
    input_buffer: int
    output_buffer: list[str]

    def __init__(self, memory: list[int], stack_size: int):
        self.data_stack = Stack(stack_size)
        self.input_buffer = 0
        self.output_buffer = []
        self.data = [0, 1] + memory
        self.data_size = len(memory)
        self.alu = ALU()


    def set_tos(self):
        self.tos = self.data_stack.peek()
