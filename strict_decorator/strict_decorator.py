import inspect
from functools import wraps


def strict(func):
    sign = inspect.signature(func)
    annotations = func.__annotations__
    @wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = sign.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param, value in bound_args.arguments.items():
            if param in annotations:
                expected_type = annotations[param]
                if type(value) is not expected_type:
                    raise TypeError(
                        f"Аргумент '{param}' должен быть типа '{expected_type.__name__}', "
                        f"а не '{type(value).__name__}'"

                    )
        return func(*args, **kwargs)
    return wrapper





@strict
def sum_two(a: int, b: int) -> int:
    return a + b


#print(sum_two(1, 2))  # >>> 3
#print(sum_two(1, 2.4))  # >>> TypeError
