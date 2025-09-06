from functools import wraps


class Result:
    """Class to represent the result of a function with preconditions or postconditions."""

    pass


class Success(Result):
    """Class to represent a successful result."""

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"Success({self.value})"


class Error(Result):
    """Class to represent an error result."""

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def __repr__(self):
        return f"Error({self.function.__name__} given args, kwargs: {self.args})"


def precondition(*functions):
    """Decorator to specify a precondition for a function.

    Args:
        functions (callable): A list of callables that take the same arguments as the decorated function
                        and return True if the precondition is met, False otherwise.

    Returns:
        callable: The decorated function with the precondition check.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for pre in functions:
                result = pre(*args, **kwargs)
                if not result:
                    return Error(func, (args, kwargs))
            return Success(func(*args, **kwargs))

        return wrapper

    return decorator


def postcondition(*functions):
    """Decorator to specify a postcondition for a function.

    Args:
        functions (callable): A list of callables that take the same arguments as the decorated function
                        and return True if the postcondition is met, False otherwise.

    Returns:
        callable: The decorated function with the postcondition check.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, Success):
                result = result.value
            for post in functions:
                check = post(result)
                if not check:
                    return Error(func, (args, kwargs))
            return Success(result)

        return wrapper

    return decorator


def invariant(*functions):
    """Decorator to specify an invariant for a function.

    Args:
        functions (callable): A list of callables that take the same arguments as the decorated function
                        and return True if the invariant is met, False otherwise.

    Returns:
        callable: The decorated function with the invariant check.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for inv in functions:
                pre_check = inv(*args, **kwargs)
                if not pre_check:
                    return Error(func, (args, kwargs))
            result = func(*args, **kwargs)
            for inv in functions:
                post_check = inv(*args, **kwargs)
                if not post_check:
                    return Error(func, (args, kwargs))
            return Success(result)

        return wrapper

    return decorator


# Aliases
require = precondition
ensure = postcondition
