"""Setup script for Thinking Dataset.

This script sets up the virtual environment, installs dependencies,
and configures the thinking-dataset CLI tool.

Functions:
    _print_usage: Prints usage information for the thinking-dataset CLI.
    _is_package_installed: Checks if the thinking-dataset package is installed.
    _create_virtual_environment: Creates a virtual environment
        if it doesn't exist.
    _install_dependencies: Installs project dependencies.
    _upgrade_existing_installation: Upgrades the existing installation.
    _install_tool: Installs the thinking-dataset CLI tool.
    main: Main function to run the setup process.
"""

import subprocess
import os
from assets.scripts.uv.theme import console

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"


def _print_usage() -> None:
    """Prints usage information for the thinking-dataset CLI."""
    console.print("[text][bold]Thinking Dataset:[/bold] "
                  "An [italic]extremely[/italic] smart dataset.[/text]")
    console.print()
    console.print("[key]Usage:[/key] [command]thinking-dataset[/command] "
                  "[param]<OPTION>[/param] [param]<COMMAND>[/param] "
                  "[param]<ARGS>[/param]")
    console.print()
    console.print("[key]Commands:[/key]")
    console.print("  [command]download[/command]: "
                  "[text]Download datasets[/text]")
    console.print("  [command]process[/command]: "
                  "[text]Process downloaded data[/text]")
    console.print("  [command]load[/command]: "
                  "[text]Load data into the database[/text]")
    console.print("  [command]generate[/command]: "
                  "[text]Generate synthetic data[/text]")
    console.print("  [command]export[/command]: "
                  "[text]Export processed data[/text]")
    console.print("  [command]upload[/command]: "
                  "[text]Upload data to HuggingFace[/text]")
    console.print("  [command]clean[/command]: "
                  "[text]Clean data directory[/text]")
    console.print("  [command]ls[/command]: "
                  "[text]List files in the dataset directory[/text]")
    console.print()
    console.print("[text]For more information, visit:[/text] "
                  "[key]https://github.com/MultiTonic/thinking-dataset[/key]")
    console.print()
    console.print("[text]Use 'thinking-dataset help' for more details.[/text]")


def _is_package_installed() -> bool:
    """Checks if the thinking-dataset package is installed."""
    try:
        result = subprocess.run(['uv', 'tool', 'list'],
                                capture_output=True,
                                text=True)
        return 'thinking-dataset' in result.stdout
    except subprocess.CalledProcessError:
        return False


def _create_virtual_environment() -> None:
    """Creates a virtual environment if it doesn't exist."""
    if not os.path.exists('.venv'):
        console.print("[text]Creating virtual environment...[/text]")
        subprocess.check_call(['uv', 'venv', '.venv'])


def _install_dependencies() -> None:
    """Installs project dependencies."""
    console.print("[text]Installing dependencies...[/text]")
    subprocess.check_call(['uv', 'pip', 'install', '-e', '.[dev]'])


def _upgrade_existing_installation() -> None:
    """Upgrades the existing installation."""
    console.print("[text]Upgrading existing installation...[/text]")
    subprocess.check_call(
        ['uv', 'pip', 'install', '--upgrade', '-e', '.[dev]'])
    subprocess.check_call(['uv', 'tool', 'upgrade', 'thinking-dataset'])


def _install_tool() -> None:
    """Installs the thinking-dataset CLI tool."""
    console.print("[text]Installing thinking-dataset CLI...[/text]")
    subprocess.check_call(['uv', 'tool', 'install', '-e', '.'])


def main() -> None:
    """Main function to run the setup process."""
    try:
        is_installed = _is_package_installed()

        _create_virtual_environment()

        if is_installed:
            _upgrade_existing_installation()
        else:
            _install_dependencies()
            _install_tool()

        console.clear()
        _print_usage()
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to setup environment:[/red] {e}")
    except Exception as e:
        console.print(f"[red]An error occurred:[/red] {e}")


if __name__ == "__main__":
    main()
