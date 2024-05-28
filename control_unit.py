from isa import Opcode
from data_path import DataPath
from stack import Stack
from interruption import Interruption, InterruptionType


class ControlUnit:
    tick_counter: int = None
    data_path: DataPath = None
    program_counter: int = None
    current_operand: int = None
    interrupt_schedule: dict = dict()
    interruption_vector_addr = None
    interruption_section = False
    inter_buff = 0

    exit = False

    instruction_memory: list[int] = None

    interrupt_stack = None

    def __init__(self, dp: DataPath, memory: list[int], schedule: list, interrupt_vector_addr):
        self.tick_counter = 0
        self.program_counter = 0
        self.data_path = dp
        self.instruction_memory = memory
        self.interrupt_stack = Stack(len(memory))
        self.convert_schedule(schedule)

        self.interruption_vector_addr = interrupt_vector_addr

    def tick(self):
        self.tick_counter += 1

    def set_program_counter(self, value: int):
        self.program_counter = value

    def inc_program_counter(self):
        self.program_counter += 1

    def interrupt_handling(self):
        interrupt = self.interrupt_stack.pop()
        match interrupt.type.name:
            case InterruptionType.HLT.value:
                self.exit = True
                self.tick()
            case InterruptionType.INPUT.value:
                if self.interruption_vector_addr is not None:
                    self.program_counter = self.interruption_vector_addr - self.data_path.data_size
                    self.inter_buff = self.program_counter
                    self.check_interruption(interrupt)
                    self.interruption_section = True
                    while self.interruption_section:
                        self.decode_and_execute()

    def convert_schedule(self, schedule):
        for instruction in schedule:
            print(instruction)
            try:
                tick, value = instruction.split(" : ")
                self.interrupt_schedule[int(tick)] = str(value)
            except ValueError:
                tick = instruction.split(" :")[0]
                self.interrupt_schedule[int(tick)] = "brake"

    def check_interruption(self, interruption: Interruption):
        if interruption.type.value == "INPUT":
            if self.interrupt_schedule[self.tick_counter] != 'brake':
                self.data_path.data[0] = self.interrupt_schedule[self.tick_counter]
            else:
                print(self.data_path.output_buffer)
                exit(465)

    def start(self):
        while not self.exit:
            try:
                if self.interrupt_schedule[self.tick_counter] is not None:
                    interruption = Interruption(InterruptionType.INPUT)
                    self.interrupt_stack.push(interruption)
                    self.interrupt_handling()
            except Exception:
                if self.interrupt_stack.is_empty():
                    self.decode_and_execute()
                else:
                    self.interrupt_handling()

    def decode_and_execute(self):


        print("--------")
        print("tick")
        print(self.program_counter)
        print(self.instruction_memory)
        instruction = self.instruction_memory[self.program_counter]
        print(self.tick_counter)
        print(self.program_counter)
        print(instruction)
        print(self.data_path.data_stack)
        print(self.data_path.output_buffer)
        print("-------------")
        self.tick()

        opcode = instruction["opcode"]

        match opcode:
            case Opcode.PUSH:
                arg = instruction["arg"]
                self.data_path.data_stack.push(arg)
                self.tick()
            case Opcode.PUSH_VAL:
                arg = instruction["arg"]
                value = self.data_path.data[arg]
                self.tick()
                self.data_path.data_stack.push(value)
                self.tick()
            case Opcode.DUP:
                value = self.data_path.data_stack.peek()
                self.tick()

                self.data_path.data_stack.push(value)
                self.tick()
            case Opcode.POP:
                if self.data_path.data_stack.is_empty():
                    # INTERRUPTION
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
                print(b, a)
                if b == 0:
                    # ADD ERROR AND INTERRUPTION
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
            case Opcode.JMP:
                arg = instruction["arg"] - self.data_path.data_size
                self.set_program_counter(arg)
            case Opcode.PRINT:
                value = self.data_path.data_stack.pop()
                self.data_path.output_buffer.append(chr(value))
            case Opcode.COMPARE:
                print(self.data_path.data_stack)
                a = self.data_path.data_stack.peek()
                self.data_path.data_stack.pop()
                b = self.data_path.data_stack.peek()
                self.data_path.data_stack.push(a)
                self.data_path.alu.compare(a, b)
            case Opcode.JNE:
                if not self.data_path.alu.zero:
                    arg = instruction["arg"] - self.data_path.data_size
                    self.set_program_counter(arg)
                    self.data_path.alu.zero = False
            case Opcode.HLT:
                interruption = Interruption(InterruptionType.HLT)
                self.interrupt_stack.push(interruption)
                self.tick()
                print(self.data_path.output_buffer)
            case Opcode.NOP:
                self.tick()
            case Opcode.RETURN:
                self.interruption_section = False
                if self.interruption_vector_addr is not None:
                    self.program_counter, self.interruption_vector_addr = 0, self.interruption_vector_addr
            case Opcode.SAVE:
                self.data_path.output_buffer.append(chr(self.data_path.data[self.data_path.data_stack.pop()]))
            case Opcode.LOAD:
                arg = instruction["arg"]
                value = self.data_path.data[arg]
                self.tick()
                self.data_path.data_stack.push(ord(value))
                self.tick()
            case Opcode.SWAP:
                self.data_path.output_buffer.reverse()
        self.inc_program_counter()
