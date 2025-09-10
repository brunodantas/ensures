"""
Design by Contract implementation for Python.

This module provides decorators for implementing preconditions, postconditions,
and invariants in Python functions, following the Design by Contract methodology.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any


class Result:
    """
    Base class for representing the result of a function with Design by Contract checks.

    This class serves as the parent for Success and Error classes, providing a common
    interface for handling the outcomes of functions decorated with precondition,
    postcondition, or invariant checks.

    The Result type enables pattern matching and functional error handling, allowing
    developers to handle success and failure cases explicitly rather than relying
    on exceptions.

    Example:
        >>> # Used internally by decorators, typically not instantiated directly
        >>> result = some_decorated_function(args)
        >>> match result:
        ...     case Success(value):
        ...         print(f"Success: {value}")
        ...     case Error(func, args):
        ...         print(f"Error in {func.__name__} with {args}")
    """


class Success(Result):
    """
    Represents a successful result from a function with Design by Contract checks.

    This class encapsulates the return value of a function that has passed all
    its precondition, postcondition, and invariant checks. It provides pattern
    matching support and maintains the original function's return value.

    Attributes:
        value: The actual return value from the successfully executed function.

    Args:
        value: The value to be wrapped in a Success result. Defaults to None.

    Example:
        >>> from ensures import precondition
        >>>
        >>> def is_positive(x):
        ...     return x > 0
        >>>
        >>> @precondition(is_positive)
        ... def square_root(x):
        ...     return x ** 0.5
        >>>
        >>> result = square_root(4)
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")  # Output: Result: 2.0
        ...     case Error(func, args):
        ...         print(f"Error in {func.__name__}")
    """

    __match_args__ = ("value",)

    def __init__(self, value: Any = None) -> None:
        """Initialize a Success result with the given value."""
        self.value = value

    def __repr__(self) -> str:
        """Return a string representation of the Success result."""
        return f"Success({self.value})"


class Error(Result):
    """
    Represents an error result from a function with failed Design by Contract checks.

    This class encapsulates information about a function that failed to meet its
    precondition, postcondition, or invariant requirements. It provides pattern
    matching support and maintains details about the failed function and its arguments.

    Attributes:
        function: The function that failed the contract check.
        args: A tuple containing the positional and keyword arguments passed to the
            function.

    Args:
        function: The function Any that failed the contract check.
        args: A tuple of (args, kwargs) representing the arguments passed to the
            function.

    Example:
        >>> from ensures import precondition
        >>>
        >>> def is_positive(x):
        ...     return x > 0
        >>>
        >>> @precondition(is_positive)
        ... def square_root(x):
        ...     return x ** 0.5
        >>>
        >>> result = square_root(-4)  # Fails precondition
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")
        ...     case Error(func, args):
        ...         print(f"Error: {func.__name__} failed with args {args}")
        ...         # Output: Error: square_root failed with args ((-4,), {})
    """

    __match_args__ = ("function", "args")

    def __init__(self, function: Callable, args: tuple) -> None:
        """Initialize an Error result with the failed function and its arguments."""
        self.function = function
        self.args = args

    def __repr__(self) -> str:
        """Return a string representation of the Error result."""
        return f"Error({self.function.__name__} given args, kwargs: {self.args})"


def precondition(
    *functions: Callable[..., bool],
) -> Callable[[Callable[..., Any]], Callable[..., Result]]:
    """
    Decorator to specify preconditions for a function.

    Preconditions are conditions that must be true when a function is called. This
    decorator checks all provided predicate functions against the function's arguments
    before executing the original function. If any precondition fails, an Error result
    is returned instead of executing the function.

    Args:
        *functions: Variable number of callable predicates that take the same arguments
            as the decorated function and return True if the precondition is satisfied,
            False otherwise. Each predicate function should have the same signature
            as the decorated function.

    Returns:
        A decorator function that wraps the original function with precondition checks.
        The decorated function will return either:
        - Success(result) if all preconditions pass and the function executes
            successfully
        - Error(function, args) if any precondition fails

    Example:
        >>> from ensures import precondition
        >>>
        >>> def is_positive(x):
        ...     '''Check if a number is positive.'''
        ...     return x > 0
        >>>
        >>> def is_not_zero(x):
        ...     '''Check if a number is not zero.'''
        ...     return x != 0
        >>>
        >>> @precondition(is_positive, is_not_zero)
        ... def safe_divide_by_self(x):
        ...     '''Divide a number by itself, requiring positive and non-zero.'''
        ...     return x / x
        >>>
        >>> # Success case
        >>> result = safe_divide_by_self(5)
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")  # Output: Result: 1.0
        ...     case Error(func, args):
        ...         print("Precondition failed")
        >>>
        >>> # Failure case
        >>> result = safe_divide_by_self(-3)  # Fails is_positive precondition
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")
        ...     case Error(func, args):
        ...         print("Precondition failed")  # This will be printed

    Note:
        Precondition functions should be pure functions without side effects, as they
        are used for validation purposes only. They should not modify the state of
        the program or perform any operations other than validation.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Result]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Result:
            for pre in functions:
                result = pre(*args, **kwargs)
                if not result:
                    return Error(func, (args, kwargs))
            result_func = func(*args, **kwargs)
            # In case of multiple decorators
            return (
                result_func
                if issubclass(type(result_func), Result)
                else Success(result_func)
            )

        return wrapper

    return decorator


