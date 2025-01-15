# @file assets/scripts/run_llama_cpp.py
# @description Download LLaMA model, check system, run llama.cpp with CUDA
# @version 2.8.8
# @license MIT

import sys
import os
import subprocess
import traceback
from huggingface_hub import hf_hub_download
from rich.console import Console

console = Console()

path = {
    'models': os.path.join(os.getcwd(), 'data', 'models'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf',
    'prompt': "Your prompt here"
}

cmd = {
    'run_llama':
    (f"llama-cpp-python -m {os.path.join(path['models'], path['model'])} "
     f"-p '{path['prompt']}'"),
    'install_cuda':
    f"{sys.executable} -m pip install llama-cpp-python"
}


def error(msg):
    tb = traceback.format_exc(limit=2)
    console.print(f"[red]An error occurred:[/red] {msg}")
    console.print(f"[red]Traceback:[/red]\n{tb}")
    sys.exit(1)


def run_command(command):
    console.print(f"[blue]Running command:[/blue] {command}")
    try:
        process = subprocess.Popen(command,
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
        error(f"Failed to run command {command}: {e}")


def install_llama_cpp():
    console.print("[green]Starting installation of llama-cpp-python[/green]")
    stdout, stderr = run_command(cmd['install_cuda'])
    console.print("[green]Installation of llama-cpp-python "
                  "completed successfully[/green]")


def download_model():
    console.print("[green]Checking model directory and "
                  "downloading model if necessary[/green]")
    if not os.path.exists(path['models']):
        os.makedirs(path['models'])
        console.print(
            f"[green]Created directory for models at {path['models']}[/green]")
    try:
        file_path = hf_hub_download(repo_id=path['repo'],
                                    filename=path['model'],
                                    local_dir=path['models'])
        console.print(f"[green]Model downloaded to {file_path}[/green]")
    except Exception as e:
        error(f"Failed to download model: {e}")


def run_llama():
    console.print("[green]Running llama-cpp-python[/green]")
    stdout, stderr = run_command(cmd['run_llama'])
    console.print(
        "[green]Execution of llama-cpp-python completed successfully[/green]")


if __name__ == "__main__":
    try:
        install_llama_cpp()
        download_model()
        run_llama()
    except Exception as e:
        error(e)
