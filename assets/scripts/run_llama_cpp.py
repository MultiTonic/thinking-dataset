# flake8: noqa
# @file assets/scripts/run_llama_cpp.py
# @description Download and install llama-cpp-python with CUDA toolkit and other required Python packages
# @version 2.9.5
# @license MIT

import sys
import subprocess
import traceback
from rich.console import Console
import signal

console = Console()

packages = {'py_pkgs': ['tqdm', 'requests']}

cmd = {
    'install_py_pkgs':
    f"{sys.executable} -m pip install {' '.join(packages['py_pkgs'])}",
    'install_llama_cpp_python':
    f"{sys.executable} -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124/"
}


def error(msg):
    tb = traceback.format_exc(limit=2)
    console.print(f"[red]An error occurred:[/red] {msg}")
    console.print(f"[red]Traceback:[/red]\n{tb}")
    sys.exit(1)


def run(cmd):
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
            raise RuntimeError(
                f"Command failed with return code {process.returncode}: "
                f"{stderr}")
        return stdout, stderr
    except Exception as e:
        error(f"Failed to run command {cmd}: {e}")


def install_py_pkgs():
    console.print(
        "[green]Starting installation of required Python packages[/green]")
    stdout, stderr = run(cmd['install_py_pkgs'])
    console.print(
        "[green]Installation of required Python packages completed successfully[/green]"
    )


def install_llama_cpp_python():
    console.print(
        "[green]Starting installation of llama-cpp-python with CUDA support[/green]"
    )
    stdout, stderr = run(cmd['install_llama_cpp_python'])
    console.print(
        "[green]Installation of llama-cpp-python with CUDA support completed successfully[/green]"
    )


def signal_handler(sig, frame):
    console.print("[red]Installation aborted by user.[/red]")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    try:
        install_py_pkgs()
        install_llama_cpp_python()
    except Exception as e:
        error(e)
