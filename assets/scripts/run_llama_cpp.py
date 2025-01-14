# @file assets/scripts/run_llama_cpp.py
# @description Download LLaMA model, check system, run llama.cpp with CUDA
# @version 2.6.5
# @license MIT

import sys
import os
import subprocess
import argparse
from huggingface_hub import hf_hub_download
from rich.console import Console
from rich.logging import RichHandler
import logging

g_paths = {
    'models': os.path.join(os.getcwd(), 'data', 'models', '8B'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf',
    'llama': "/path/to/llama.cpp",
    'prompt': "Your prompt here",
    'wsl_cmd': "wsl -e bash -c"
}
g_checks = {
    'wsl': ['wsl', '--list', '--verbose'],
    'cuda': ['nvidia-smi'],
    'timeout': 10
}
g_cmd = {
    'llama':
    f"""
    cd {g_paths['llama']}
    make clean && make CUBLAS=1
    ./main -m {os.path.join(g_paths['models'],
                            g_paths['model'])} -p "{g_paths['prompt']}"
    """
}

g_console = Console()


def _log():
    logging.basicConfig(level="NOTSET",
                        format="%(message)s",
                        datefmt="[%X]",
                        handlers=[RichHandler()])
    return logging.getLogger("rich")


g_log = _log()


def log(msg, level=logging.INFO):
    g_log.log(level, msg)


def exit(msg, code=1):
    log(msg, logging.ERROR if code else logging.INFO)
    sys.exit(code)


def run(cmd):
    try:
        return subprocess.run(cmd,
                              capture_output=True,
                              text=True,
                              timeout=g_checks['timeout'])
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        log(f"Failed to run command {cmd}: {e}", logging.ERROR)
        return None


def check_wsl2():
    log("Checking WSL2...")
    result = run(g_checks['wsl'])
    if result and 'WSL 2' in result.stdout:
        log("WSL2 is available.")
        return True
    return False


def check_cuda():
    log("Checking CUDA...")
    result = run(g_checks['cuda'])
    if result and 'CUDA' in result.stdout:
        log("CUDA is available.")
        return True
    log("CUDA not available or an error occurred. Ensure CUDA is installed.")
    return False


def check_sys():
    if not check_wsl2():
        exit("WSL2 not available. Update/install WSL2. Try: 'wsl --install'")
    if not check_cuda():
        exit("CUDA not available. Install CUDA for GPU.")
    log("System check passed.")


def download():
    if not os.path.exists(g_paths['models']):
        os.makedirs(g_paths['models'])
        log(f"Creating models dir at {g_paths['models']}")

    log("Checking if models need download from Hugging Face Hub...")
    try:
        model_path = hf_hub_download(repo_id=g_paths['repo'],
                                     filename=g_paths['model'],
                                     local_dir=g_paths['models'])
        log(f"Model downloaded and saved to {model_path}")
    except Exception as e:
        exit(f"Failed to download model: {e}")


def run_llama():
    parser = argparse.ArgumentParser(
        description="Run LLaMA with llama.cpp and CUDA")
    parser.add_argument('--check', action='store_true', help="Check system")

    args = parser.parse_args()

    log("Checking system...")
    check_sys()

    if not args.check:
        log("Checking for models and downloading if needed...")
        download()
        os.system(f"{g_paths['wsl_cmd']} '{g_cmd['llama']}'")


if __name__ == "__main__":
    run_llama()
