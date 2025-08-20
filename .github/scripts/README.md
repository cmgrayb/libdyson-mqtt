# CI/CD Scripts

This directory contains scripts used by the Continuous Integration and Continuous Deployment (CI/CD) pipeline.

## Scripts

### `publish_to_pypi.py`
**Purpose**: Build and publish the package to PyPI/TestPyPI.

**Features**:
- Quality checks (Black, Flake8, isort)
- Package building with `python -m build`
- Package validation with Twine
- Upload to TestPyPI and PyPI
- Dependency management

**Usage**:

From project root:
```bash
# Build and validate package only
python .github/scripts/publish_to_pypi.py --check

# Upload to TestPyPI for testing
python .github/scripts/publish_to_pypi.py --test

# Upload to production PyPI
python .github/scripts/publish_to_pypi.py --prod

# Skip quality checks (use with caution)
python .github/scripts/publish_to_pypi.py --check --skip-checks
```

**GitHub Actions Integration**:
This script can be used locally for development, but the GitHub Actions workflow uses the standard tools directly:
- `python -m build` for building
- `twine upload` for publishing

**Prerequisites**:
- PyPI/TestPyPI API tokens set up
- All dependencies installed (`pip install build twine`)
- Package passes quality checks

## Notes

- These scripts are designed for **CI/CD use** and **local development**
- They are **not included** in the PyPI package distribution
- Scripts assume they're run from the project root directory
- All scripts include error handling and detailed output for debugging

## Directory Structure

```
.github/
├── scripts/
│   └── publish_to_pypi.py    # Build and publish automation
└── workflows/
    └── publish-to-pypi.yml   # GitHub Actions workflow
```

## Best Practices

1. **Test locally first**: Always test with `--check` before publishing
2. **Use TestPyPI**: Test uploads with `--test` before production
3. **Quality checks**: Don't skip quality checks unless absolutely necessary
4. **Token security**: Never commit API tokens to version control
5. **Version management**: Update version in `pyproject.toml` before publishing
