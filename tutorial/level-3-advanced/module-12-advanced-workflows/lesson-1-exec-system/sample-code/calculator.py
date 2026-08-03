"""A simple calculator module with a deliberate bug."""


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: int, b: int) -> float:
    # Bug: no zero-division check
    return a / b


def power(base: int, exp: int) -> int:
    return base**exp


if __name__ == "__main__":
    print(f"add(2, 3) = {add(2, 3)}")
    print(f"subtract(10, 4) = {subtract(10, 4)}")
    print(f"multiply(3, 7) = {multiply(3, 7)}")
    print(f"divide(10, 0) = {divide(10, 0)}")  # Will crash
