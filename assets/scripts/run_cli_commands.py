# @file run_cli_commands.py
# @description Run workflow: clean, download, process, load, export.
# @version 1.0.2
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
        "thinking-dataset process", "thinking-dataset load",
        "thinking-dataset export"
    ]

    for command in commands:
        print(f"Running command: {command}")
        run_command(command)
