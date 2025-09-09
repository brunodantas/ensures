"""
Test suite for the ensures module based on examples.py.

Tests all functionality including preconditions, postconditions, invariants,
and the Result types (Success and Error).
"""

import pytest

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
# TEST HELPER FUNCTIONS
# ============================================================================


def is_positive(x):
    """Check if a number is positive."""
    return x > 0


def is_non_empty(text):
    """Check if a string is not empty."""
    return len(text) > 0


def result_is_positive(result):
    """Check if result is positive."""
    return result > 0


def result_is_even(result):
    """Check if result is even."""
    return result % 2 == 0


# ============================================================================
# PRECONDITION TESTS
# ============================================================================


class TestPreconditions:
    """Test precondition decorator functionality."""

    def test_precondition_success(self):
        """Test successful precondition check."""

        @precondition(is_positive)
        def square_root(x):
            return x**0.5

        result = square_root(9)
        assert isinstance(result, Success)
        assert result.value == 3.0

    def test_precondition_failure(self):
        """Test failed precondition check."""

        @precondition(is_positive)
        def square_root(x):
            return x**0.5

        result = square_root(-4)
        assert isinstance(result, Error)
        assert result.function.__name__ == "square_root"
        assert result.args == ((-4,), {})

    def test_require_alias(self):
        """Test that require is an alias for precondition."""

        @require(is_non_empty)
        def capitalize_text(text):
            return text.capitalize()

        # Success case
        result = capitalize_text("hello")
        assert isinstance(result, Success)
        assert result.value == "Hello"

        # Failure case
        result = capitalize_text("")
        assert isinstance(result, Error)

    def test_multiple_preconditions_success(self):
        """Test multiple preconditions all passing."""

        @precondition(lambda x, y: x != 0, lambda x, y: y != 0)
        def divide_safe(x, y):
            return x / y

        result = divide_safe(10, 2)
        assert isinstance(result, Success)
        assert result.value == 5.0

    def test_multiple_preconditions_failure(self):
        """Test multiple preconditions with one failing."""

        @precondition(lambda x, y: x != 0, lambda x, y: y != 0)
        def divide_safe(x, y):
            return x / y

        result = divide_safe(10, 0)
        assert isinstance(result, Error)

    def test_precondition_with_kwargs(self):
        """Test precondition with keyword arguments."""

        @precondition(lambda name, age: len(name) > 0 and age >= 0)
        def create_person(name, age):
            return f"{name} is {age} years old"

        # Success case
        result = create_person(name="Alice", age=25)
        assert isinstance(result, Success)
        assert result.value == "Alice is 25 years old"

        # Failure case
        result = create_person(name="", age=25)
        assert isinstance(result, Error)


# ============================================================================
# POSTCONDITION TESTS
# ============================================================================


class TestPostconditions:
    """Test postcondition decorator functionality."""

    def test_postcondition_success(self):
        """Test successful postcondition check."""

        @postcondition(result_is_positive)
        def absolute_value(x):
            return abs(x)

        result = absolute_value(-5)
        assert isinstance(result, Success)
        assert result.value == 5

    def test_postcondition_failure(self):
        """Test failed postcondition check."""

        @postcondition(result_is_positive)
        def negative_value(x):
            return -abs(x)

        result = negative_value(5)
        assert isinstance(result, Error)

    def test_ensure_alias(self):
        """Test that ensure is an alias for postcondition."""

        @ensure(result_is_even)
        def double_number(x):
            return x * 2

        # Success case
        result = double_number(3)
        assert isinstance(result, Success)
        assert result.value == 6

        # Failure case (when input is float, result might not be integer even)
        result = double_number(2.5)
        assert isinstance(result, Error)

    def test_lambda_postcondition(self):
        """Test postcondition with lambda function."""

        @postcondition(lambda result: len(result) > 0)
        def get_string():
            return "Hello, World!"

        result = get_string()
        assert isinstance(result, Success)
        assert result.value == "Hello, World!"

    def test_postcondition_failure_with_empty_result(self):
        """Test postcondition failure with empty result."""

        @postcondition(lambda result: len(result) > 0)
        def get_empty_string():
            return ""

        result = get_empty_string()
        assert isinstance(result, Error)


