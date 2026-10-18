"""Provide the TraceEval management-command entry point."""

import os
import sys


def main():
    """Run Django management commands through the project's uv entry point."""
    # Keep core imports independent of the Django management subsystem.
    from django.core.management import execute_from_command_line

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traceeval.settings")
    execute_from_command_line(sys.argv)
