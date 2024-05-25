from data_path import DataPath
from isa import Opcode


class ControlUnit:
    tick_counter: int = None
    data_path: DataPath = None
    program_counter: int = None
    current_operand: int = None

    instruction_memory: list[str] = None

    def __init__(self, dp: DataPath, memory: list[str]):
        self.tick_counter = 0
        self.program_counter = 0
        self.data_path = dp
        self.instruction_memory = memory

    def tick(self):
        self.tick_counter += 1

    def set_program_counter(self, value: int):
        self.program_counter = value

    def inc_program_counter(self):
        self.program_counter += 1

    def decode_and_execute(self):
        instruction = self.instruction_memory[self.program_counter]

        self.tick()

        opcode = "opcode"
        operand = 1
        optype = "optype"

        match opcode:
            case Opcode.PUSH:
                self.data_path.data_stack.push(operand)
                self.tick()
            case Opcode.DUP:
                value = self.data_path.data_stack.peek()
                self.tick()

                self.data_path.data_stack.push(value)
                self.tick()
            case Opcode.POP:
                if self.data_path.data_stack.is_empty():
                    # НУЖНО ДОБАВИТЬ ПРЕРЫВНИЯ
                    self.tick()
                else:
                    self.data_path.data_stack.pop()
                    self.tick()
                self.tick()
            case Opcode.ADD:
                b = self.data_path.data_stack.pop()
                self.tick()
                a = self.data_path.data_stack.pop()
                self.tick()

                # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Adding {a} and {b}")

                self.data_path.alu.add(a, b)
                self.tick()
                self.data_path.data_stack.push(self.data_path.alu.result)
                self.tick()

            case Opcode.SUB:
                b = self.data_path.data_stack.pop()
                self.tick()
                a = self.data_path.data_stack.pop()
                self.tick()

                # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Subtracting {a} and {b}")

                self.data_path.alu.sub(a, b)
                self.tick()
                self.data_path.data_stack.push(self.data_path.alu.result)
                self.tick()

            case Opcode.MUL:
                b = self.data_path.data_stack.pop()
                self.tick()
                a = self.data_path.data_stack.pop()
                self.tick()

                # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Multiplying {a} and {b}")

                self.data_path.alu.mul(a, b)
                self.tick()
                self.data_path.data_stack.push(self.data_path.alu.result)
                self.tick()

            case Opcode.DIV:
                b = self.data_path.data_stack.pop()
                self.tick()
                a = self.data_path.data_stack.pop()
                self.tick()

                if b == 0:
                    # ДОБАВИТЬ ОШИБКУ И ПРЕРЫВАНИЯ
                    self.tick()
                else:
                    # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Dividing {a} and {b}")

                    self.data_path.alu.div(a, b)
                    self.tick()
                    self.data_path.data_stack.push(self.data_path.alu.result)
                    self.tick()

                self.tick()

            case Opcode.INC:
                a = self.data_path.data_stack.pop()
                self.tick()

                # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Incrementing {a}")

                self.data_path.alu.add(a, 1)
                self.tick()
                self.data_path.data_stack.push(self.data_path.alu.result)
                self.tick()

            case Opcode.DEC:
                a = self.data_path.data_stack.pop()
                self.tick()

                # self.logger.log(LogLevel.DEBUG, Place.ALU, f"Decrementing {a}")

                self.data_path.alu.sub(a, 1)
                self.tick()
                self.data_path.data_stack.push(self.data_path.alu.result)
                self.tick()
