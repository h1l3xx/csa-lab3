from __future__ import annotations

import json
from enum import Enum
from typing import Any

BITS = 32
MIN_SIGN = -(2 ** (BITS - 1))
MAX_SIGN = 2 ** (BITS - 1) - 1
MAX_UNSIGN = 2**BITS - 1


class Opcode(Enum):
    HLT = "HLT"
    NOP = "NOP"
    JMP = "JMP"
    JNE = "JNE"
    JEQ = "JEQ"
    SAVE = "SAVE"

    PUSH = "PUSH"
    PUSH_VAL = "PUSH_VAL"
    POP = "POP"
    LOAD = "LOAD"
    SWAP = "SWAP"
    DUP = "DUP"
    COMPARE = "COMPARE"

    PRINT_BY_INDEX = "PRINT_BY_INDEX"

    PRINT_VAL = "PRINT_VAL"
    PRINT = "PRINT"

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

    DATA = "DATA"
    DATA_SIZE = "DATA_SIZE"


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
        # Line to Opcode
        instr["opcode"] = Opcode(instr["opcode"])

    return code


def decode_data_line(line) -> int | None:
    if line["opcode"] != Opcode.DATA_SIZE.value:
        return int(line["arg"])
    return None


def read_data(source: str) -> list[str]:
    with open(source, encoding="utf-8") as file:
        data = file.read()
    return data.split("\n")