# ============================================================================
# INVARIANT TESTS
# ============================================================================


class TestInvariants:
    """Test invariant decorator functionality."""

    def test_invariant_success(self):
        """Test successful invariant check."""

        @invariant(lambda x: x >= 0)
        def increment_counter(x):
            return x + 1

        result = increment_counter(5)
        assert isinstance(result, Success)
        assert result.value == 6

    def test_invariant_failure_precondition(self):
        """Test invariant failure at precondition check."""

        @invariant(lambda x: x >= 0)
        def increment_counter(x):
            return x + 1

        result = increment_counter(-1)
        assert isinstance(result, Error)

    def test_invariant_failure_postcondition(self):
        """Test invariant failure at postcondition check."""
        # Note: The current invariant implementation checks the same args
        # before and after, so this test checks for consistent behavior
        call_count = 0

        def changing_invariant(balance, amount):
            nonlocal call_count
            call_count += 1
            # Fail on the second call (postcondition check)
            return call_count == 1

        @invariant(changing_invariant)
        def subtract_from_balance(balance, amount):
            return balance - amount

        result = subtract_from_balance(50, 60)
        assert isinstance(result, Error)

    def test_invariant_with_multiple_args(self):
        """Test invariant with multiple arguments."""

        def balance_is_non_negative(*args, **kwargs):
            if args:
                return args[0] >= 0
            return True

        @invariant(balance_is_non_negative)
        def add_to_balance(balance, amount):
            return balance + amount

        # Success case
        result = add_to_balance(100, 50)
        assert isinstance(result, Success)
        assert result.value == 150

        # Failure case
        result = add_to_balance(-10, 5)
        assert isinstance(result, Error)


# ============================================================================
# COMPLEX DECORATOR COMBINATIONS
# ============================================================================


class TestComplexDecorators:
    """Test combinations of multiple decorators."""

    def test_precondition_and_postcondition(self):
        """Test function with both precondition and postcondition."""

        def valid_age(age, _):
            return 0 <= age <= 150

        def valid_name(_, name):
            return isinstance(name, str) and len(name.strip()) > 0

        @precondition(valid_age, valid_name)
        @postcondition(lambda result: isinstance(result, str))
        def create_person_description(age, name):
            return f"{name} is {age} years old"

        # Success case
        result = create_person_description(25, "Alice")
        assert isinstance(result, Success)
        # Note: nested Success due to combining decorators
        assert isinstance(result.value, Success)
        assert result.value.value == "Alice is 25 years old"

        # Precondition failure
        result = create_person_description(-5, "Bob")
        assert isinstance(result, Error)

        # Another precondition failure
        result = create_person_description(25, "")
        assert isinstance(result, Error)

    def test_require_and_ensure_aliases(self):
        """Test using require and ensure aliases together."""

        def adult_age(age, _):
            return age >= 18

        @require(adult_age)
        @ensure(lambda result: "adult" in result.lower())
        def create_adult_profile(age, name):
            return f"{name} is an adult at {age} years old"

        # Success case
        result = create_adult_profile(21, "Charlie")
        assert isinstance(result, Success)
        # Note: nested Success due to combining decorators
        assert isinstance(result.value, Success)
        assert result.value.value == "Charlie is an adult at 21 years old"

        # Precondition failure
        result = create_adult_profile(16, "David")
        assert isinstance(result, Error)


# ============================================================================
# CLASS METHOD TESTS
# ============================================================================


