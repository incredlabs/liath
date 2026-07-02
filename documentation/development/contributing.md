# Contributing

Thank you for your interest in contributing to Liath!

## Getting Started

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/incredlabs/liath.git
   cd liath
   ```

2. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies:
   ```bash
   poetry install --with docs --all-extras
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=liath

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest -v
```

### Building Documentation

```bash
# Build documentation
mkdocs build

# Serve locally
mkdocs serve
# Open http://localhost:8000
```

## Code Style

### Python Style

- Follow PEP 8
- Use type hints where practical
- Maximum line length: 100 characters
- Use docstrings for public APIs (Google style)

### Docstring Format

```python
def function_name(param1: str, param2: int) -> dict:
    """Short description of function.

    Longer description if needed, explaining behavior,
    side effects, or important details.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.

    Example:
        >>> function_name("test", 42)
        {'result': 'test42'}
    """
```

### Commit Messages

Use conventional commits:

```
feat: Add new vector search capability
fix: Resolve memory leak in cache plugin
docs: Update installation guide
test: Add tests for batch operations
refactor: Simplify query execution flow
```

## Pull Request Process

### Before Submitting

1. **Create an issue** (for significant changes)
2. **Fork the repository**
3. **Create a feature branch**: `git checkout -b feat/my-feature`
4. **Write tests** for new functionality
5. **Update documentation** if needed
6. **Run tests**: `pytest`
7. **Run linting**: `poetry run flake8`

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] PR description explains changes

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (describe)

## Testing
How was this tested?

## Related Issues
Fixes #123
```

## Development Guidelines

### Adding a New Plugin

1. Create file in `liath/plugins/`
2. Inherit from `PluginBase`
3. Implement required methods
4. Add tests in `tests/`
5. Document in `documentation/plugins/`

### Modifying Core Components

1. Discuss in an issue first
2. Consider backward compatibility
3. Update all affected tests
4. Update documentation

### Adding Dependencies

1. Use `poetry add <package>`
2. Consider if it should be optional
3. Document in installation guide

## Architecture Decisions

### Adding New Storage Backend

1. Inherit from `StorageBase`
2. Implement all abstract methods
3. Add to storage selection logic
4. Test thoroughly with existing tests
5. Document configuration

### Modifying Query Execution

1. Consider Lua sandboxing implications
2. Test with complex queries
3. Benchmark performance impact

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG
3. Create git tag
4. GitHub Actions publishes to PyPI

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email maintainers directly

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers feel welcome

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
