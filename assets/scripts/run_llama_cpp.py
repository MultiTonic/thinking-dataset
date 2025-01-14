# @file assets/scripts/run_llama_cpp.py
# @description Download LLaMA model, check system, run llama.cpp with CUDA
# @version 2.6.9
# @license MIT

import sys
import os
import subprocess
import argparse
from huggingface_hub import hf_hub_download
from rich.logging import RichHandler
import logging

paths = {
    'models': os.path.join(os.getcwd(), 'data', 'models', '8B'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf',
    'llama': "/path/to/llama.cpp",
    'prompt': "Your prompt here",
    'wsl_cmd': "wsl -e bash -c"
}
checks = {'wsl': ['wsl', '--version'], 'timeout': 10}
cmd = {
    'make_clean':
    f"""
    cd {paths['llama']} && \\
    make clean && make CUBLAS=1
    """,
    'run_llama':
    f"""
    ./main -m {os.path.join(paths['models'], paths['model'])} \\
    -p "{paths['prompt']}"
    """
}

is_check = False


def _log():
    logging.basicConfig(level=logging.INFO,
                        format="%(message)s",
                        datefmt="[%X]",
                        handlers=[RichHandler()])
    return logging.getLogger("rich")


log = _log()


def log_msg(msg, level=logging.INFO):
    log.log(level, msg)


def exit_script(msg, code=1):
    log_msg(msg, logging.ERROR if code else logging.INFO)
    sys.exit(code)


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd,
                                capture_output=True,
                                text=True,
                                timeout=checks['timeout'])
        if result and result.returncode == 0:
            return result
    except subprocess.TimeoutExpired:
        log_msg("Command timed out")
    except Exception as e:
        log_msg(f"Failed to run command {cmd}: {e}", logging.ERROR)
    return None


def check_wsl():
    log_msg("Checking WSL installation...")
    result = run_cmd(checks['wsl'])
    if result and result.stdout:
        version_line = result.stdout.split('\n')[0]
        truncated_version = version_line.split(':', 1)[1].strip()
        if truncated_version:
            log_msg(f"Detected WSL version: {truncated_version}")
            return True
    log_msg("WSL not installed or failed to detect WSL version.")
    exit_script("WSL not available. Install WSL. Try: 'wsl --install'")


def check_sys():
    check_wsl()
    log_msg("System check passed.")


def download():
    if not os.path.exists(paths['models']):
        os.makedirs(paths['models'])
        log_msg(f"Creating models dir at {paths['models']}")
    log_msg("Checking if models need download from Hugging Face Hub...")
    try:
        model_path = hf_hub_download(repo_id=paths['repo'],
                                     filename=paths['model'],
                                     local_dir=paths['models'])
        log_msg(f"Model downloaded and saved to {model_path}")
    except Exception as e:
        exit_script(f"Failed to download model: {e}")


def run_llama():
    parser = argparse.ArgumentParser(
        description="Run LLaMA with llama.cpp and CUDA")
    parser.add_argument('--check', action='store_true', help="Check system")
    parser.add_argument('--bypass',
                        action='store_true',
                        help="Bypass system check")

    args = parser.parse_args()

    global is_check
    is_check = args.check

    if not args.bypass:
        log_msg("Checking system...")
        check_sys()

    if is_check:
        log_msg("System checks completed successfully.")
        return

    log_msg("Checking for models and downloading if needed...")
    download()

    wsl_command_clean = f"{paths['wsl_cmd']} \"{cmd['make_clean']}\""
    wsl_command_run = f"{paths['wsl_cmd']} \"{cmd['run_llama']}\""
    log_msg(f"Executing WSL make clean command: {wsl_command_clean}")
    result_clean = run_cmd(wsl_command_clean)

    if result_clean:
        log_msg(f"Executing WSL run command: {wsl_command_run}")
        result_run = run_cmd(wsl_command_run)
        if not result_run:
            exit_script("Failed to run LLaMA command.")
    else:
        exit_script("Failed to clean and build LLaMA.")


if __name__ == "__main__":
    run_llama()