def postcondition(
    *functions: Callable[[Any], bool],
) -> Callable[[Callable[..., Any]], Callable[..., Result]]:
    """
    Decorator to specify postconditions for a function.

    Postconditions are conditions that must be true after a function has executed
    successfully. This decorator executes the original function first, then checks
    all provided predicate functions against the function's return value. If any
    postcondition fails, an Error result is returned.

    Args:
        *functions: Variable number of callable predicates that take the function's
            return value as their single argument and return True if the postcondition
            is satisfied, False otherwise. Each predicate function should accept
            exactly one parameter: the return value of the decorated function.

    Returns:
        A decorator function that wraps the original function with postcondition checks.
        The decorated function will return either:
        - Success(result) if the function executes and all postconditions pass
        - Error(function, args) if any postcondition fails

    Example:
        >>> from ensures import postcondition
        >>>
        >>> def is_positive_result(result):
        ...     '''Check if the result is positive.'''
        ...     return result > 0
        >>>
        >>> def is_reasonable_square_root(result):
        ...     '''Check if result is a reasonable square root (< 100).'''
        ...     return result < 100
        >>>
        >>> @postcondition(is_positive_result, is_reasonable_square_root)
        ... def safe_square_root(x):
        ...     '''Calculate square root with postcondition checks.'''
        ...     return x ** 0.5
        >>>
        >>> # Success case
        >>> result = safe_square_root(16)
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")  # Output: Result: 4.0
        ...     case Error(func, args):
        ...         print("Postcondition failed")
        >>>
        >>> # Failure case (if we had a function that could return negative results)
        >>> # The postcondition would catch invalid results

    Note:
        Postcondition functions are called after the original function executes,
        so they should only validate the result, not modify it. They should be
        pure functions without side effects.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Result]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Result:
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


def invariant(
    *functions: Callable[..., bool],
) -> Callable[[Callable[..., Any]], Callable[..., Result]]:
    """
    Decorator to specify invariants for a function.

    Invariants are conditions that must remain true both before and after a function
    executes. This decorator checks all provided predicate functions against the
    function's arguments before execution, executes the original function, then
    checks the same predicates again with the same arguments. If any invariant
    fails at any point, an Error result is returned.

    Args:
        *functions: Variable number of callable predicates that take the same arguments
            as the decorated function and return True if the invariant holds,
            False otherwise. Each predicate function should have the same signature
            as the decorated function and should check conditions that must remain
            constant throughout the function's execution.

    Returns:
        A decorator function that wraps the original function with invariant checks.
        The decorated function will return either:
        - Success(result) if all invariants hold before and after execution
        - Error(function, args) if any invariant fails before or after execution

    Example:
        >>> from ensures import invariant
        >>>
        >>> # Global state that should remain unchanged
        >>> global_config = {"debug": True, "version": "1.0"}
        >>>
        >>> def config_unchanged():
        ...     '''Check that global config remains unchanged.'''
        ...     return global_config == {"debug": True, "version": "1.0"}
        >>>
        >>> def input_type_preserved(x):
        ...     '''Check that input is still a number.'''
        ...     return isinstance(x, (int, float))
        >>>
        >>> @invariant(config_unchanged, input_type_preserved)
        ... def safe_calculation(x):
        ...     '''Perform calculation while preserving invariants.'''
        ...     # This function should not modify global_config or change x's type
        ...     return x * 2 + 1
        >>>
        >>> # Success case
        >>> result = safe_calculation(5)
        >>> match result:
        ...     case Success(value):
        ...         print(f"Result: {value}")  # Output: Result: 11
        ...     case Error(func, args):
        ...         print("Invariant violation")

    Note:
        Invariant functions should check conditions that are expected to remain
        constant throughout the execution of the decorated function. They are
        particularly useful for checking that global state, Any properties,
        or input characteristics remain unchanged during function execution.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Result]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Result:
            for inv in functions:
                pre_check = inv(*args, **kwargs)
                if not pre_check:
                    return Error(func, (args, kwargs))
            result_func = func(*args, **kwargs)
            for inv in functions:
                post_check = inv(*args, **kwargs)
                if not post_check:
                    return Error(func, (args, kwargs))
            return (
                result_func
                if issubclass(type(result_func), Result)
                else Success(result_func)
            )

        return wrapper

    return decorator


# Aliases for more expressive Design by Contract syntax
require = precondition
"""
Alias for precondition decorator.

This alias provides more expressive syntax when specifying preconditions,
following the conventional Design by Contract terminology where "require"
statements specify what must be true when a function is called.

Example:
    >>> from ensures import require
    >>>
    >>> def is_positive(x):
    ...     return x > 0
    >>>
    >>> @require(is_positive)
    ... def square_root(x):
    ...     return x ** 0.5

See Also:
    precondition: The main precondition decorator function.
"""

ensure = postcondition
"""
Alias for postcondition decorator.

This alias provides more expressive syntax when specifying postconditions,
following the conventional Design by Contract terminology where "ensure"
statements specify what must be true after a function executes.

Example:
    >>> from ensures import ensure
    >>>
    >>> def result_is_positive(result):
    ...     return result > 0
    >>>
    >>> @ensure(result_is_positive)
    ... def absolute_value(x):
    ...     return abs(x)

See Also:
    postcondition: The main postcondition decorator function.
"""
