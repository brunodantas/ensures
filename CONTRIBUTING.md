# Contributing to ensures

Thank you for your interest in contributing to `ensures`! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ensures.git
   cd ensures
   ```
3. **Set up the development environment**:
   ```bash
   uv sync --dev
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Environment Setup
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/brunodantas/ensures.git
cd ensures
uv sync --dev
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run property-based tests
uv run pytest src/ensures/test_property_based.py

# Run performance benchmarks
uv run pytest src/ensures/test_benchmarks.py --benchmark-only
```

### Code Quality Checks
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy .
```

## 📝 Code Style

We use several tools to maintain code quality:

- **Ruff**: For formatting and linting
- **mypy**: For type checking
- **pytest**: For testing
- **Hypothesis**: For property-based testing

### Code Formatting
- Line length: 88 characters (Black compatible)
- Use type hints for all public APIs
- Follow PEP 8 naming conventions
- Write comprehensive docstrings using Google style

### Example Code Style
```python
from typing import Any, Callable
from ensures import precondition, postcondition, Success, Error


def positive_number(x: float) -> bool:
    """Check if a number is positive.
    
    Args:
        x: The number to check.
        
    Returns:
        True if the number is positive, False otherwise.
    """
    return x > 0


@precondition(positive_number)
@postcondition(lambda result: result > 0)
def square_root(x: float) -> float:
    """Calculate the square root of a positive number.
    
    Args:
        x: A positive number.
        
    Returns:
        The square root of x.
        
    Example:
        >>> result = square_root(4.0)
        >>> isinstance(result, Success)
        True
        >>> result.value
        2.0
    """
    return x ** 0.5
```

## 🧪 Testing Guidelines

### Test Coverage
- Maintain 100% test coverage for core functionality
- Write both unit tests and integration tests
- Use property-based testing for edge case discovery

### Test Types
1. **Unit Tests** (`tests.py`): Core functionality testing
2. **Property-Based Tests** (`test_property_based.py`): Edge case discovery
3. **Integration Tests** (`test_integration.py`): Real-world scenarios
4. **Benchmarks** (`test_benchmarks.py`): Performance validation

### Writing Tests
```python
import pytest
from hypothesis import given, strategies as st
from ensures import precondition, Success, Error


class TestPreconditions:
    def test_precondition_success(self):
        """Test successful precondition."""
        @precondition(lambda x: x > 0)
        def positive_function(x: int) -> int:
            return x * 2
            
        result = positive_function(5)
        assert isinstance(result, Success)
        assert result.value == 10
    
    @given(st.integers(max_value=0))
    def test_precondition_failure(self, x: int):
        """Property-based test for precondition failure."""
        @precondition(lambda x: x > 0)
        def positive_function(x: int) -> int:
            return x * 2
            
        result = positive_function(x)
        assert isinstance(result, Error)
```

## 📋 Contribution Process

### 1. Create an Issue
Before starting work, create an issue to discuss:
- Bug reports
- Feature requests
- Performance improvements
- Documentation updates

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes
- Write code following our style guidelines
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 4. Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat: add support for async functions`
- `fix: handle edge case in postcondition validation`
- `docs: improve precondition examples`
- `test: add property-based tests for invariants`

### 5. Submit Pull Request
- Push your branch to your fork
- Open a pull request against the main branch
- Fill out the pull request template
- Wait for review and address feedback

## 🔍 Pull Request Guidelines

### Before Submitting
- [ ] All tests pass
- [ ] Code is formatted with Ruff
- [ ] Type checking passes with mypy
- [ ] Documentation is updated
- [ ] Changelog is updated (for notable changes)

### PR Description Should Include
- Clear description of changes
- Link to related issue(s)
- Testing approach
- Breaking changes (if any)

## 🐛 Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Minimal code example reproducing the issue
- Expected behavior
- Actual behavior
- Error messages (if any)

## 💡 Feature Requests

For feature requests, please provide:
- Use case description
- Proposed API (if applicable)
- Examples of how it would be used
- Alternatives considered

## 📚 Documentation

We value good documentation:
- All public APIs must have comprehensive docstrings
- Include examples in docstrings
- Update README for significant features
- Keep changelog updated

## ⚡ Performance Considerations

- Run benchmarks for performance-critical changes
- Consider memory usage implications
- Maintain backward compatibility when possible

## 🎉 Recognition

Contributors will be recognized in:
- Git commit history
- Release notes
- Future contributor documentation

## 📞 Getting Help

- Open an issue for bugs or feature requests
- Check existing issues and discussions
- Review the documentation and examples

## 📄 License

By contributing, you agree that your contributions will be licensed under the GPL-3.0-or-later license.

---

Thank you for contributing to `ensures`! 🚀
