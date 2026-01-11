# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Liquid ASCII project.

## Overview

The project uses **GitHub Actions** for automated testing, linting, and quality checks on every push and pull request.

## Workflows

### 1. Test Workflow (`.github/workflows/test.yml`)

Runs comprehensive tests across multiple Python versions and operating systems.

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Test Matrix:**
- **Python versions**: 3.11, 3.12, 3.13
- **Operating systems**: Ubuntu (latest), macOS (latest), Windows (latest)
- **Total combinations**: 9 test runs per push

**Steps:**
1. Checkout code
2. Set up Python environment
3. Install uv (fast package installer)
4. Create virtual environment
5. Install dependencies (requirements.txt, requirements-dev.txt)
6. Run pytest with coverage
7. Upload coverage to Codecov (Ubuntu + Python 3.11 only)

**Coverage Reporting:**
- Coverage reports generated in XML and terminal formats
- Uploaded to [Codecov](https://codecov.io) for tracking over time
- Badge available for README

**Status Badge:**
```markdown
![Tests](https://github.com/michelabboud/liquid-ascii/actions/workflows/test.yml/badge.svg)
```

### 2. Lint Workflow (`.github/workflows/lint.yml`)

Runs code quality checks and type checking.

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Jobs:**

#### Ruff (Linter & Formatter)
- Fast Python linter and formatter written in Rust
- Checks for code style issues, bugs, and complexity
- Verifies code formatting consistency

**Rules enabled:**
- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `N` - pep8-naming
- `UP` - pyupgrade (modern syntax)
- `B` - flake8-bugbear (common bugs)
- `C4` - flake8-comprehensions
- `SIM` - flake8-simplify

**Configuration:** `ruff.toml`

#### MyPy (Type Checking)
- Static type checker for Python
- Catches type errors before runtime
- Ensures type hint consistency
- Currently non-blocking (continues on error)

**Configuration:** `mypy.ini`

**Status Badge:**
```markdown
![Lint](https://github.com/michelabboud/liquid-ascii/actions/workflows/lint.yml/badge.svg)
```

## Local Development

### Running Tests Locally

```bash
# Run all tests
./dev.sh test

# Run with coverage
./dev.sh test --coverage

# Run specific test file
./dev.sh test tests/test_sdf.py

# Run with verbose output
./dev.sh test -v
```

### Running Linters Locally

```bash
# Install dev dependencies
./dev.sh install

# Activate virtual environment
source .venv/bin/activate

# Run ruff check
ruff check .

# Run ruff with auto-fix
ruff check . --fix

# Run ruff formatter
ruff format .

# Run mypy type checking
mypy src/ --ignore-missing-imports --no-strict-optional
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Configuration:** `.pre-commit-config.yaml`

The hooks will automatically:
- Run ruff linter and formatter
- Run mypy type checking
- Fix trailing whitespace
- Ensure files end with newline
- Check YAML/TOML syntax
- Prevent large file commits
- Check for merge conflicts

## Configuration Files

### `ruff.toml`
Ruff linter and formatter configuration.

**Key settings:**
- Target: Python 3.11+
- Line length: 100 characters
- Enabled rules: E, W, F, I, N, UP, B, C4, SIM
- Excludes: `.venv`, `__pycache__`, `build`, `dist`

### `mypy.ini`
MyPy type checker configuration.

**Key settings:**
- Python version: 3.11
- Ignore missing imports: Yes
- Strict optional: No (for gradual typing)
- Show error codes: Yes
- Excludes: tests, setup

### `pytest.ini`
Pytest test runner configuration.

**Key settings:**
- Test paths: `tests/`
- Min pytest version: 7.0
- Coverage reporting: term-missing, html, xml
- Test markers: unit, integration, slow, benchmark, visual

### `.pre-commit-config.yaml`
Pre-commit hooks configuration.

**Hooks:**
- Ruff (linter + formatter)
- MyPy (type checking)
- General file checks (trailing whitespace, EOF, YAML/TOML validation)

## Performance

**Test Execution Times** (approximate):
- Unit tests: ~0.1s (31 tests)
- All tests with coverage: ~0.2s
- Full CI pipeline (9 combinations): ~5-10 minutes

**Lint Execution Times** (approximate):
- Ruff check: ~0.5s
- Ruff format check: ~0.3s
- MyPy: ~3-5s

## Troubleshooting

### Tests Failing Locally But Passing in CI

**Possible causes:**
1. Different Python version (check with `python --version`)
2. Stale virtual environment (run `./dev.sh clean && ./dev.sh setup`)
3. Missing dependencies (run `./dev.sh install`)
4. Platform-specific issues (test on same OS as CI)

### Linter Failures

**"Ruff check failed":**
- Run `ruff check . --fix` to auto-fix issues
- Check `ruff.toml` for rule configuration
- Some rules may need manual fixes

**"Ruff format failed":**
- Run `ruff format .` to auto-format all files
- Format is deterministic and should match CI

**"MyPy errors":**
- MyPy is currently non-blocking (won't fail CI)
- Fix by adding type hints or `# type: ignore` comments
- Check `mypy.ini` for configuration

### Coverage Not Uploading

**Requirements:**
- Must run on Ubuntu with Python 3.11
- Requires `CODECOV_TOKEN` secret in GitHub repository
- Token can be obtained from [codecov.io](https://codecov.io)

**Setup:**
1. Go to https://codecov.io and sign in with GitHub
2. Add repository
3. Copy the token
4. Add as `CODECOV_TOKEN` in GitHub repo secrets (Settings → Secrets → Actions)

## Adding New Tests

1. Create test file in `tests/` directory
2. Name file `test_*.py`
3. Name test functions `test_*()`
4. Use pytest fixtures and markers
5. Run locally to verify
6. Commit and push (CI will run automatically)

**Example:**
```python
# tests/test_myfeature.py
import pytest

def test_my_feature():
    """Test my new feature."""
    result = my_feature()
    assert result == expected_value
```

## Adding New Lint Rules

1. Edit `ruff.toml` to add/remove rules
2. Run `ruff check .` locally to test
3. Fix any new violations
4. Commit configuration change
5. CI will use new rules on next push

## Future Enhancements

- [ ] Add benchmark workflow for performance regression testing
- [ ] Add release workflow for automated PyPI publishing
- [ ] Add documentation build/deploy workflow
- [ ] Add Docker image build workflow
- [ ] Add dependency update automation (Dependabot)
- [ ] Add security scanning (Bandit, Safety)
- [ ] Add code complexity analysis
- [ ] Add test result dashboard

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Pre-commit Documentation](https://pre-commit.com/)
