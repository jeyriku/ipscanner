"""Command-line entry point for the jeyipscan Django app.

Usage:
    jeyipscan           # runs development server on 127.0.0.1:8000
    jeyipscan runserver 0.0.0.0:8080

This module is used as a console script entry point by the package.
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipscanner.settings")
    try:
        from django.core.management import execute_from_command_line
    except Exception:
        # Provide a clearer error when Django is not available
        sys.stderr.write("Django is not installed in the active environment.\n")
        raise

    # If no arguments provided, start the dev server on localhost:8000
    if len(sys.argv) == 1:
        args = [sys.argv[0], "runserver", "127.0.0.1:8000"]
    else:
        args = sys.argv

    execute_from_command_line(args)


if __name__ == "__main__":
    main()
