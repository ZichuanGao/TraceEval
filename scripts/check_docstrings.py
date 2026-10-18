"""Check triple-double-quoted docstrings on every Python definition.

Run with uv run python scripts/check_docstrings.py from the repository root.
No database configuration or external service credentials are required.
"""

import ast
from pathlib import Path

DEFINITIONS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
PLACEHOLDERS = {"todo", "tbd", "fixme", "placeholder", "..."}


def python_files(root: Path) -> list[Path]:
    """Return repository-owned Python sources, tests, scripts, and manage.py."""
    paths = [
        path
        for directory in ("src", "tests", "scripts")
        for path in (root / directory).rglob("*.py")
    ]
    if (root / "manage.py").is_file():
        paths.append(root / "manage.py")
    return sorted(set(paths))


def check_source(source: str, filename: str = "<memory>") -> list[str]:
    """Report undocumented modules and definitions, including private ones.

    Args:
        source: Python source text to parse without executing it.
        filename: Display name used in diagnostics.

    Returns:
        Diagnostics for missing, blank, incorrectly quoted, or placeholder
        docstrings. Invalid Python syntax produces a diagnostic as well.
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [f"{filename}:{exc.lineno}: invalid Python syntax"]
    objects = [("<module>", tree)] + [
        (node.name, node) for node in ast.walk(tree) if isinstance(node, DEFINITIONS)
    ]
    issues = []
    for name, node in objects:
        location = f"{filename}:{getattr(node, 'lineno', 1)}: {name}"
        docstring = ast.get_docstring(node, clean=False)
        if not docstring or not docstring.strip():
            issues.append(f"{location}: missing nonempty docstring")
            continue
        literal = ast.get_source_segment(source, node.body[0]) or ""
        if not literal.startswith(('"""', 'r"""', 'R"""')):
            issues.append(f"{location}: use triple double quotes")
        summary = docstring.strip().splitlines()[0].strip().casefold()
        if summary in PLACEHOLDERS or summary.rstrip(".") in PLACEHOLDERS:
            issues.append(f"{location}: replace placeholder with a behavior description")
    return issues


def check_repository(root: Path) -> tuple[list[str], int]:
    """Return all docstring violations and the number of inspected definitions."""
    issues = []
    definitions = 0
    for path in python_files(root):
        name = str(path.relative_to(root))
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issues.append(f"{name}: cannot read UTF-8 source")
            continue
        issues.extend(check_source(source, name))
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        definitions += sum(isinstance(node, DEFINITIONS) for node in ast.walk(tree))
    return issues, definitions


def main() -> int:
    """Print actionable violations and fail when any required docstring is absent."""
    root = Path(__file__).resolve().parents[1]
    issues, definitions = check_repository(root)
    if issues:
        print("\n".join(issues))
        print(f"Docstring check failed: {len(issues)} issue(s).")
        return 1
    print(f"Docstring check passed: {definitions} class/function definitions, no exceptions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
