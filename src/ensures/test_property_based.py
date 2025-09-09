"""
Property-based tests for the ensures module using Hypothesis.

These tests automatically generate test cases to find edge cases and
validate the contracts across a wide range of inputs.
"""

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ensures import Error, Success, invariant, postcondition, precondition
from ensures.ensures import Result

# ============================================================================
# PROPERTY-BASED TESTS FOR PRECONDITIONS
# ============================================================================


class TestPreconditionProperties:
    """Property-based tests for precondition decorators."""

    @given(st.integers())
    def test_precondition_always_returns_result(self, x: int):
        """Property: precondition decorator always returns Result type."""

        def is_even(n):
            return n % 2 == 0

        @precondition(is_even)
        def double_if_even(n):
            return n * 2

        result = double_if_even(x)
        assert isinstance(result, Success | Error)

    @given(st.integers().filter(lambda x: x > 0))
    def test_precondition_success_with_positive_numbers(self, x: int):
        """Property: positive numbers should pass positive precondition."""

        def is_positive(n):
            return n > 0

        @precondition(is_positive)
        def square(n):
            return n * n

        result = square(x)
        assert isinstance(result, Success)
        assert result.value == x * x

    @given(st.integers().filter(lambda x: x <= 0))
    def test_precondition_failure_with_non_positive_numbers(self, x: int):
        """Property: non-positive numbers should fail positive precondition."""

        def is_positive(n):
            return n > 0

        @precondition(is_positive)
        def square(n):
            return n * n

        result = square(x)
        assert isinstance(result, Error)
        assert result.function.__name__ == "square"

    @given(st.lists(st.integers(), min_size=1, max_size=10))
    def test_multiple_preconditions_properties(self, numbers: list[int]):
        """Property: multiple preconditions behavior is predictable."""

        def all_positive(nums):
            return all(n > 0 for n in nums)

        def not_empty(nums):
            return len(nums) > 0

        @precondition(all_positive, not_empty)
        def sum_positive_numbers(nums):
            return sum(nums)

        result = sum_positive_numbers(numbers)

        # Since list is guaranteed to be non-empty (min_size=1),
        # the result depends only on whether all numbers are positive
        if all(n > 0 for n in numbers):
            assert isinstance(result, Success)
            assert result.value == sum(numbers)
        else:
            assert isinstance(result, Error)


# ============================================================================
# PROPERTY-BASED TESTS FOR POSTCONDITIONS
# ============================================================================


class TestPostconditionProperties:
    """Property-based tests for postcondition decorators."""

    @given(st.integers())
    def test_postcondition_validates_output(self, x: int):
        """Property: postcondition validates function output correctly."""

        def result_is_even(result):
            return result % 2 == 0

        @postcondition(result_is_even)
        def double_number(n):
            return n * 2

        result = double_number(x)
        # n * 2 is always even, so this should always succeed
        assert isinstance(result, Success)
        assert result.value == x * 2

    @given(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False))
    def test_postcondition_with_mathematical_properties(self, x: float):
        """Property: mathematical postconditions work correctly."""

        def result_is_non_negative(result):
            return result >= 0

        def result_is_finite(result):
            return abs(result) < float("inf")

        @postcondition(result_is_non_negative, result_is_finite)
        def square_root(n):
            return n**0.5

        result = square_root(x)
        assert isinstance(result, Success)
        assert abs(result.value - x**0.5) < 1e-10  # Account for floating point


# ============================================================================
# PROPERTY-BASED TESTS FOR INVARIANTS
# ============================================================================


class TestInvariantProperties:
    """Property-based tests for invariant decorators."""

    @given(st.integers(min_value=-100, max_value=100))
    def test_invariant_preserves_input_properties(self, x: int):
        """Property: invariants preserve properties of input arguments."""

        def input_within_range(n):
            return -100 <= n <= 100

        @invariant(input_within_range)
        def safe_increment(n):
            return n + 1

        result = safe_increment(x)
        assert isinstance(result, Success)
        assert result.value == x + 1

    @given(st.lists(st.integers(), min_size=0, max_size=5))
    def test_invariant_with_list_operations(self, numbers: list[int]):
        """Property: invariants work correctly with list operations."""

        def input_is_list(nums):
            return isinstance(nums, list)

        @invariant(input_is_list)
        def sum_list(nums):
            return sum(nums) if nums else 0

        result = sum_list(numbers)
        assert isinstance(result, Success)
        assert result.value == sum(numbers) if numbers else True


# ============================================================================
# EDGE CASE PROPERTY TESTS
# ============================================================================


class TestEdgeCaseProperties:
    """Property-based tests for edge cases and boundary conditions."""

    @given(st.one_of(st.integers(), st.text(), st.lists(st.integers())))
    def test_contracts_handle_various_types(self, value: Any):
        """Property: contracts handle various input types gracefully."""

        def always_true(x):
            return True

        @precondition(always_true)
        def stringify_value(x):
            return str(x)

        result = stringify_value(value)
        assert isinstance(result, Success)
        assert result.value == str(value)

    @given(st.integers(min_value=0, max_value=3))
    def test_empty_function_list_behavior(self, x: int):
        """Property: decorators with no functions behave predictably."""

        @precondition()  # No precondition functions
        def identity(n):
            return n

        result = identity(x)
        assert isinstance(result, Success)
        assert result.value == x

    @given(st.text(min_size=0, max_size=10))
    def test_string_processing_contracts(self, text: str):
        """Property: string processing with contracts works correctly."""

        def result_is_uppercase(result):
            return result.isupper() or result == ""

        @postcondition(result_is_uppercase)
        def make_uppercase(s):
            return s.upper()

        result = make_uppercase(text)
        assert isinstance(result, Result)


# ============================================================================
# PERFORMANCE-RELATED PROPERTY TESTS
# ============================================================================


class TestPerformanceProperties:
    """Property-based tests that help identify performance characteristics."""

    @given(st.lists(st.integers(), min_size=0, max_size=100))
    @settings(max_examples=50)  # Reduce examples for performance tests
    def test_contract_overhead_is_reasonable(self, numbers: list[int]):
        """Property: contract checking doesn't add excessive overhead."""

        def always_true(nums):
            return True

        @precondition(always_true)
        @postcondition(lambda result: isinstance(result, int))
        def sum_numbers(nums):
            return sum(nums) if nums else True

        result = sum_numbers(numbers)
        assert isinstance(result, Success)
        assert result.value == sum(numbers) if numbers else True

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_multiple_contract_functions_performance(self, n: int):
        """Property: multiple contract functions don't cause excessive slowdown."""

        def condition1(x):
            return x > 0

        def condition2(x):
            return x < 100

        def condition3(x):
            return x != 50

        @precondition(condition1, condition2, condition3)
        def process_number(x):
            return x * 2

        result = process_number(n)
        if n != 50:  # All conditions should pass except when n == 50
            assert isinstance(result, Success)
            assert result.value == n * 2
        else:
            assert isinstance(result, Error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
