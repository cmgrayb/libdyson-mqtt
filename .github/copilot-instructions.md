# Copilot Instructions for libdyson-mqtt

## Project Overview
This is a Python 3 library for interacting with Dyson products over MQTT. The library is designed to be consumed as public code and must maintain high code quality standards.

## Development Standards

### Code Quality Tools
- **Black**: Code formatting (line length: 120 characters)
- **Flake8**: Linting and style checking
- **isort**: Import sorting and organization
- **Pytest**: Unit and integration testing

### Code Quality Requirements
- All code must pass black formatting
- All code must pass flake8 linting (PEP 8 compliance)
- All imports must be sorted with isort
- All tests must pass before commits
- Minimum test coverage should be maintained

### Project Structure
```
libdyson-mqtt/
├── src/
│   └── libdyson_mqtt/
│       ├── __init__.py
│       ├── client.py
│       ├── exceptions.py
│       ├── models/
│       └── utils/
├── tests/
│   ├── unit/
│   └── integration/
├── .venv/
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .flake8
├── .pre-commit-config.yaml
└── .vscode/
    └── tasks.json
```

## Configuration Files

### pyproject.toml
- Black configuration
- isort configuration
- Project metadata
- Build system configuration

### .flake8
- Flake8 configuration
- Ignore rules if necessary
- Max line length: 120 (to match Black)

### requirements.txt
- Production dependencies only
- Pinned versions for reproducibility

### requirements-dev.txt
- Development dependencies (black, flake8, isort, pytest, etc.)
- Pre-commit hooks

## VSCode Tasks
The following tasks should be available:
- **Format Code**: Run black on the entire codebase
- **Lint Code**: Run flake8 on the entire codebase
- **Sort Imports**: Run isort on the entire codebase
- **Run Tests**: Execute pytest with coverage
- **Check All**: Run all quality checks in sequence
- **Setup Dev Environment**: Create venv and install dependencies

## Testing Strategy
- Unit tests for individual functions and classes
- Integration tests for API interactions
- Mock external API calls in unit tests
- Use real API endpoints in integration tests (with proper credentials)
- Maintain test coverage above 80%

## Security Considerations
- No hardcoded credentials or sensitive data
- API hostnames and decryption keys are the only allowed static values
- Use environment variables for configuration
- Validate all user inputs
- Sanitize API responses

## API Design Principles
- Clean, intuitive public interface
- Proper exception handling with custom exception classes
- Type hints for all public methods
- Comprehensive docstrings following Google or NumPy style
- Support for both synchronous and asynchronous operations (if needed)

## Development Workflow
1. Create/activate virtual environment
2. Install development dependencies
3. Make changes following coding standards
4. Run format/lint/test tasks
5. Ensure all checks pass before committing
6. Use pre-commit hooks for automated checks

## Dependencies Management
- Use virtual environments for isolation
- Pin exact versions in requirements.txt
- Use requirements-dev.txt for development tools
- Regular dependency updates with testing

## Version Synchronization Process
When updating development tool versions, ensure consistency across all configuration files:

### Current Tool Versions (as of Aug 16, 2025)
- Black: 25.1.0
- Flake8: 7.3.0
- isort: 6.0.1
- pytest: 8.4.1
- pytest-cov: 6.2.1
- mypy: 1.17.1
- pre-commit: 4.3.0
- types-requests: 2.32.4.20250809
- types-cryptography: 3.3.23.2

### Step-by-Step Version Update Process

1. **Check Local Environment Versions**
   ```bash
   # Activate virtual environment
   .venv\Scripts\activate

   # Check currently installed versions
   pip list | findstr "black flake8 isort pytest mypy"
   ```

2. **Synchronize requirements-dev.txt**
   - Update to exact version pins matching pre-commit hooks
   - Use `==` instead of `>=` for consistency
   - Include all development dependencies with exact versions

3. **Update pyproject.toml Optional Dependencies**
   - Match the exact versions from requirements-dev.txt
   - Update `[project.optional-dependencies].dev` section
   - Use exact version pins (`==`) for consistency

4. **Verification Steps**
   ```bash
   # Install updated dependencies
   pip install -r requirements-dev.txt

   # Verify all tools work locally
   python -m black --check .
   python -m flake8 .
   python -m isort --check-only .
   python -m mypy src/
   python -m pytest

   # Verify pre-commit hooks work
   pre-commit run --all-files
   ```

5. **Files to Update**
   - `requirements-dev.txt` (manual exact version pins)
   - `pyproject.toml` (`[project.optional-dependencies].dev` section)

### Version Selection Strategy
- Use newest available versions when possible
- Always verify all quality checks pass after version updates
- Document version changes for future reference

