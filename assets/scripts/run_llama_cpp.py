# @file assets/scripts/run_llama_cpp.py
# @description Download LLaMA model, check system, run llama.cpp with CUDA
# @version 2.7.11
# @license MIT

import sys, os, subprocess, argparse, logging, inspect  # noqa
from huggingface_hub import hf_hub_download
from rich.logging import RichHandler

P = argparse.ArgumentParser

path = {
    'models': os.path.join(os.getcwd(), 'data', 'models'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf',
    'llama': "/path/to/llama.cpp",
    'prompt': "Your prompt here",
    'wsl_cmd': "wsl -e bash -c"
}

cmd = {
    'make_clean':
    f"""
        cd {path['llama']} && \\
        make clean && make CUBLAS=1
    """,
    'run_llama':
    f"""
        ./main -m {os.path.join(path['models'], path['model'])} \\
        -p "{path['prompt']}"
    """
}

checks = {'wsl': ['wsl', '--version'], 'cuda': "nvcc --version", 'timeout': 10}
cuda_version = "12.2"
is_check = False

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)])

logger = logging.getLogger("rich")


def log(msg, level=logging.INFO):
    frame = inspect.stack()[1]
    filename = os.path.basename(frame.filename)
    lineno = frame.lineno
    logger.log(level, f"{msg} ({filename}:{lineno})")


def exit(msg, code=1):
    log(msg, logging.ERROR if code else logging.INFO)
    sys.exit(code)


def run(cmd):
    try:
        _stdout = subprocess.run(cmd,
                                 capture_output=True,
                                 text=True,
                                 timeout=checks['timeout'])
        if _stdout and _stdout.returncode == 0:
            return _stdout
    except subprocess.TimeoutExpired:
        log("Command timed out")
    except Exception as e:
        log(f"Failed to run command {cmd}: {e}", logging.ERROR)
    return None


def check_wsl():
    result = run(checks['wsl'])
    if result and result.stdout:
        text = result.stdout.split('\n')[0].split(':', 1)[1].strip()
        if text:
            log(f"Detected WSL version: {text}")
            return True
    exit("WSL not available. Install WSL. Try: 'wsl --install'")


def check_cuda():
    result = run(f"{path['wsl_cmd']} \"{checks['cuda']}\"")
    if result and result.stdout:
        log(f"Detected CUDA version: {result.stdout.strip()}")
        for line in result.stdout.split('\n'):
            if "release" in line:
                version = line.split()[-1]
                if version >= cuda_version:
                    log(f"CUDA version {version} is compatible.")
                    return True
                else:
                    exit(f"CUDA version {version} is not compatible. "
                         f"Required version: {cuda_version}")
    exit("CUDA not available. Install CUDA.")


def check_sys():
    check_wsl()
    check_cuda()
    log("System check passed.")


def dl():
    if not os.path.exists(path['models']):
        os.makedirs(path['models'])
    try:
        file_path = hf_hub_download(repo_id=path['repo'],
                                    filename=path['model'],
                                    local_dir=path['models'])
        log(f"Model downloaded to {file_path}")
    except Exception as e:
        exit(f"Failed to download model: {e}")


def run_llama_cpp():
    parser = P(description="Run LLaMA with llama.cpp and CUDA")
    parser.add_argument('--check', action='store_true', help="Check system")
    args = parser.parse_args()

    global is_check
    is_check = args.check
    log("Checking system...")
    check_sys()
    if is_check:
        log("System checks completed successfully.")
        return

    log("Checking for models and downloading if needed...")
    dl()
    result_clean = run(f"{path['wsl_cmd']} \"{cmd['make_clean']}\"")
    if result_clean:
        result_run = run(f"{path['wsl_cmd']} \"{cmd['run_llama']}\"")
        if not result_run:
            exit("Failed to run LLaMA command.")
    else:
        exit("Failed to clean and build LLaMA.")


if __name__ == "__main__":
    run_llama_cpp()
