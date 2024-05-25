import argparse
from isa import read_code


def start(input_file: str):
    read = read_code(input_file)
    data_size = read[0]["arg"]
    data = read[1:data_size+1]

    code = read[data_size+1:]

    print(data)
    print(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Симуляция процессора")
    parser.add_argument("code_file", help="Имя файла с кодом")

    args = parser.parse_args()

    start(args.code_file)
