"""Run the project's static checks and optional PostgreSQL-backed regression suite.

Use uv run python scripts/check.py for the full gate, or append --static-only
when database configuration is unavailable. This command never runs live batches.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def commands(static_only: bool) -> list[list[str]]:
    """Build the fixed sequence of local quality checks without model commands."""
    python = sys.executable
    checks = [
        [python, "-m", "ruff", "format", "--check", "."],
        [python, "-m", "ruff", "check", "."],
        [python, "scripts/check_docstrings.py"],
    ]
    if not static_only:
        checks.extend(
            [
                [python, "manage.py", "check"],
                [python, "manage.py", "makemigrations", "--check", "--dry-run"],
                [python, "-m", "pytest", "-q"],
            ]
        )
    return checks


def run_checks(root: Path, static_only: bool) -> int:
    """Run checks in order and return immediately on the first nonzero exit."""
    for command in commands(static_only):
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            return result.returncode
    print("All requested checks passed.", flush=True)
    return 0


def main() -> int:
    """Parse the static-only option and execute checks from the repository root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    options = parser.parse_args()
    return run_checks(Path(__file__).resolve().parents[1], options.static_only)


if __name__ == "__main__":
    raise SystemExit(main())