class TestClassMethods:
    """Test decorators on class methods."""

    class BankAccount:
        """Test bank account class with decorated methods."""

        def __init__(self, initial_balance=0):
            self.balance = initial_balance

        def amount_positive(self, amount):
            return amount > 0

        def balance_sufficient(self, amount):
            return self.balance >= amount

        @precondition(lambda self, amount: self.amount_positive(amount))
        def deposit(self, amount):
            self.balance += amount
            return self.balance

        @precondition(
            lambda self, amount: self.balance_sufficient(amount),
            lambda self, amount: self.amount_positive(amount),
        )
        def withdraw(self, amount):
            self.balance -= amount
            return self.balance

    def test_bank_account_deposit_success(self):
        """Test successful bank account deposit."""
        account = self.BankAccount(100)
        result = account.deposit(50)
        assert isinstance(result, Success)
        assert result.value == 150
        assert account.balance == 150

    def test_bank_account_deposit_failure(self):
        """Test failed bank account deposit with negative amount."""
        account = self.BankAccount(100)
        result = account.deposit(-10)
        assert isinstance(result, Error)
        assert account.balance == 100  # Balance unchanged

    def test_bank_account_withdraw_success(self):
        """Test successful bank account withdrawal."""
        account = self.BankAccount(100)
        result = account.withdraw(30)
        assert isinstance(result, Success)
        assert result.value == 70
        assert account.balance == 70

    def test_bank_account_withdraw_insufficient_funds(self):
        """Test failed withdrawal with insufficient funds."""
        account = self.BankAccount(100)
        result = account.withdraw(200)
        assert isinstance(result, Error)
        assert account.balance == 100  # Balance unchanged

    def test_bank_account_withdraw_negative_amount(self):
        """Test failed withdrawal with negative amount."""
        account = self.BankAccount(100)
        result = account.withdraw(-10)
        assert isinstance(result, Error)
        assert account.balance == 100  # Balance unchanged


# ============================================================================
# RESULT TYPE TESTS
# ============================================================================


class TestResultTypes:
    """Test Success and Error result types."""

    def test_success_creation(self):
        """Test Success object creation and representation."""
        success = Success(42)
        assert success.value == 42
        assert repr(success) == "Success(42)"

    def test_success_without_value(self):
        """Test Success object without explicit value."""
        success = Success()
        assert success.value is None
        assert repr(success) == "Success(None)"

    def test_error_creation(self):
        """Test Error object creation and representation."""

        def dummy_func(x, y):
            return x + y

        error = Error(dummy_func, ((1, 2), {"z": 3}))
        assert error.function == dummy_func
        assert error.args == ((1, 2), {"z": 3})
        assert "dummy_func" in repr(error)

    def test_result_pattern_matching(self):
        """Test pattern matching with Success and Error results."""

        @precondition(is_positive)
        def safe_sqrt(x):
            return Success(x**0.5)

        # Success case
        result = safe_sqrt(9)
        assert isinstance(result, Success)
        # The result will be Success(Success(3.0)) due to decorator wrapping
        assert isinstance(result.value, Success)
        assert result.value.value == 3.0

        # Error case
        result = safe_sqrt(-4)
        match result:
            case Success(_):
                pytest.fail("Expected Error, got Success")
            case Error(func, args):
                assert func.__name__ == "safe_sqrt"
                assert args == ((-4,), {})


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_precondition_with_exception(self):
        """Test precondition that raises an exception."""

        def risky_check(x):
            return 1 / x > 0  # Will raise ZeroDivisionError for x=0

        @precondition(risky_check)
        def safe_function(x):
            return x * 2

        # This should propagate the ZeroDivisionError, not return Error
        with pytest.raises(ZeroDivisionError):
            safe_function(0)

    def test_postcondition_with_none_result(self):
        """Test postcondition with None result."""

        @postcondition(lambda result: result is not None)
        def return_none():
            return None

        result = return_none()
        assert isinstance(result, Error)

    def test_empty_precondition_list(self):
        """Test decorator with no precondition functions."""

        @precondition()
        def simple_function(x):
            return x * 2

        result = simple_function(5)
        assert isinstance(result, Success)
        assert result.value == 10

    def test_function_with_no_args(self):
        """Test decorated function with no arguments."""

        @postcondition(lambda result: result > 0)
        def get_positive_number():
            return 42

        result = get_positive_number()
        assert isinstance(result, Success)
        assert result.value == 42


if __name__ == "__main__":
    pytest.main([__file__])
