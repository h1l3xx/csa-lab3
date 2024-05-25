class Stack:
    def __init__(self):
        self.items: list = []

    def is_empty(self) -> bool:
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        else:
            return None

    def size(self) -> int:
        return len(self.items)

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return str(self)
