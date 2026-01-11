# Build and Distribution Guide

This document explains how to build, package, and distribute Liquid ASCII Art Animation.

## Table of Contents

- [Building the Package](#building-the-package)
- [Docker Images](#docker-images)
- [Publishing to PyPI](#publishing-to-pypi)
- [Creating Releases](#creating-releases)
- [Testing Distribution](#testing-distribution)

---

## Building the Package

### Prerequisites

- Python 3.11 or later
- uv (installed automatically by `./dev.sh`)
- Build tools (gcc, portaudio for audio support)

### Local Build

Build the Python wheel and source distribution:

```bash
# Using dev script
./dev.sh install

# Or manually
pip install build
python -m build
```

This creates distribution files in `dist/`:
- `liquid_ascii-0.2.0-py3-none-any.whl` (wheel)
- `liquid_ascii-0.2.0.tar.gz` (source distribution)

### Testing Local Build

Install and test the built package:

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate  # Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/liquid_ascii-0.2.0-py3-none-any.whl

# Test installation
liquid-ascii --help
liquid-ascii --speak "Testing installation"

# Clean up
deactivate
rm -rf test-env
```

---

## Docker Images

### Building Docker Image

```bash
# Build image
docker build -t liquid-ascii:latest .

# Build with specific version tag
docker build -t liquid-ascii:0.2.0 .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t liquid-ascii:latest .
```

### Testing Docker Image

```bash
# Run demo mode
docker run -it --rm liquid-ascii:latest

# Run with custom command
docker run -it --rm liquid-ascii:latest --speak "Hello from Docker!"

# Run with audio support (Linux)
docker run -it --rm --device /dev/snd liquid-ascii:latest --speak "Audio test"

# Interactive mode
docker run -it --rm liquid-ascii:latest --interactive
```

### Using Docker Compose

```bash
# Run demo
docker-compose --profile demo up

# Run different profiles
docker-compose --profile speak up
docker-compose --profile alien up
docker-compose --profile robot up

# Custom command
docker-compose run --rm liquid-ascii-base --character baby --quality ultra
```

### Publishing Docker Images

```bash
# Tag for GitHub Container Registry
docker tag liquid-ascii:latest ghcr.io/YOUR_ORG/liquid-ascii:latest
docker tag liquid-ascii:latest ghcr.io/YOUR_ORG/liquid-ascii:0.2.0

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push images
docker push ghcr.io/YOUR_ORG/liquid-ascii:latest
docker push ghcr.io/YOUR_ORG/liquid-ascii:0.2.0
```

---

## Publishing to PyPI

### Prerequisites

- PyPI account (https://pypi.org/account/register/)
- API token (https://pypi.org/manage/account/token/)

### Manual Publication

```bash
# Install twine
pip install twine

# Build package
python -m build

# Check distribution
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ liquid-ascii

# Upload to PyPI (production)
twine upload dist/*
```

### Automated Publication

The project uses GitHub Actions for automated releases:

1. **Update version** in `pyproject.toml`
2. **Commit changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   ```
3. **Create and push tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. **GitHub Actions automatically**:
   - Runs tests
   - Builds package
   - Publishes to PyPI
   - Creates GitHub release
   - Builds and pushes Docker images

### Setting Up PyPI Token

Add `PYPI_API_TOKEN` to GitHub repository secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token
5. Save

---

## Creating Releases

### Release Checklist

Before creating a release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Run full test suite: `./dev.sh test`
- [ ] Run benchmarks: `python benchmarks/render_benchmark.py`
- [ ] Test in Docker: `docker build -t liquid-ascii:test . && docker run -it liquid-ascii:test`
- [ ] Update README.md if needed
- [ ] Update documentation

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backward compatible
- **PATCH** (0.2.1): Bug fixes, backward compatible

### Manual Release

```bash
# Update version
vim pyproject.toml

# Update changelog
vim CHANGELOG.md

# Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.2.0"

# Create tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push changes and tag
git push origin main
git push origin v0.2.0
```

### Automated Release (Recommended)

Push a version tag to trigger automated release:

```bash
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions will:
1. Run tests and linters
2. Build Python package
3. Publish to PyPI
4. Create GitHub release with notes
5. Build multi-platform Docker images
6. Push to GitHub Container Registry

---

## Testing Distribution

### Test PyPI Package

```bash
# Install from PyPI
pip install liquid-ascii

# Verify installation
liquid-ascii --version
liquid-ascii --help

# Test functionality
liquid-ascii --speak "Testing PyPI installation"
liquid-ascii --character alien --quality high
```

### Test Docker Image

```bash
# Pull from registry
docker pull ghcr.io/YOUR_ORG/liquid-ascii:latest

# Run tests
docker run -it --rm ghcr.io/YOUR_ORG/liquid-ascii:latest --help
docker run -it --rm ghcr.io/YOUR_ORG/liquid-ascii:latest --character robot
```

### Verify All Installation Methods

Test all documented installation methods:

1. **PyPI**: `pip install liquid-ascii`
2. **Docker**: `docker run ghcr.io/YOUR_ORG/liquid-ascii`
3. **From source**: `git clone && ./dev.sh setup`

---

## CI/CD Pipeline

### GitHub Actions Workflows

The project includes several CI/CD workflows:

1. **test.yml** - Run tests on push/PR
2. **lint.yml** - Code quality checks
3. **release.yml** - Automated releases on tags

### Workflow Triggers

- **test.yml**: Runs on every push and pull request
- **lint.yml**: Runs on every push to main and PRs
- **release.yml**: Triggers on version tags (v*)

### Required Secrets

Configure these in repository settings:

- `PYPI_API_TOKEN` - PyPI publishing (required for releases)
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

---

## Troubleshooting

### Build Failures

**Error: "No module named 'src'"**
```bash
# Ensure you're in project root
cd /path/to/liquid-ascii
python -m build
```

**Error: "PortAudio not found"**
```bash
# Install system dependencies
# Ubuntu/Debian:
sudo apt-get install portaudio19-dev

# macOS:
brew install portaudio

# Then rebuild
pip install --force-reinstall sounddevice
```

### Docker Build Issues

**Error: "failed to solve: process terminated"**
```bash
# Clear build cache
docker builder prune -af

# Rebuild without cache
docker build --no-cache -t liquid-ascii:latest .
```

### PyPI Upload Issues

**Error: "403 Forbidden"**
- Verify API token is correct
- Check token permissions (must allow upload)
- Ensure package name is available

**Error: "File already exists"**
- Version already published
- Increment version in pyproject.toml
- Rebuild and upload new version

---

## Distribution Artifacts

### Python Package

- **Wheel**: `liquid_ascii-VERSION-py3-none-any.whl`
  - Platform-independent
  - Fast installation
  - Recommended for pip install

- **Source**: `liquid_ascii-VERSION.tar.gz`
  - Contains full source code
  - Used for building from source
  - Includes tests and documentation

### Docker Images

- **Platforms**: linux/amd64, linux/arm64
- **Base**: python:3.11-slim
- **Size**: ~300MB (optimized)
- **Registry**: ghcr.io/YOUR_ORG/liquid-ascii

### Tags

- `latest` - Most recent release
- `0.2.0` - Specific version
- `0.2` - Minor version (tracks patches)
- `0` - Major version (tracks minors)

---

## Best Practices

### Before Release

1. Run full test suite with coverage
2. Test on multiple platforms (Linux, macOS, Windows)
3. Verify Docker build
4. Update documentation
5. Create release notes

### Release Notes

Include in releases:
- New features
- Bug fixes
- Breaking changes
- Upgrade instructions
- Deprecations

### Version Tags

Always use semantic versioning:
- Format: `vMAJOR.MINOR.PATCH` (e.g., v0.2.0)
- Prefix with 'v'
- Match version in pyproject.toml

### Security

- Never commit API tokens
- Use GitHub Secrets for credentials
- Scan dependencies regularly
- Keep base images updated

---

## Additional Resources

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
