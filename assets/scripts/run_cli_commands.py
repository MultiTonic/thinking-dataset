"""Run CLI commands for Thinking Dataset.

This script runs a series of CLI commands for the Thinking Dataset project.

Functions:
    main: Main function to run all CLI commands in sequence.
"""

import subprocess
import sys

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


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

    try:
        for command in commands:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout, end='')
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.cmd}")
        print(f"Error output:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
