import argparse

from isa import *
from isa import Opcode


def get_meaningful_token(line: str) -> str:
    return line.split(";", 1)[0].strip()


def translate_data_part(token: str, data_length: int) -> tuple[int, Any, list[int | Any] | list[int | str] | list[int]]:

    current_data = data_length
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
        if '"' in arg:
            current_arg = arg[1:-1]
        else:
            current_arg = arg
        if current_data != 0:
            current_data += len(current_arg) + 2
        else:
            current_data += len(current_arg)
        start = str(current_data) + " MEM"
        tokens = [start] + [ord(c) for c in current_arg]
    elif opcode == Opcode.BUFFER:
        num = int(arg)
        assert 1 <= num <= MAX_UNSIGN, f"Wrong instruction argument: {token}"
        tokens = [0] * num
    else:
        raise ValueError(f"Wrong opcode: {opcode}")

    return current_data, variable, tokens


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
            Opcode.JNE,
            Opcode.LOAD,
            Opcode.JEQ,
            Opcode.PRINT_VAL
        ], f"Instruction shouldn't have an argument: {token}"
        arg = sub_tokens[1]
        if arg.isdigit():
            arg = int(arg)
            assert MIN_SIGN <= arg < MAX_SIGN, f"16-bit numbers only {token}"
            if arg < 0:
                arg = MAX_UNSIGN + arg
        if arg == "OUTPUT":
            arg = 1
        elif arg == "INPUT":
            arg = 0
        print(arg)

        tokens += [[opcode, arg]]

    else:
        # instruction without argument
        opcode = Opcode[token]
        tokens.append(opcode)

    return tokens


def translate_stage_1(
        text: str,
) -> tuple[dict[str, int], list[str | int | Opcode]]:
    variables = {}
    tokens = [0]  # first token is data part length

    data_stage = True
    data_counter = 0
    program_counter = 0
    data_length = 0
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
            data_length, variable, data_part = translate_data_part(token, data_length)
            assert variable not in variables, f"Redefinition of variable: {variable}"
            variables[variable] = data_counter
            data_counter += len(data_part)
            tokens += data_part
        else:
            if token.endswith(":"):  # label
                label = token.strip(":")
                tokens.append(label)
            else:
                code_part = translate_code_part(token)
                program_counter += len(code_part)
                tokens += code_part

    return variables, tokens


def translate_stage_2(
        variables: dict[str, int], tokens: list[str | int | Opcode]
) -> list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]:

    code = []
    data = []
    labels = {}

    data_length = int(tokens[0])

    data.append({"index": 0, "opcode": Opcode.DATA_SIZE.value, "arg": data_length})

    for i in range(1, data_length + 1):
        token = tokens[i]
        if isinstance(token, int):
            assert 0 <= token <= MAX_UNSIGN, f"16-bit numbers only {token}"
            data.append({"index": i, "opcode": Opcode.DATA.value, "arg": token})
        elif " MEM" in token:
            data.append({"index": i, "opcode": Opcode.DATA_SIZE.value, "arg": token.split(" ")[0]})

    code_size = len(tokens) - data_length

    for i in range(data_length + code_size - 1, data_length, -1):
        token = tokens[i]
        if isinstance(token, str):
            labels[token] = i

    for i in range(data_length + 1, data_length + code_size):
        token = tokens[i]

        if isinstance(token, Opcode):
            code.append({"index": i, "opcode": token.value})

        else:
            if isinstance(token, str):
                continue
            else:
                opcode = token[0].value
                arg = token[1]
                if arg in labels:
                    code.append({"index": i, "opcode": opcode, "arg": labels[arg]})
                elif arg in variables:
                    code.append({"index": i, "opcode": opcode, "arg": variables[arg] + 1})
                else:
                    code.append({"index": i, "opcode": opcode, "arg": arg})

    for i in range(len(labels)):

        label, index = labels.popitem()

        if label == "interrupt":
            data.insert(0, {"index": -1, "opcode": Opcode.DATA.value, "arg": index})

        code.insert(index - data_length - 1, {"index": index, "opcode": Opcode.NOP.value})

    code = data + code
    return code


def translate(text: str) -> list[dict[str, int | str | Opcode | Any] | dict[str, int | Any]]:
    variables, tokens = translate_stage_1(text)
    code = translate_stage_2(variables, tokens)

    return code


def main(source: str, target: str):
    with open(source, "r") as f:
        text = f.read()

    code = translate(text)
    write_code(target, code)

    print("LoC:", len(text.split("\n")), "Code bytes:", len(code) * BITS // 8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file")
    parser.add_argument("target_file")

    args = parser.parse_args()

    main(args.source_file, args.target_file)
