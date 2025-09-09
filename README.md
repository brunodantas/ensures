# ensures

[![CI](https://github.com/brunodantas/ensures/actions/workflows/ci.yml/badge.svg)](https://github.com/brunodantas/ensures/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ensures.svg)](https://badge.fury.io/py/ensures)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ensures)](https://pypi.org/project/ensures/)
[![codecov](https://codecov.io/gh/brunodantas/ensures/graph/badge.svg)](https://codecov.io/gh/brunodantas/ensures)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI - Status](https://img.shields.io/pypi/status/ensures)](https://pypi.org/project/ensures/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

`ensures` is a simple Python package that implements the idea of [Design by Contract](https://en.wikipedia.org/wiki/Design_by_contract) described in the *Pragmatic Paranoia* chapter of [The Pragmatic Programmer](https://en.wikipedia.org/wiki/The_Pragmatic_Programmer). That's the chapter where they say you should *trust nobody, not even yourself*.

![](trust.jpg)

## Main Features

- Verification of lists of pre/post condition and invariant functions.
- Usage of arbitrary functions for such verification.
- [Result-type](https://en.wikipedia.org/wiki/Result_type) return values.


## Installation

```bash
pip install ensures
```

## Usage

### `precondition` / `require`

Runs a list of functions on all args.

Returns `Error` if any of them fails.

```python
from ensures import precondition


def is_positive(x):
    """Check if a number is positive."""
    return x > 0


@precondition(is_positive)
def square_root(x):
    """Calculate square root with precondition that x must be positive."""
    return x**0.5
```

### `postcondition` / `ensure`

Runs a list of functions on the result.

Returns `Error` if any of them fails.

```python
from ensures import ensure


def result_is_even(result):
    """Check if result is even."""
    return result % 2 == 0


@ensure(result_is_even)  # Using the alias
def double_number(x):
    """Double a number with postcondition that result is even."""
    return x * 2
```


### `invariant`

Runs a list of functions on all args.

Returns `Error` if any of them fails.

```python
from ensures import invariant


@invariant(lambda x: x >= 0)  # Simple lambda invariant
def increment_counter(x):
    """Increment a counter with invariant that it stays non-negative."""
    return x + 1
```

### Result Handling

Pattern matching is supported to unpack the `Return` value.

```python
from ensures import Error, Success


result1 = square_root(1)
result2 = square_root(-1)  # This will return an Error instance

def handle_result(res):
    match res:
        case Success(value):
            print(f"Square root calculated: {value}")
        case Error(func, args):
            print(f"Precondition failed in {func.__name__} with args {args}")

handle_result(result1)
handle_result(result2)
```


## More examples

Check [examples.py](/src/ensures/examples.py)