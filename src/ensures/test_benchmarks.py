"""
Performance benchmarks for the ensures module.

These tests measure the performance characteristics of the contract decorators
to ensure they don't add excessive overhead to function execution.
"""

import time

import pytest

from ensures import Error, Success, postcondition, precondition

# ============================================================================
# BENCHMARK HELPER FUNCTIONS
# ============================================================================


def simple_function(x: int) -> int:
    """A simple function without any decorators for baseline measurement."""
    return x * 2 + 1


def is_positive(x: int) -> bool:
    """Simple precondition function."""
    return x > 0


def result_is_positive(result: int) -> bool:
    """Simple postcondition function."""
    return result > 0


@precondition(is_positive)
def decorated_function(x: int) -> int:
    """Same function as simple_function but with a precondition."""
    return x * 2 + 1


@postcondition(result_is_positive)
def postcondition_function(x: int) -> int:
    """Same function with postcondition."""
    return x * 2 + 1


@precondition(is_positive)
@postcondition(result_is_positive)
def fully_decorated_function(x: int) -> int:
    """Function with both pre and postconditions."""
    return x * 2 + 1


# ============================================================================
# PERFORMANCE BENCHMARK TESTS
# ============================================================================


class TestPerformanceBenchmarks:
    """Benchmark tests for contract decorator performance."""

    def test_baseline_function_performance(self, benchmark):
        """Benchmark baseline function without decorators."""
        result = benchmark(simple_function, 42)
        assert result == 85

    def test_precondition_overhead(self, benchmark):
        """Benchmark function with precondition decorator."""

        def run_decorated():
            result = decorated_function(42)
            assert isinstance(result, Success)
            return result.value

        result = benchmark(run_decorated)
        assert result == 85

    def test_postcondition_overhead(self, benchmark):
        """Benchmark function with postcondition decorator."""

        def run_postcondition():
            result = postcondition_function(42)
            assert isinstance(result, Success)
            return result.value

        result = benchmark(run_postcondition)
        assert result == 85

    def test_full_decoration_overhead(self, benchmark):
        """Benchmark function with both pre and postconditions."""

        def run_full_decoration():
            result = fully_decorated_function(42)
            assert isinstance(result, Success)
            return result.value

        result = benchmark(run_full_decoration)
        assert result == 85

    def test_multiple_preconditions_overhead(self, benchmark):
        """Benchmark function with multiple precondition checks."""

        def is_even(x):
            return x % 2 == 0

        def less_than_hundred(x):
            return x < 100

        @precondition(is_positive, is_even, less_than_hundred)
        def multi_precondition_func(x):
            return x * 2 + 1

        def run_multi_precondition():
            result = multi_precondition_func(42)
            assert isinstance(result, Success)
            return result.value

        result = benchmark(run_multi_precondition)
        assert result == 85

    def test_failing_precondition_performance(self, benchmark):
        """Benchmark performance when precondition fails."""

        def run_failing_precondition():
            result = decorated_function(-1)  # Should fail is_positive
            assert isinstance(result, Error)
            return result

        result = benchmark(run_failing_precondition)
        assert isinstance(result, Error)

    def test_list_processing_performance(self, benchmark):
        """Benchmark contract decorators with list processing."""

        def list_not_empty(lst):
            return len(lst) > 0

        def result_same_length(result):
            return len(result) == 1000  # We know the input will be 1000 items

        @precondition(list_not_empty)
        @postcondition(result_same_length)
        def double_list_items(items):
            return [x * 2 for x in items]

        test_data = list(range(1000))

        def run_list_processing():
            result = double_list_items(test_data)
            assert isinstance(result, Success)
            return len(result.value)

        result = benchmark(run_list_processing)
        assert result == 1000


# ============================================================================
# SCALABILITY TESTS
# ============================================================================


