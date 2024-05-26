import argparse

from control_unit import ControlUnit
from isa import read_code, decode_data_line
from data_path import DataPath


def start(input_file: str, stack_size: int):
    read = read_code(input_file)
    data_size = read[0]["arg"]
    data = read[1:data_size + 1]

    code = read[data_size + 1:]

    data_memory = []
    for i in range(data_size):
        decode = decode_data_line(data[i])
        if decode is not None:
            data_memory.append(decode)

    data_path = DataPath(data_memory, int(stack_size))
    control_unit = ControlUnit(data_path, code)

    while not control_unit.exit:
        if control_unit.interrupt_stack.is_empty():
            control_unit.decode_and_execute()
        else:
            control_unit.interrupt_handling()
    print("Program finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Симуляция процессора")
    parser.add_argument("code_file", help="Имя файла с кодом")
    parser.add_argument("stack_size")
    args = parser.parse_args()

    start(args.code_file, args.stack_size)
