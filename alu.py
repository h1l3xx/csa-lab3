class ALU:
    def __init__(self):
        self.result = None
        self.zero = False
        self.negative = False

    def add(self, a: int, b: int):
        self.result = a + b
        self.zero = self.result == 0
        self.negative = self.result < 0

    def sub(self, a: int, b: int):
        self.result = a - b
        self.zero = self.result == 0
        self.negative = self.result < 0

    def mul(self, a: int, b: int):
        self.result = a * b
        self.zero = self.result == 0
        self.negative = self.result < 0

    def div(self, a: int, b: int):
        self.result = a // b
        self.zero = self.result == 0
        self.negative = self.result < 0

    def compare(self, a: int, b: int):
        if a > b:
            self.result = 1
        elif a < b:
            self.result = -1
        else:
            self.result = 0

        self.zero = self.result == 0
        self.negative = self.result < 0
