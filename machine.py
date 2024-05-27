import argparse

from control_unit import ControlUnit
from isa import read_code, decode_data_line, read_data
from data_path import DataPath


def simulate(input_file: str, stack_size: int, schedule: str):
    read = read_code(input_file)
    interruption_vector_addr = None
    read_schedule = read_data(schedule)
    if read[0]["index"] == -1:
        data_size = read[1]["arg"]
        data = read[2:data_size + 2]
        interruption_vector_addr = read[0]["arg"]
    else:
        data_size = read[0]["arg"]
        data = read[1:data_size + 1]

    code = read[data_size + 2:]
    data_memory = []
    for i in range(data_size):
        decode = decode_data_line(data[i])
        if decode is not None:
            data_memory.append(decode)

    data_path = DataPath(data_memory, int(stack_size))
    control_unit = ControlUnit(data_path, code, read_schedule, interruption_vector_addr)

    control_unit.start()

    print("Program finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Симуляция процессора")
    parser.add_argument("code_file", help="Имя файла с кодом")
    parser.add_argument("input_file")
    parser.add_argument("stack_size")
    args = parser.parse_args()

    simulate(args.code_file, args.stack_size, args.input_file)
