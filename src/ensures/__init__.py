"""
ensures: Simple Design by Contract for Python.

This package provides decorators for implementing Design by Contract methodology
in Python, including preconditions, postconditions, and invariants.

Classes:
    Result: Base class for contract check results
    Success: Represents a successful contract check result
    Error: Represents a failed contract check result

Functions:
    precondition: Decorator for specifying function preconditions
    postcondition: Decorator for specifying function postconditions
    invariant: Decorator for specifying function invariants
    require: Alias for precondition (more expressive syntax)
    ensure: Alias for postcondition (more expressive syntax)

Example:
    >>> from ensures import precondition, postcondition, Success, Error
    >>>
    >>> def is_positive(x):
    ...     return x > 0
    >>>
    >>> def result_is_positive(result):
    ...     return result > 0
    >>>
    >>> @precondition(is_positive)
    ... @postcondition(result_is_positive)
    ... def square_root(x):
    ...     return x ** 0.5
    >>>
    >>> result = square_root(4)
    >>> match result:
    ...     case Success(value):
    ...         print(f"Result: {value}")
    ...     case Error(func, args):
    ...         print("Contract violation")
"""

from .ensures import (
    Error,
    Result,
    Success,
    ensure,
    invariant,
    postcondition,
    precondition,
    require,
)

__all__ = [
    "Result",
    "Success",
    "Error",
    "precondition",
    "postcondition",
    "invariant",
    "require",
    "ensure",
]
