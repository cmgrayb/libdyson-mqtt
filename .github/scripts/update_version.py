#!/usr/bin/env python3
"""
Version Update Script for libdyson-mqtt

Updates pyproject.toml version based on command line arguments.
Supports PEP 440 compliant versioning.

Usage:
    python scripts/update_version.py 0.3.0a1      # Set to alpha
    python scripts/update_version.py 0.3.0b1      # Set to beta
    python scripts/update_version.py 0.3.0rc1     # Set to release candidate
    python scripts/update_version.py 0.3.0        # Set to stable
    python scripts/update_version.py --increment alpha  # Auto-increment to next alpha
    python scripts/update_version.py --increment beta   # Auto-increment to next beta
"""

import argparse
import re
import sys
from pathlib import Path


def get_current_version() -> str:
    """Extract current version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def set_version(new_version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace version line
    new_content = re.sub(r'^version = "[^"]+"', f'version = "{new_version}"', content, flags=re.MULTILINE)

    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Updated version to: {new_version}")


def parse_and_increment_alpha(current: str, base_version: str) -> str:
    """Handle alpha version incrementing"""
    if "a" in current:
        # Increment existing alpha
        alpha_match = re.search(r"a(\d+)", current)
        if alpha_match:
            alpha_num = int(alpha_match.group(1)) + 1
            return f"{base_version}a{alpha_num}"
        else:
            return f"{base_version}a1"
    else:
        # Start new alpha series
        return f"{base_version}a1"


def parse_and_increment_beta(current: str, base_version: str) -> str:
    """Handle beta version incrementing"""
    if "b" in current:
        # Increment existing beta
        beta_match = re.search(r"b(\d+)", current)
        if beta_match:
            beta_num = int(beta_match.group(1)) + 1
            return f"{base_version}b{beta_num}"
        else:
            return f"{base_version}b1"
    else:
        # Start new beta series
        return f"{base_version}b1"


def parse_and_increment_rc(current: str, base_version: str) -> str:
    """Handle release candidate version incrementing"""
    if "rc" in current:
        # Increment existing rc
        rc_match = re.search(r"rc(\d+)", current)
        if rc_match:
            rc_num = int(rc_match.group(1)) + 1
            return f"{base_version}rc{rc_num}"
        else:
            return f"{base_version}rc1"
    else:
        # Start new rc series
        return f"{base_version}rc1"


def increment_version(version_type: str) -> str:
    """Auto-increment version based on current version"""
    current = get_current_version()

    # Parse current version
    base_match = re.match(r"(\d+\.\d+\.\d+)", current)
    if not base_match:
        raise ValueError(f"Could not parse base version from: {current}")

    base_version = base_match.group(1)

    # Increment logic
    if version_type == "alpha":
        return parse_and_increment_alpha(current, base_version)
    elif version_type == "beta":
        return parse_and_increment_beta(current, base_version)
    elif version_type == "rc":
        return parse_and_increment_rc(current, base_version)
    else:
        raise ValueError(f"Unknown version type: {version_type}")


def validate_version(version: str) -> bool:
    """Validate PEP 440 compliance"""
    pep440_pattern = r"^(\d+!)?\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$"
    if not re.match(pep440_pattern, version):
        raise ValueError(f"Version '{version}' is not PEP 440 compliant")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update version in pyproject.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("version", nargs="?", help="Explicit version to set")
    group.add_argument("--increment", choices=["alpha", "beta", "rc"], help="Auto-increment version type")
    group.add_argument("--show", action="store_true", help="Show current version")

    args = parser.parse_args()

    try:
        if args.show:
            current = get_current_version()
            print(f"Current version: {current}")

        elif args.increment:
            new_version = increment_version(args.increment)
            validate_version(new_version)
            set_version(new_version)

        elif args.version:
            validate_version(args.version)
            set_version(args.version)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
