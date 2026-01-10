# Contributing Guide

Thank you for your interest in contributing to Liquid ASCII Art Animation!

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version, terminal)

### Suggesting Features

1. Check existing issues/discussions
2. Create an issue with:
   - Feature description
   - Use case / motivation
   - Proposed implementation (if any)

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/liquid-ascii.git
cd liquid-ascii

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Code Style

- Follow PEP 8
- Use type hints where practical
- Add docstrings for public functions
- Keep functions focused and small

### Example

```python
def calculate_something(value: float, factor: float = 1.0) -> float:
    """
    Calculate something important.

    Args:
        value: Input value
        factor: Multiplier (default: 1.0)

    Returns:
        Calculated result
    """
    return value * factor
```

## Project Structure

```
src/
├── renderer/    # Add new SDF primitives here
├── model/       # Add character models here
├── audio/       # Add TTS backends here
├── terminal/    # Add display features here
└── main.py      # Entry point
```

## Adding New Features

### New Character

1. Edit `src/model/head.py`
2. Add geometry to `HeadGeometry`
3. Add preset to `CharacterHead._get_character_geometry()`

### New Color Scheme

1. Edit `src/terminal/colors.py`
2. Add to `PRESET_SCHEMES` dictionary

### New SDF Primitive

1. Edit `src/renderer/sdf.py`
2. Follow existing function signatures
3. Add to `__init__.py` exports

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_sdf.py
```

## Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for technical changes
- Add docstrings to new code

## Pull Request Checklist

- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

## Questions?

Feel free to open a discussion or issue!
