class Stack:
    max_size = None

    def __init__(self, size):
        self.items: list = []
        self.max_size = size

    def is_empty(self) -> bool:
        return self.items == []

    def push(self, item):
        if len(self.items) < self.max_size:
            self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def size(self) -> int:
        return len(self.items)

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return str(self)