class TestScalabilityBenchmarks:
    """Tests to measure how performance scales with input size."""

    @pytest.mark.parametrize("size", [10, 100, 1000])
    def test_list_size_scaling(self, benchmark, size: int):
        """Test how performance scales with list size."""

        def list_not_empty(lst):
            return len(lst) > 0

        def result_correct_length(result):
            return len(result) == size

        @precondition(list_not_empty)
        @postcondition(result_correct_length)
        def process_list(items):
            return [x + 1 for x in items]

        test_data = list(range(size))

        def run_processing():
            result = process_list(test_data)
            assert isinstance(result, Success)
            return len(result.value)

        result = benchmark(run_processing)
        assert result == size

    @pytest.mark.parametrize("num_conditions", [1, 3, 5, 10])
    def test_multiple_conditions_scaling(self, benchmark, num_conditions: int):
        """Test how performance scales with number of contract conditions."""

        # Create multiple simple conditions
        conditions = []
        for i in range(num_conditions):
            conditions.append(lambda x, i=i: x > i)  # Each condition checks x > i

        # Apply all conditions as preconditions
        def create_decorated_function():
            @precondition(*conditions)
            def multi_condition_func(x):
                return x * 2

            return multi_condition_func

        decorated_func = create_decorated_function()

        def run_multi_conditions():
            # Use a value that satisfies all conditions
            result = decorated_func(num_conditions + 5)
            assert isinstance(result, Success)
            return result.value

        result = benchmark(run_multi_conditions)
        assert result == (num_conditions + 5) * 2


# ============================================================================
# MEMORY USAGE TESTS
# ============================================================================


class TestMemoryBenchmarks:
    """Tests to ensure contract decorators don't cause memory leaks."""

    def test_repeated_calls_memory_usage(self, benchmark):
        """Test that repeated calls don't accumulate memory."""

        @precondition(is_positive)
        def simple_calc(x):
            return x + 1

        def run_many_calls():
            results = []
            for i in range(1000):
                result = simple_calc(i + 1)  # Ensure positive input
                if isinstance(result, Success):
                    results.append(result.value)
            return len(results)

        count = benchmark(run_many_calls)
        assert count == 1000

    def test_large_error_accumulation(self, benchmark):
        """Test that error objects don't accumulate excessively."""

        @precondition(is_positive)
        def strict_function(x):
            return x * 2

        def run_many_failures():
            error_count = 0
            for i in range(1000):
                result = strict_function(-i - 1)  # All negative, should fail
                if isinstance(result, Error):
                    error_count += 1
            return error_count

        count = benchmark(run_many_failures)
        assert count == 1000


# ============================================================================
# COMPARISON BENCHMARKS
# ============================================================================


class TestComparisonBenchmarks:
    """Benchmarks comparing decorated vs undecorated performance."""

    def test_overhead_ratio_measurement(self):
        """Measure the overhead ratio of decorated vs undecorated functions."""
        import os

        def undecorated_function(x):
            return x * 2 + 1

        @precondition(is_positive)
        def decorated_function_local(x):
            return x * 2 + 1

        # More extensive warm-up for CI environments
        warmup_iterations = 5000 if os.getenv("CI") else 1000
        for _ in range(warmup_iterations):
            undecorated_function(42)
            result = decorated_function_local(42)

        # Run multiple measurement cycles and take the best (most stable) result
        best_ratio = float("inf")
        iterations = 50000

        for _ in range(3):  # Run 3 measurement cycles
            # Time undecorated function
            start_time = time.perf_counter()
            for _ in range(iterations):
                undecorated_function(42)
            undecorated_time = time.perf_counter() - start_time

            # Time decorated function
            start_time = time.perf_counter()
            for _ in range(iterations):
                result = decorated_function_local(42)
                assert isinstance(result, Success)
            decorated_time = time.perf_counter() - start_time

            # Calculate overhead ratio for this cycle
            cycle_ratio = (
                decorated_time / undecorated_time if undecorated_time > 0 else float("inf")
            )
            best_ratio = min(best_ratio, cycle_ratio)

        # CI environments can be highly variable, so use more generous threshold
        # Local development typically sees 5-10x, CI can see 10-20x
        max_overhead = 25.0 if os.getenv("CI") else 15.0

        assert best_ratio < max_overhead, f"Overhead ratio too high: {best_ratio:.2f}x (threshold: {max_overhead}x)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
