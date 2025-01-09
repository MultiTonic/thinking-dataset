# @file run_cli_commands.py
# @description Run workflow: clean, download, prepare, load, export.
# @version 1.0.1
# @license MIT

import subprocess


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(result.stdout, end='')
    except subprocess.CalledProcessError as e:
        print(f"Error while executing {command}: {e.stderr}")


if __name__ == "__main__":
    commands = [
        "thinking-dataset clean", "thinking-dataset download",
        "thinking-dataset prepare", "thinking-dataset load",
        "thinking-dataset export"
    ]

    for command in commands:
        print(f"Running command: {command}")
        run_command(command)
