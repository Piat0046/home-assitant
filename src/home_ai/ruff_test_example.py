"""Ruff test file - intentional violations for CI testing."""


def process_data(data, options):
    """Process data with violations."""
    x = 1
    y = 2
    result = x + y
    unused_variable = "this is never used"

    if result == True:
        return "yes"
    elif result == False:
        return "no"

    items = dict(a=1, b=2, c=3)
    return items


class DataProcessor:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def process(self):
        l = [1, 2, 3, 4, 5]
        return l
