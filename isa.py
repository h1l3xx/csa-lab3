import struct
from enum import Enum
import json
from typing import Any

BITS = 32
MIN_SIGN = -(2 ** (BITS - 1))
MAX_SIGN = 2 ** (BITS - 1) - 1
MAX_UNSIGN = 2 ** BITS - 1


class Opcode(Enum):

    HLT = "HLT"
    NOP = "NOP"
    JMP = "JMP"
    JZ = "JZ"
    CALL = "CALL"
    # RET = 0b10000101

    PUSH = "PUSH"
    POP = "POP"
    LOAD = "LOAD"
    DROP = "DROP"
    SWAP = "SWAP"
    DUP = "DUP"

    INC = "INC"
    DEC = "DEC"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    NUMBER = "NUMBER"
    STRING = "STRING"
    BUFFER = "BUFFER"


opcode_values = [e.value for e in Opcode]


def write_code(target: str, code: list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]):
    with open(target, "w", encoding="utf-8") as file:
        # Почему не: `file.write(json.dumps(code, indent=4))`?
        # Чтобы одна инструкция была на одну строку.
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(source: str) -> list[int]:
    code = []
    with open(source, "rb") as f:
        short = f.read(4)
        while short:
            code.append(*struct.unpack("I", short))
            short = f.read(4)

    return code
