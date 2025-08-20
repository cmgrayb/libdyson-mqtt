#!/usr/bin/env python3
"""
Script to build and publish libdyson-mqtt to PyPI.

Usage:
    python publish_to_pypi.py --test      # Upload to TestPyPI
    python publish_to_pypi.py --prod      # Upload to production PyPI
    python publish_to_pypi.py --check     # Just check the package without uploading
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(cmd: str, description: str) -> Optional[subprocess.CompletedProcess]:
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Exit code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def check_dependencies() -> None:
    """Check if required tools are installed."""
    print("🔍 Checking dependencies...")

    required_tools = ["twine", "build"]
    missing_tools = []

    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"   ✅ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
            print(f"   ❌ {tool} is not installed")

    if missing_tools:
        print(f"\n📦 Installing missing tools: {', '.join(missing_tools)}")
        install_cmd = f"pip install {' '.join(missing_tools)}"
        run_command(install_cmd, "Installing build tools")


def clean_build_artifacts() -> None:
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")

    paths_to_clean = ["dist/", "build/", "src/*.egg-info/", "*.egg-info/"]

    for path_pattern in paths_to_clean:
        for path in Path(".").glob(path_pattern):
            if path.exists():
                if path.is_dir():
                    import shutil

                    shutil.rmtree(path)
                    print(f"   🗑️  Removed directory: {path}")
                else:
                    path.unlink()
                    print(f"   🗑️  Removed file: {path}")


def run_quality_checks() -> None:
    """Run code quality checks before building."""
    print("🔍 Running quality checks...")

    # Check if code is formatted
    run_command("python -m black --check .", "Black formatting check")

    # Check imports
    run_command("python -m isort --check-only .", "Import sorting check")

    # Run linting
    run_command("python -m flake8 .", "Flake8 linting")

    print("✅ All quality checks passed")


def build_package() -> None:
    """Build the package."""
    run_command("python -m build", "Building package")

    # List built files
    dist_files = list(Path("dist").glob("*"))
    if dist_files:
        print("📦 Built packages:")
        for file in sorted(dist_files):
            print(f"   📄 {file}")
    else:
        print("❌ No package files found in dist/")
        sys.exit(1)


def check_package() -> None:
    """Check the package with twine."""
    run_command("python -m twine check dist/*", "Checking package with twine")


def upload_to_testpypi() -> None:
    """Upload to TestPyPI."""
    print("📤 Uploading to TestPyPI...")
    print("   You'll need your TestPyPI API token.")
    print("   Create one at: https://test.pypi.org/manage/account/")

    cmd = "python -m twine upload --repository testpypi dist/*"
    run_command(cmd, "Uploading to TestPyPI")

    print("\n🎉 Upload to TestPyPI successful!")
    print("📋 Test installation with:")
    print("   pip install -i https://test.pypi.org/simple/ libdyson-mqtt")


def upload_to_pypi() -> None:
    """Upload to production PyPI."""
    print("📤 Uploading to PyPI...")
    print("   You'll need your PyPI API token.")
    print("   Create one at: https://pypi.org/manage/account/")

    # Final confirmation
    response = input("\n⚠️  This will upload to PRODUCTION PyPI. Are you sure? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Upload cancelled")
        return

    cmd = "python -m twine upload dist/*"
    run_command(cmd, "Uploading to PyPI")

    print("\n🎉 Upload to PyPI successful!")
    print("📋 Install with:")
    print("   pip install libdyson-mqtt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and publish libdyson-mqtt to PyPI")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--prod", action="store_true", help="Upload to production PyPI")
    parser.add_argument("--check", action="store_true", help="Just build and check package")
    parser.add_argument("--skip-checks", action="store_true", help="Skip quality checks")

    args = parser.parse_args()

    if not any([args.test, args.prod, args.check]):
        parser.print_help()
        sys.exit(1)

    print("🚀 libdyson-mqtt PyPI Publisher")
    print("=" * 50)

    # Step 1: Check dependencies
    check_dependencies()

    # Step 2: Clean build artifacts
    clean_build_artifacts()

    # Step 3: Run quality checks (unless skipped)
    if not args.skip_checks:
        try:
            run_quality_checks()
        except SystemExit:
            print("\n⚠️  Quality checks failed. Use --skip-checks to bypass if needed.")
            sys.exit(1)

    # Step 4: Build package
    build_package()

    # Step 5: Check package
    check_package()

    # Step 6: Upload (if requested)
    if args.check:
        print("\n✅ Package check complete! Package is ready for upload.")
        print("📋 Next steps:")
        print("   python .github/scripts/publish_to_pypi.py --test   # Upload to TestPyPI")
        print("   python .github/scripts/publish_to_pypi.py --prod   # Upload to PyPI")
    elif args.test:
        upload_to_testpypi()
    elif args.prod:
        upload_to_pypi()

    print("\n🎯 All done!")


if __name__ == "__main__":
    main()
