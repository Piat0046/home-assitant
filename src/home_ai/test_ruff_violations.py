"""Ruff test file with intentional violations."""


def bad_function(x, y):
    """Function with style violations."""
    unused_var = "hello"
    result = x + y
    if result == True:
        print("yes")
    return result


class BadClass:
    def __init__(self, name):
        self.name = name

    def method(self):
        l = [1, 2, 3]
        d = dict(a=1, b=2)
        return l, d
