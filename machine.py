from __future__ import annotations

import argparse


from data_path import DataPath
from control_unit import ControlUnit
from isa import decode_data_line, read_code, read_data
from logger import Logger, LogLevel, Place


def simulate(input_file: str, stack_size: int, schedule: str | None, limit: int, log_file: str):
    read = read_code(input_file)
    logger = Logger()
    logger.set_log_filepath(log_file)
    interruption_vector_addr = None

    if read[0]["index"] == -1:
        data_size = read[1]["arg"]
        data = read[2 : data_size + 2]

        interruption_vector_addr = read[0]["arg"]
        code = read[data_size + 2 :]
    else:
        data_size = read[0]["arg"]

        data = read[1 : data_size + 1]
        code = read[data_size + 1 :]

    data_memory = []

    for i in range(data_size):
        decode = decode_data_line(data[i])

        if decode is not None:
            data_memory.append(decode)

    data_path = DataPath(data_memory, int(stack_size))

    if schedule is not None:
        read_schedule = read_data(schedule)
        logger.log(LogLevel.INFO, Place.INPUT, f"Schedule : {read_schedule}")
        control_unit = ControlUnit(data_path, code, read_schedule, interruption_vector_addr, int(limit))
    else:
        control_unit = ControlUnit(data_path, code, None, interruption_vector_addr, int(limit))
    control_unit.set_logger(logger)
    control_unit.start()
    print("".join(control_unit.data_path.output_buffer))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Симуляция процессора")
    parser.add_argument("code_file")
    parser.add_argument("input_file")
    parser.add_argument("stack_size")
    parser.add_argument("ticks_limit")
    parser.add_argument("log_file")
    args = parser.parse_args()

    simulate(args.code_file, args.stack_size, args.input_file, args.ticks_limit, args.log_file)
