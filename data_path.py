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

    def load_in_memory(self, index: int, value):
        if index <= self.data_size + 1:
            self.data[index] = value
        else:
            self.data.append(value)

    def push_in_stack(self, value: int):
        self.data_stack.push(value)

    def pop_from_stack(self):
        return self.data_stack.pop()

    def peek_from_stack(self):
        return self.data_stack.peek()

    def get_data_size(self):
        return self.data_size

    def add_in_output_buffer(self, value: str):
        self.output_buffer.append(value)

    def get_from_memory(self, index: int):
        return self.data[index]
