"""Verify strict docstring coverage beyond Ruff's public-definition checks."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from scripts.check import run_checks
from scripts.check_docstrings import check_repository, check_source, python_files


@pytest.mark.parametrize(
    "definition",
    [
        "class Hidden: pass",
        "def _private(): pass",
        "async def _private(): pass",
        'class Wrapped:\n    """Describe wrapped behavior."""\n    def __init__(self): pass',
        'def outer():\n    """Describe outer behavior."""\n    def nested(): pass',
        'class Wrapped:\n    """Describe wrapped behavior."""\n    class Meta: pass',
    ],
)
def test_private_nested_magic_and_meta_require_docstrings(definition):
    """Reject missing docstrings on definitions that public-only checks can omit."""
    source = '"""Describe the fixture module."""\n' + definition + "\n"
    assert any("missing nonempty docstring" in issue for issue in check_source(source))


@pytest.mark.parametrize(
    "docstring", ['"A short string."', "'''A single-quoted string.'''", '"""   """', '"""TODO"""']
)
def test_incorrect_quotes_blank_and_placeholder_are_rejected(docstring):
    """Reject string literals that do not meet the project's documentation rule."""
    source = '"""Describe the fixture module."""\ndef documented():\n    ' + docstring + "\n"
    assert check_source(source)


def test_documented_private_and_nested_definitions_are_accepted():
    """Accept a documented module, class, constructor, and nested async function."""
    source = '''"""Describe the fixture module."""
class Example:
    """Keep the example interface explicit."""

    def __init__(self):
        """Initialize the example without external resources."""
        async def _nested():
            """Return a local result."""
            return 1
'''
    assert check_source(source) == []


def test_syntax_errors_report_a_failure_without_execution():
    """Turn invalid syntax into a diagnostic rather than executing fixture code."""
    assert "invalid Python syntax" in check_source("def broken(")[0]


def test_file_discovery_excludes_private_environment_and_virtualenv(tmp_path):
    """Inspect owned Python files without scanning environment or dependency trees."""
    for name in [
        "src/module.py",
        "tests/test_module.py",
        "scripts/check.py",
        ".venv/private.py",
        ".env",
        "manage.py",
    ]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('"""Describe the fixture module."""\n')
    names = {str(path.relative_to(tmp_path)) for path in python_files(tmp_path)}
    assert names == {"src/module.py", "tests/test_module.py", "scripts/check.py", "manage.py"}
    issues, definitions = check_repository(tmp_path)
    assert issues == [] and definitions == 0


def test_quality_gate_stops_at_first_failure(tmp_path):
    """Stop after a failed check rather than running later database or test steps."""
    with patch(
        "scripts.check.subprocess.run",
        side_effect=[SimpleNamespace(returncode=0), SimpleNamespace(returncode=7)],
    ) as run:
        assert run_checks(tmp_path, static_only=False) == 7
    assert run.call_count == 2


def test_repository_docstrings_cover_every_definition():
    """Keep full docstring coverage enforced even when pytest runs without the main gate."""
    issues, definitions = check_repository(Path(__file__).resolve().parents[1])
    assert issues == [], "\n".join(issues)
    assert definitions > 0
