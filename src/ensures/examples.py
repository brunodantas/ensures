"""
Examples demonstrating the usage of the ensures module.

The ensures module provides decorators for Design by Contract programming:
- @precondition (alias: @require): Check conditions before function execution
- @postcondition (alias: @ensure): Check conditions after function execution
- @invariant: Check conditions both before and after function execution
"""

from ensures import (
    Error,
    Success,
    ensure,
    invariant,
    postcondition,
    precondition,
    require,
)

# ============================================================================
# PRECONDITION EXAMPLES
# ============================================================================


def is_positive(x):
    """Check if a number is positive."""
    return x > 0


def is_non_empty(text):
    """Check if a string is not empty."""
    return len(text) > 0


@precondition(is_positive)
def square_root(x):
    """Calculate square root with precondition that x must be positive."""
    return x**0.5


@require(is_non_empty)  # Using the alias
def capitalize_text(text):
    """Capitalize text with precondition that text must not be empty."""
    return text.capitalize()


@precondition(lambda x, y: x != 0, lambda x, y: y != 0)  # Multiple preconditions
def divide_safe(x, y):
    """Safe division with preconditions that both numbers must be non-zero."""
    return x / y


# ============================================================================
# POSTCONDITION EXAMPLES
# ============================================================================


def result_is_positive(result):
    """Check if result is positive."""
    return result > 0


def result_is_even(result):
    """Check if result is even."""
    return result % 2 == 0


@postcondition(result_is_positive)
def absolute_value(x):
    """Calculate absolute value with postcondition that result is positive."""
    return abs(x)


@ensure(result_is_even)  # Using the alias
def double_number(x):
    """Double a number with postcondition that result is even."""
    return x * 2


@postcondition(lambda result: len(result) > 0)  # Lambda postcondition
def get_non_empty_string():
    """Return a non-empty string."""
    return "Hello, World!"


# ============================================================================
# INVARIANT EXAMPLES
# ============================================================================


def balance_is_non_negative(*args, **kwargs):
    """Check that balance is non-negative (for account operations)."""
    # For this example, we assume the first argument is always the balance
    if args:
        return args[0] >= 0
    return True


@invariant(balance_is_non_negative)
def add_to_balance(balance, amount):
    """Add amount to balance with invariant that balance stays non-negative."""
    return balance + amount


@invariant(lambda x: x >= 0)  # Simple lambda invariant
def increment_counter(x):
    """Increment a counter with invariant that it stays non-negative."""
    return x + 1


# ============================================================================
# COMPLEX EXAMPLES
# ============================================================================


def valid_age(age, _):
    """Check if age is valid (between 0 and 150)."""
    return 0 <= age <= 150


def valid_name(_, name):
    """Check if name is valid (non-empty string)."""
    return isinstance(name, str) and len(name.strip()) > 0


def adult_age(age, _):
    """Check if age represents an adult (18 or older)."""
    return age >= 18


@precondition(valid_age, valid_name)
@postcondition(lambda result: isinstance(result, str))
def create_person_description(age, name):
    """Create a person description with multiple conditions."""
    return f"{name} is {age} years old"


@require(adult_age)  # Using require alias
@ensure(lambda result: "adult" in result.lower())  # Using ensure alias
def create_adult_profile(age, name):
    """Create an adult profile with precondition and postcondition."""
    return f"{name} is an adult at {age} years old"


class BankAccount:
    """Example class demonstrating contract usage with methods."""

    def __init__(self, initial_balance=0):
        self.balance = initial_balance

    def __repr__(self) -> str:
        return f"BankAccount(balance={self.balance})"

    def balance_sufficient(self, amount):
        """Check if balance is sufficient for withdrawal."""
        return self.balance >= amount

    def amount_positive(self, amount):
        """Check if amount is positive."""
        return amount > 0

    @precondition(lambda self, amount: self.amount_positive(amount))
    def deposit(self, amount):
        """Deposit money with precondition that amount is positive."""
        self.balance += amount
        return self.balance

    @precondition(
        lambda self, amount: self.balance_sufficient(amount),
        lambda self, amount: self.amount_positive(amount),
    )
    def withdraw(self, amount):
        """Withdraw money with preconditions for positive amount and sufficient balance."""
        self.balance -= amount
        return self.balance


# ============================================================================
# DEMO FUNCTION
# ============================================================================


def run_examples():
    """Run all examples and demonstrate the results."""
    print("=== ENSURES MODULE EXAMPLES ===\n")

    # Successful precondition examples
    print("1. Successful Precondition Examples:")
    print(f"square_root(9) = {square_root(9)}")
    print(f"capitalize_text('hello') = {capitalize_text('hello')}")
    print(f"divide_safe(10, 2) = {divide_safe(10, 2)}")
    print()

    # Failed precondition examples
    print("2. Failed Precondition Examples:")
    print(f"square_root(-4) = {square_root(-4)}")
    print(f"capitalize_text('') = {capitalize_text('')}")
    print(f"divide_safe(10, 0) = {divide_safe(10, 0)}")
    print()

    # Successful postcondition examples
    print("3. Successful Postcondition Examples:")
    print(f"absolute_value(-5) = {absolute_value(-5)}")
    print(f"double_number(3) = {double_number(3)}")
    print(f"get_non_empty_string() = {get_non_empty_string()}")
    print()

    # Failed postcondition example
    print("4. Failed Postcondition Example:")
    print(
        f"double_number(2.5) = {double_number(2.5)}"
    )  # Will fail since 5.0 is not even
    print()

    # Invariant examples
    print("5. Invariant Examples:")
    print(f"add_to_balance(100, 50) = {add_to_balance(100, 50)}")
    print(f"add_to_balance(50, -60) = {add_to_balance(50, -60)}")  # Will fail invariant
    print(f"increment_counter(5) = {increment_counter(5)}")
    print()

    # Complex examples
    print("6. Complex Examples:")
    print(
        f"create_person_description(25, 'Alice') = {create_person_description(25, 'Alice')}"
    )
    print(
        f"create_person_description(-5, 'Bob') = {create_person_description(-5, 'Bob')}"
    )  # Will fail
    print(
        f"create_adult_profile(21, 'Charlie') = {create_adult_profile(21, 'Charlie')}"
    )
    print(
        f"create_adult_profile(16, 'David') = {create_adult_profile(16, 'David')}"
    )  # Will fail
    print()

    # Bank account examples
    print("7. Bank Account Examples:")
    account = BankAccount(100)
    print(f"Initial balance: {account.balance}")
    print(f"Deposit 50: {account.deposit(50)}")
    print(f"Withdraw 30: {account.withdraw(30)}")
    print(f"Try to withdraw 200: {account.withdraw(200)}")  # Will fail
    print(f"Try to deposit -10: {account.deposit(-10)}")  # Will fail
    print()

    # Result handling example
    print("8. Result Handling Example:")
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

    print("=== END OF EXAMPLES ===")


if __name__ == "__main__":
    run_examples()
