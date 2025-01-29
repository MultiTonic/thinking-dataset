"""Deploy and manage a Hugging Face model server.

This script sets up a Flask-based HTTP server to serve Hugging Face models,
    handling package dependencies and server initialization.

Functions:
    log: Logs a message to the console.
    run: Runs a shell command and collects output.
    collect_output: Collects subprocess output.
    error: Logs errors with traceback.
    dynamic_import: Imports packages dynamically.
    install_flask: Installs Flask package.
    install_transformers: Installs Transformers package.
    install_torch: Installs PyTorch package.
    initialize: Sets up server and installs dependencies.
"""

import sys
import subprocess
import traceback
import importlib
from rich.console import Console

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

app = None
console = Console()

cmd = {
    'install_flask':
    f"{sys.executable} -m pip install flask",
    'install_transformers':
    f"{sys.executable} -m pip install transformers",
    'install_torch': (f"{sys.executable} -m pip install torch "
                      "--index-url https://download.pytorch.org/whl/cu124")
}


def log(message: str) -> None:
    """Logs a message to the console.

    Args:
        message (str): The message to log.
    """
    console.print(message)


def run(command: str) -> tuple:
    """Runs a shell command and collects its output.

    Args:
        command (str): The command to run.

    Returns:
        tuple: The stdout and stderr output of the command.
    """
    process = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = collect_output(process)
    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed with return code {process.returncode}: {stderr}")
    return stdout, stderr


def collect_output(process: subprocess.Popen) -> tuple:
    """Collects the output of a subprocess.

    Args:
        process (subprocess.Popen): The subprocess to collect output from.

    Returns:
        tuple: The stdout and stderr output of the subprocess.
    """
    stdout, stderr = [], []
    for line in iter(process.stdout.readline, ''):
        console.print(line, end='')
        stdout.append(line)
    for line in iter(process.stderr.readline, ''):
        console.print(line, end='')
        stderr.append(line)
    process.stdout.close()
    process.stderr.close()
    process.wait()
    return ''.join(stdout), ''.join(stderr)


def error(msg: str) -> None:
    """Logs an error message and traceback.

    Args:
        msg (str): The error message to log.
    """
    tb = traceback.format_exc(limit=2)
    log(f"[red]An error occurred:[/red] {msg}")
    log(f"[red]Traceback:[/red]\n{tb}")
    sys.exit(1)


def dynamic_import(package_name: str):
    """Dynamically imports a package.

    Args:
        package_name (str): The name of the package to import.

    Returns:
        module: The imported module.
    """
    try:
        module = importlib.import_module(package_name)
        return module
    except ImportError:
        log(f"[red]Failed to import package: {package_name}[/red]")
        raise


def install_flask() -> None:
    """Installs Flask."""
    log("[green]Starting installation of Flask[/green]")
    try:
        run(cmd['install_flask'])
        log("[green]Installation of Flask completed successfully[/green]")
    except Exception as e:
        error(f"Failed to install Flask: {e}")


def install_transformers() -> None:
    """Installs the Transformers library."""
    log("[green]Starting installation of Transformers[/green]")
    try:
        run(cmd['install_transformers'])
        log("[green]Installation of Transformers completed![/green]")
    except Exception as e:
        error(f"Failed to install Transformers: {e}")


def install_torch() -> None:
    """Installs the Torch library."""
    log("[green]Starting installation of torch[/green]")
    try:
        run(cmd['install_torch'])
        log("[green]Installation of torch completed successfully[/green]")
    except Exception as e:
        error(f"Failed to install torch: {e}")


def initialize() -> None:
    """Initializes the server and installs required packages."""
    install_flask()
    install_transformers()
    install_torch()

    flask = dynamic_import('flask')
    global Flask, request, jsonify
    Flask = flask.Flask
    request = flask.request
    jsonify = flask.jsonify

    transformers = dynamic_import('transformers')
    global pipeline
    pipeline = transformers.pipeline

    # Create an instance of the pipeline and test text completion
    pipe = pipeline("text-generation",
                    model="meta-llama/Llama-3.1-8B-Instruct")

    messages = [{"role": "user", "content": "Who are you?"}]
    response = pipe(messages)
    print(response)

    global app
    app = Flask(__name__)


if __name__ == "__main__":
    try:
        initialize()
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        error(f"Failed to start server: {e}")