## Continuous Integration
- All PRs must pass quality checks
- Automated testing on multiple Python versions
- Code coverage reporting
- Security scanning of dependencies
- **Important**: CI workflows must install package in development mode (`pip install -e .`) for tests to import modules

## Documentation
- README with clear usage examples
- API documentation generated from docstrings
- Contributing guidelines
- Changelog maintenance

## Common Commands
```bash
# Setup development environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
pip install -e .  # Install package in development mode for testing

# Code quality checks
python -m black --check .
python -m flake8 .
python -m isort --check-only .
python -m mypy src/
python -m pytest

# Pre-commit setup
pre-commit install
pre-commit run --all-files

# Version synchronization (automated)
python scripts/sync_versions.py --verbose          # Full synchronization
python scripts/sync_versions.py --dry-run --verbose # Preview changes only

# Then manually update requirements-dev.txt and pyproject.toml to match
pip install -r requirements-dev.txt     # Install updated versions
```

## VSCode Tasks
The project includes comprehensive VSCode tasks accessible via Ctrl+Shift+P → "Tasks: Run Task":

### Development Tasks
- **Setup Dev Environment**: Create virtual environment
- **Install Dev Dependencies**: Install development packages
- **Format Code**: Run Black code formatting
- **Lint Code**: Run Flake8 linting with problem matchers
- **Sort Imports**: Run isort import sorting
- **Type Check**: Run mypy type checking with problem matchers
- **Check All**: Run complete quality check sequence

### Testing Tasks
- **Run Tests**: Execute full test suite with coverage
- **Run Unit Tests**: Execute unit tests only
- **Run Integration Tests**: Execute integration tests only

### Security Scanning Tasks (Docker-based)
- **Security Scan (Bandit)**: Run Bandit security scanner using Docker container (cross-platform)
- **Security Scan (Safety)**: Check for known security vulnerabilities in dependencies using Docker
- **Security Scan (All)**: Run all security scans using Docker containers

### Version Management Tasks
- **Sync Tool Versions (Python)**: Automated version synchronization using Python script
- **Sync Tool Versions (Dry Run)**: Preview version changes without modifications
- **Update Tool Versions**: Update pre-commit versions only (manual process step 1)
- **Verify Version Sync**: Run all quality checks after version updates

## GitHub Actions CI/CD

The project includes comprehensive GitHub Actions workflows for continuous integration and quality assurance:

### Quality Assurance Workflows
- **Code Quality Checks**: Black formatting, Flake8 linting, isort imports, mypy types, pytest tests across Python 3.9-3.13
- **Build Testing**: Cross-platform package building and installation testing (Ubuntu/Windows/macOS)

### Security and Maintenance
- **Security Scanning**: Weekly vulnerability scanning with Safety and Bandit tools
- **Dependency Updates**: Automated monitoring with GitHub issue creation for available updates
- **Version Synchronization**: Validates tool version alignment across configuration files

### CI Pipeline Features
- **Smart Execution**: Skips CI for draft PRs (unless `ci-force` label present)
- **Parallel Processing**: Runs quality checks simultaneously for faster feedback
- **Automated PR Comments**: Provides actionable feedback directly in pull requests
- **Artifact Management**: Stores build artifacts and security reports for review

### Branch Protection Requirements
Required status checks for merge approval:
- Quality checks pass (Python 3.11)
- Build test passes (Ubuntu/Python 3.11)
- Version sync check (when configuration files modified)

See `.github/workflows/README.md` for detailed workflow documentation and troubleshooting guides.

## Automated Dependency Management

The project uses Renovate Bot for self-hosted automated dependency management:

### Self-hosted Renovate Features
- **No external reporting**: All dependency scanning happens locally within GitHub
- **Automated PRs**: Creates pull requests for dependency updates weekly (Mondays 6 AM UTC)
- **Intelligent grouping**: Groups related dependencies (dev tools, production, security)
- **Version synchronization**: Automatically reminds to run `python scripts/sync_versions.py` after quality tool updates
- **Security alerts**: Immediate PRs for vulnerability fixes

### Dependency Update Categories
- **Production dependencies** (requirements.txt): 7-day minimum age, conservative updates
- **Development dependencies** (requirements-dev.txt): 3-day minimum age, requires version sync
- **Code quality tools** (black, flake8, isort, mypy, pytest): Critical - must run version sync after merge
- **Pre-commit hooks**: Auto-updates with version sync requirements
- **GitHub Actions**: Updates workflow dependencies
- **Security tools**: 1-day minimum age for faster security patches

### Renovate Configuration
- **Configuration**: `renovate.json` - Main Renovate settings
- **Workflow**: `.github/workflows/renovate.yml` - Self-hosted execution
- **Dashboard**: Automatic dependency dashboard issue for overview
- **Manual trigger**: Available via GitHub Actions for immediate checks
