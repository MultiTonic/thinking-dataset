# flake8: noqa
# @file assets/scripts/run_llama_cpp.py
# @description Download and install llama-cpp-python with CUDA toolkit and other required Python packages, and download model using hfapi
# @version 3.0.0
# @license MIT

import sys
import subprocess
import traceback
from rich.console import Console
import signal
import os
from huggingface_hub import hf_hub_download

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


def download_model():
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


def signal_handler(sig, frame):
    console.print("[red]Installation aborted by user.[/red]")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    try:
        install_py_pkgs()
        install_llama_cpp_python()
        # model_path = download_model()

        from llama_cpp import Llama

        llm = Llama.from_pretrained(
            repo_id="bullerwins/DeepSeek-V3-GGUF",
            filename=
            "DeepSeek-V3-Q4_K_M/DeepSeek-V3-Q4_K_M-00001-of-00010.gguf",
        )

        print(
            llm.create_chat_completion(
                messages="What is the answer to the universe?"))

    except Exception as e:
        error(e)
