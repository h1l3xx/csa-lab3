from __future__ import annotations

from typing import ClassVar

from data_path import DataPath
from interruption import Interruption, InterruptionType
from isa import Opcode
from logger import Logger, LogLevel, Place
from stack import Stack


class ControlUnit:
    tick_counter: int = None
    data_path: DataPath = None
    program_counter: int = None
    current_operand: int = None
    interruption_vector_addr = None
    interruption_section = False
    inter_buff = 0
    limit = None

    interrupt_schedule: ClassVar[dict | None] = dict()

    instruction_counter: int = 0
    logger: Logger = None

    exit = False

    instruction_memory: list[int] = None

    interrupt_stack = None

    def __init__(self, dp: DataPath, memory: list[int], schedule: list | None, interrupt_vector_addr, limit: int):
        self.tick_counter = 0
        self.program_counter = 0
        self.data_path = dp
        self.instruction_memory = memory
        self.interrupt_stack = Stack(len(memory))

        if schedule is not None:
            self.convert_schedule(schedule)
        else:
            self.interrupt_schedule = None

        self.limit = limit
        self.interruption_vector_addr = interrupt_vector_addr

    def set_logger(self, logger: Logger):
        self.logger = logger

    def tick(self):
        self.tick_counter += 1

    def set_program_counter(self, value: int):
        self.program_counter = value

    def inc_program_counter(self):
        self.program_counter += 1

    def interrupt_handling(self):
        self.logger.log(LogLevel.DEBUG, Place.INTER, f"Have {self.interrupt_stack.size()} interruptions")
        interrupt = self.interrupt_stack.pop()
        self.logger.log(LogLevel.DEBUG, Place.INTER, f"Processing {interrupt}")

        match interrupt.type.name:
            case InterruptionType.HLT.value:
                self.exit = True
                self.tick()
                self.logger.log(LogLevel.INFO, Place.SYSTEM, "Halting")

            case InterruptionType.INPUT.value:
                if self.interruption_vector_addr is not None:
                    self.program_counter = self.interruption_vector_addr - self.data_path.data_size - 1

                    self.check_interruption(interrupt)
                    self.interruption_section = True

                    while self.interruption_section:
                        self.decode_and_execute()

    def convert_schedule(self, schedule):
        for instruction in schedule:
            try:
                tick, value = instruction.split(" : ")
                self.interrupt_schedule[int(tick)] = str(value)
            except ValueError:
                tick = instruction.split(" :")[0]
                self.interrupt_schedule[int(tick)] = "#"

    def check_interruption(self, interruption: Interruption):
        if interruption.type.value == "INPUT":
            if self.interrupt_schedule[self.tick_counter] == "#":
                self.data_path.push_in_stack(35)
                self.data_path.load_in_memory(0, 35)
                self.program_counter += 2
            else:
                value = self.interrupt_schedule[self.tick_counter]
                self.data_path.load_in_memory(0, ord(value))

    def start(self):
        self.logger.log(LogLevel.INFO, Place.SYSTEM, "Starting execution")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Instructions memory: {self.instruction_memory}")
        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Data memory: {self.data_path.data}")

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

        self.logger.log(LogLevel.INFO, Place.SYSTEM, f"Program finished: ticks = {self.tick_counter}," f" instructions executed = {self.instruction_counter}")

    def decode_and_execute(self):
        self.instruction_counter += 1
        instruction = self.instruction_memory[self.program_counter]
        self.tick()
        if self.tick_counter >= self.limit:
            interruption = Interruption(InterruptionType.HLT)
            self.interrupt_stack.push(interruption)

        opcode = instruction["opcode"]

        self.logger.log(LogLevel.DEBUG, Place.SYSTEM, f"Data stack: {self.data_path.data_stack}")

        try:
            arg = instruction["arg"]
            (self.logger.log(LogLevel.INFO, Place.INSTR, f"Processing {opcode.name} {instruction['arg']}"))
        except KeyError:
            self.logger.log(LogLevel.INFO, Place.INSTR, f"Processing {opcode.name}")

        match opcode:
            case Opcode.PUSH:
                arg = instruction["arg"]
                self.data_path.push_in_stack(arg)
                self.tick()

                self.inc_program_counter()
            case Opcode.PUSH_VAL:
                arg = instruction["arg"] + 1
                value = self.data_path.data[arg]
                self.tick()

                self.data_path.push_in_stack(value)
                self.tick()

                self.inc_program_counter()
            case Opcode.DUP:
                value = self.data_path.peek_from_stack()
                self.tick()

                self.data_path.push_in_stack(value)
                self.tick()

                self.inc_program_counter()

            case Opcode.POP:
                if self.data_path.data_stack.is_empty():
                    interruption = Interruption(InterruptionType.HLT)
                    self.interrupt_stack.push(interruption)
                    self.tick()

                else:
                    self.data_path.pop_from_stack()
                    self.tick()

                self.tick()

                self.inc_program_counter()
            case Opcode.ADD:
                b = self.data_path.pop_from_stack()
                self.tick()

                a = self.data_path.pop_from_stack()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Adding {a} and {b}")

                self.data_path.alu.add(a, b)
                self.tick()

                result = self.data_path.alu.result
                self.data_path.push_in_stack(result)
                self.tick()

                self.inc_program_counter()

            case Opcode.SUB:
                b = self.data_path.pop_from_stack()
                self.tick()

                a = self.data_path.pop_from_stack()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Subtracting {a} and {b}")

                self.data_path.alu.sub(a, b)
                self.tick()

                result = self.data_path.alu.result
                self.data_path.push_in_stack(result)
                self.tick()

                self.inc_program_counter()
            case Opcode.MUL:
                b = self.data_path.pop_from_stack()
                self.tick()

                a = self.data_path.pop_from_stack()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Multiplying {a} and {b}")

                self.data_path.alu.mul(a, b)
                self.tick()

                result = self.data_path.alu.result
                self.data_path.push_in_stack(result)
                self.tick()

                self.inc_program_counter()

            case Opcode.DIV:
                a = self.data_path.pop_from_stack()
                self.tick()

                b = self.data_path.pop_from_stack()
                self.tick()
                if b == 0:
                    interruption = Interruption(InterruptionType.HLT)
                    self.interrupt_stack.push(interruption)
                    self.tick()
                else:
                    self.logger.log(LogLevel.DEBUG, Place.ALU, f"Dividing {a} and {b}")

                    self.data_path.alu.div(a, b)
                    self.tick()

                    result = self.data_path.alu.result
                    self.data_path.push_in_stack(result)
                    self.tick()

                self.tick()

                self.inc_program_counter()

            case Opcode.INC:
                a = self.data_path.pop_from_stack()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Incrementing {a}")

                self.data_path.alu.add(a, 1)
                self.tick()

                result = self.data_path.alu.result
                self.data_path.push_in_stack(result)
                self.tick()

                self.inc_program_counter()

            case Opcode.DEC:
                a = self.data_path.pop_from_stack()
                self.tick()

                self.logger.log(LogLevel.DEBUG, Place.ALU, f"Decrementing {a}")

                self.data_path.alu.sub(a, 1)
                self.tick()

                result = self.data_path.alu.result
                self.data_path.push_in_stack(result)
                self.tick()

                self.inc_program_counter()

            case Opcode.JMP:
                arg = instruction["arg"] - self.data_path.data_size - 1
                self.set_program_counter(arg)
                self.tick()

                self.interruption_section = False
                self.tick()

            case Opcode.JEQ:
                if self.data_path.alu.result == 0:
                    arg = instruction["arg"] - self.data_path.get_data_size() - 1
                    self.set_program_counter(arg)
                    self.tick()

                    self.data_path.alu.zero = False
                    self.tick()
                else:
                    self.tick()
                    self.inc_program_counter()

            case Opcode.PRINT:
                value = self.data_path.pop_from_stack()
                self.tick()

                self.data_path.add_in_output_buffer(chr(value))
                self.tick()

                self.inc_program_counter()

            case Opcode.SAVE:
                value = self.data_path.pop_from_stack()
                self.tick()

                index = self.data_path.peek_from_stack()
                self.tick()

                self.tick()

                self.data_path.load_in_memory(index, value)
                self.tick()

                self.inc_program_counter()

            case Opcode.PRINT_BY_INDEX:
                index = self.data_path.peek_from_stack() + 2
                self.tick()

                value = self.data_path.get_from_memory(index)
                self.tick()

                self.data_path.add_in_output_buffer(chr(value))
                self.tick()

                self.inc_program_counter()
            case Opcode.COMPARE:
                a = self.data_path.peek_from_stack()
                self.tick()

                self.data_path.pop_from_stack()
                self.tick()

                b = self.data_path.peek_from_stack()
                self.tick()

                self.data_path.push_in_stack(a)
                self.tick()

                self.data_path.alu.compare(a, b)
                self.tick()

                self.inc_program_counter()
            case Opcode.PRINT_VAL:
                value = self.data_path.data_stack.pop()
                self.tick()

                self.data_path.add_in_output_buffer(str(value))
                self.tick()

                self.inc_program_counter()

            case Opcode.JNE:
                if not self.data_path.alu.zero:
                    arg = instruction["arg"] - self.data_path.get_data_size()
                    self.set_program_counter(arg)
                    self.tick()

                    self.data_path.alu.zero = False
                    self.tick()
                else:
                    self.inc_program_counter()

            case Opcode.HLT:
                interruption = Interruption(InterruptionType.HLT)
                self.interrupt_stack.push(interruption)
                self.interruption_section = False
                self.tick()
                self.inc_program_counter()

            case Opcode.NOP:
                self.tick()
                self.inc_program_counter()

            case Opcode.LOAD:
                arg = instruction["arg"]
                value = self.data_path.get_from_memory(arg)
                self.tick()

                self.data_path.data_stack.push(value)
                self.tick()

                self.inc_program_counter()

            case Opcode.SWAP:
                a = self.data_path.data_stack.pop()
                self.tick()

                b = self.data_path.data_stack.pop()
                self.tick()

                self.data_path.data_stack.push(a)
                self.tick()

                self.data_path.data_stack.push(b)
                self.tick()

                self.inc_program_counter()
