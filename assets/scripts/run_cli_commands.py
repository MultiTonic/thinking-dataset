"""Run CLI commands for Thinking Dataset.

This script runs a series of CLI commands for the Thinking Dataset project.

Functions:
    run_command: Runs a single CLI command.
    main: Main function to run all CLI commands in sequence.
"""

import subprocess

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


def run_command(command: str) -> None:
    """Runs a single CLI command.

    Args:
        command (str): The CLI command to run.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(result.stdout, end='')
    except subprocess.CalledProcessError as e:
        print(f"Error while executing {command}: {e.stderr}")


def main() -> None:
    """Main function to run all CLI commands in sequence."""
    commands = [
        "thinking-dataset clean",
        "thinking-dataset download",
        "thinking-dataset process",
        "thinking-dataset load",
        "thinking-dataset generate",
        "thinking-dataset export",
        "thinking-dataset upload",
    ]

    for command in commands:
        run_command(command)


if __name__ == "__main__":
    main()
