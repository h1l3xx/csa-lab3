import argparse

import isa
from isa import *
from isa import Opcode


def get_meaningful_token(line: str) -> str:
    return line.split(";", 1)[0].strip()


def translate_data_part(token: str) -> tuple[str, list[str | int | Opcode]]:
    print(token)
    variable, str_opcode, arg = token.split(" ", 2)
    opcode = Opcode[str_opcode]
    assert opcode in [
        Opcode.NUMBER,
        Opcode.STRING,
        Opcode.BUFFER,
    ], f"Wrong instruction in data part {token}"

    if opcode == Opcode.NUMBER:
        num = int(arg)
        assert MIN_SIGN <= num <= MAX_SIGN, f"Wrong instruction argument: {token}"
        if num < 0:
            num = MAX_UNSIGN + num
        tokens = [num]
    elif opcode == Opcode.STRING:
        start = str(len(arg)) + " MEM"
        tokens = [start] + [ord(c) for c in arg]
    elif opcode == Opcode.BUFFER:
        num = int(arg)
        assert 1 <= num <= MAX_UNSIGN, f"Wrong instruction argument: {token}"
        tokens = [0] * num
    else:
        raise ValueError(f"Wrong opcode: {opcode}")

    return variable, tokens


def translate_code_part(token: str) -> list[str | int | Opcode]:
    tokens = []
    if " " in token:  # instruction with argument
        sub_tokens = token.split(" ")
        assert (
            len(sub_tokens) == 2
        ), f"Invalid instruction, check arguments amount: {token}"
        opcode = Opcode[sub_tokens[0]]
        assert opcode in [
            Opcode.PRINT,
            Opcode.PUSH,
            Opcode.PUSH_VAL,
            Opcode.JMP,
            Opcode.JZ,
            Opcode.CALL,
            Opcode.JNE
        ], f"Instruction shouldn't have an argument: {token}"
        arg = sub_tokens[1]
        if arg.isdigit():
            arg = int(arg)
            assert MIN_SIGN <= arg < MAX_SIGN, f"16-bit numbers only {token}"
            if arg < 0:
                arg = MAX_UNSIGN + arg
        if arg == "OUTPUT":
            arg = 3
        elif arg == "INPUT":
            arg = 2
        print(arg)

        tokens += [opcode, arg]

    else:
        # instruction without argument
        opcode = Opcode[token]
        tokens.append(opcode)

    return tokens


def translate_stage_1(
    text: str,
) -> tuple[dict[str, int], dict[str, int], list[str | int | Opcode]]:
    variables = {}
    labels = {}
    tokens = [0]  # first token is data part length

    data_stage = True

    data_counter = 0
    program_counter = 0
    for line in text.splitlines():
        token = get_meaningful_token(line)
        if not data_stage and token == ".data":
            raise ValueError(".data shouldn't't be there")
        if token == "" or token == ".data:":
            continue

        if token == ".code:":
            tokens[0] = data_counter  # set first word as data part length
            data_stage = False
            program_counter = data_counter
            continue

        if data_stage:
            variable, data_part = translate_data_part(token)
            assert variable not in variables, f"Redefinition of variable: {variable}"
            variables[variable] = data_counter
            data_counter += len(data_part)
            tokens += data_part
        else:
            if token.endswith(":"):  # label
                label = token.strip(":")
                assert label not in labels, f"Redefinition of label: {label}"
                labels[label] = program_counter
            else:
                code_part = translate_code_part(token)
                program_counter += len(code_part)
                tokens += code_part

    return labels, variables, tokens


def translate_stage_2(
    labels: dict[str, int], variables: dict[str, int], tokens: list[str | int | Opcode]
) -> list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]:
    labels_indexes = []
    code = []
    data = []
    for label in labels:
        labels_indexes.append(labels[label])
        if label == "interrupt":
            data.insert(0, {"index": -1, "opcode": Opcode.DATA.value, "arg": labels[label]})

    data_part = True
    for ind, token in enumerate(tokens):
        if ind in labels_indexes:
            code.append({"index": ind, "opcode": Opcode.NOP.value})
        if isinstance(token, Opcode):
            data_part = False
            if token in [Opcode.JMP, Opcode.JZ, Opcode.CALL, Opcode.PUSH, Opcode.PUSH_VAL, Opcode.JNE, Opcode.PRINT]:
                next_token = tokens[ind + 1]
                if next_token in labels:
                    next_token = labels[next_token]
                elif next_token in variables:
                    next_token = variables[next_token]
                code.append(
                    {"index": ind, "opcode": token.value, "arg": next_token}
                )
            else:
                code.append(
                    {"index": ind, "opcode": token.value}
                )
            if token in [Opcode.JMP, Opcode.JNE, Opcode.PUSH]:
                code.append(
                    {"index": ind + 1, "opcode": Opcode.NOP.value}
                )
        else:
            if data_part:
                if isinstance(token, int):
                    assert 0 <= token <= MAX_UNSIGN, f"16-bit numbers only {token}"
                    data.append({"index": ind, "opcode": Opcode.DATA.value, "arg": token})
                elif " MEM" in token:
                    data.append({"index": ind, "opcode": Opcode.DATA_SIZE.value, "arg": token.split(" ")[0]})
    data[1] = {"index": 0, "opcode": Opcode.DATA_SIZE.value, "arg": (len(data) - 2)}
    code = data + code

    return code


def translate(text: str) -> list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]:
    labels, variables, tokens = translate_stage_1(text)
    code = translate_stage_2(labels, variables, tokens)

    return code


def main(source: str, target: str):
    with open(source, "r") as f:
        text = f.read()

    code = translate(text)
    print(code)
    write_code(target, code)
    print("LoC:", len(text.split("\n")), "Code bytes:", len(code) * BITS // 8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Трансляция кода")
    parser.add_argument("source_file", help="Имя файла с кодом")
    parser.add_argument("target_file", help="Имя выходного файла")

    args = parser.parse_args()

    main(args.source_file, args.target_file)
