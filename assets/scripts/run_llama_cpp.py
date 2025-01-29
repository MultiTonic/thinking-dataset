"""Script to install llama-cpp-python with CUDA toolkit and other required
    packages.

This script installs the llama-cpp-python package with CUDA support and other
required Python packages. It also downloads a model using the Hugging Face API.

Functions:
    error: Logs an error message and traceback.
    run: Runs a shell command and collects its output.
    install_py_pkgs: Installs required Python packages.
    install_llama_cpp_python: Installs llama-cpp-python with CUDA support.
    download_model: Downloads a model from the Hugging Face Hub.
    signal_handler: Handles the SIGINT signal to abort installation.
"""

import sys
import subprocess
import traceback
from rich.console import Console
import signal
import os
from huggingface_hub import hf_hub_download

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

console = Console()

path = {
    'models': os.path.join(os.getcwd(), 'data', 'models'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf'
}

packages = {
    'py_pkgs': ['tqdm', 'requests', 'huggingface_hub'],
    'llama_cpp': ['llama-cpp-python']
}

cmd = {
    'install_py_pkgs':
    f"{sys.executable} -m pip install {' '.join(packages['py_pkgs'])}",
    'install_llama_cpp_python':
    (f"{sys.executable} -m pip install llama-cpp-python "
     "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124/")
}


def error(msg: str) -> None:
    """Logs an error message and traceback.

    Args:
        msg (str): The error message to log.
    """
    tb = traceback.format_exc(limit=2)
    console.print(f"[red]An error occurred:[/red] {msg}")
    console.print(f"[red]Traceback:[/red]\n{tb}")
    sys.exit(1)


def run(cmd: str) -> tuple:
    """Runs a shell command and collects its output.

    Args:
        cmd (str): The command to run.

    Returns:
        tuple: The stdout and stderr output of the command.
    """
    console.print(f"[blue]Running command:[/blue] {cmd}")
    try:
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
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
        stdout = ''.join(stdout)
        stderr = ''.join(stderr)
        if process.returncode != 0:
            raise RuntimeError(f"Command failed with return code "
                               f"{process.returncode}: {stderr}")
        return stdout, stderr
    except Exception as e:
        error(f"Failed to run command {cmd}: {e}")


def install_py_pkgs() -> None:
    """Installs required Python packages."""
    console.print(
        "[green]Starting installation of required Python packages[/green]")
    stdout, stderr = run(cmd['install_py_pkgs'])
    console.print(
        "[green]Installation of required Python packages completed![/green]")


def install_llama_cpp_python() -> None:
    """Installs llama-cpp-python with CUDA support."""
    console.print("[green]Starting installation of llama-cpp-python "
                  "with CUDA support[/green]")
    stdout, stderr = run(cmd['install_llama_cpp_python'])
    console.print("[green]Installation of llama-cpp-python "
                  "with CUDA support completed successfully[/green]")


def download_model() -> str:
    """Downloads a model from the Hugging Face Hub.

    Returns:
        str: The path to the downloaded model.
    """
    console.print(
        "[green]Starting model download from Hugging Face Hub[/green]")
    if not os.path.exists(path['models']):
        os.makedirs(path['models'])
    try:
        file_path = hf_hub_download(repo_id=path['repo'],
                                    filename=path['model'],
                                    local_dir=path['models'])
        console.print(f"[green]Model downloaded to {file_path}[/green]")
    except Exception as e:
        error(f"Failed to download model: {e}")
    return file_path


def signal_handler(sig, frame) -> None:
    """Handles the SIGINT signal to abort installation.

    Args:
        sig: The signal number.
        frame: The current stack frame.
    """
    console.print("[red]Installation aborted by user.[/red]")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    try:
        install_py_pkgs()
        install_llama_cpp_python()
        # model_path = download_model()

        from llama_cpp import Llama  # type: ignore # noqa: E402

        llm = Llama.from_pretrained(
            repo_id="bullerwins/DeepSeek-V3-GGUF",
            filename=  # noqa
            "DeepSeek-V3-Q4_K_M/DeepSeek-V3-Q4_K_M-00001-of-00010.gguf",
        )

        print(
            llm.create_chat_completion(
                messages="What is the answer to the universe?"))

    except Exception as e:
        error(e)
