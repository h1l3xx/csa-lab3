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
    JNE = "JNE"
    CALL = "CALL"
    SAVE = "SAVE"
    # RET = 0b10000101

    PUSH = "PUSH"
    PUSH_VAL = "PUSH_VAL"
    POP = "POP"
    LOAD = "LOAD"
    DROP = "DROP"
    SWAP = "SWAP"
    DUP = "DUP"
    COMPARE = "COMPARE"

    INC = "INC"
    DEC = "DEC"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"

    INPUT = 0
    OUTPUT = 1

    NUMBER = "NUMBER"
    STRING = "STRING"
    BUFFER = "BUFFER"

    RETURN = "RETURN"

    DATA = "DATA"
    DATA_SIZE = "DATA_SIZE"

    PRINT = "PRINT"


opcode_values = [e.value for e in Opcode]


def write_code(target: str, code: list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]):
    with open(target, "w", encoding="utf-8") as file:
        buf = []
        for instr in code:
            buf.append(json.dumps(instr))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(source: str) -> list[int]:
    with open(source, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        # Конвертация строки в Opcode
        instr["opcode"] = Opcode(instr["opcode"])

    return code


def decode_data_line(line) -> int | None:
    if line["opcode"] != Opcode.DATA_SIZE.value:
        return int(line["arg"])
    else:
        return None


def read_data(source: str) -> list[str]:
    with open(source, encoding="utf-8") as file:
        data = file.read()
    return data.split("\n")
