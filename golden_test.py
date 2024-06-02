import contextlib
import io
import os
import tempfile

import machine
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.lisp")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.o")
        log_file = os.path.join(tmpdirname, "log.txt")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        try:
            with open(input_stream, "w", encoding="utf-8") as file:
                file.write(golden["in_stdin"])
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                translator.main(source, target)
                print("============================================================")
                machine.simulate(target, 100, input_stream, 100000, log_file)
        except TypeError:
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                translator.main(source, target)
                print("============================================================")
                machine.simulate(target, 100, None, 100000, log_file)

        # Запускаем транслятор и собираем весь стандартный вывод в переменную
        # stdout

        # Выходные данные также считываем в переменные.
        with open(target, encoding="utf-8") as file:
            code = file.read()
        with open(log_file, encoding="utf-8") as file:
            log = file.read().strip()

        # Проверяем, что ожидания соответствуют реальности.
        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert log == golden.out["out_log"]
