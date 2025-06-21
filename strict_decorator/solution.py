from strict_decorator import strict
import pytest


def sum_two(a: int, b: int) -> int:
    return a + b


def concat(a: str, b: str) -> str:
    return a + b


def invert(flag: bool) -> bool:
    return not flag


def divide(a: float, b: float) -> float:
    return a / b


def power(base: int, exp: float) -> float:
    return base ** exp


def type_mixer(a: bool, b: int, c: float, d: str) -> tuple:
    return (a, b, c, d)


def get_answer() -> str:
    return "42"


@pytest.mark.parametrize("func, args, kwargs, expected", [
    (sum_two, (1, 2), {}, 3),
    (concat, ("Hello", "World"), {}, "HelloWorld"),
    (invert, (True,), {}, False),
    (divide, (4.0, 2.0), {}, 2.0),
    (get_answer, (), {}, "42"),
    (power, (2,), {"exp": 3.0}, 8.0),
    (type_mixer, (True, 42, 3.14, "hello"), {}, (True, 42, 3.14, "hello")),
])
def test_strict_decorator_success(func, args, kwargs, expected):
    decorated_func = strict(func)
    result = decorated_func(*args, **kwargs)
    assert result == expected


@pytest.mark.parametrize("func, args, kwargs, error_parts", [
    (sum_two, (1, True), {}, ['Аргумент', 'b', 'типа', 'int', 'не', 'bool']),
    (concat, (100, "%"), {}, ['Аргумент', 'a', 'типа', 'str', 'не', 'int']),
    (invert, (1,), {}, ['Аргумент', 'flag', 'типа', 'bool', 'не', 'int']),
    (divide, (4.0, 2), {}, ['Аргумент', 'b', 'типа', 'float', 'не', 'int']),
    (power, (2.0,), {"exp": 3}, ['Аргумент', 'base', 'типа', 'int', 'не', 'float']),
    (type_mixer, (1, 42, 3.14, "hello"), {}, ['Аргумент', 'a', 'типа', 'bool', 'не', 'int']),
    (type_mixer, (True, 4.2, 3.14, "hello"), {}, ['Аргумент', 'b', 'типа', 'int', 'не', 'float']),
    (type_mixer, (True, 42, 3, "hello"), {}, ['Аргумент', 'c', 'типа', 'float', 'не', 'int']),
])
def test_strict_decorator_failure(func, args, kwargs, error_parts):
    decorated_func = strict(func)
    with pytest.raises(TypeError) as excinfo:
        decorated_func(*args, **kwargs)

    error_msg = str(excinfo.value)
    for part in error_parts:
        assert part in error_msg, f"Ожидалась часть '{part}' в сообщении об ошибке: '{error_msg}'"