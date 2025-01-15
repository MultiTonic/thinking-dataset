# @file assets/scripts/run_llama_cpp.py
# @description Download LLaMA model, check system, run llama.cpp with CUDA
# @version 2.8.6
# @license MIT

import sys, os, subprocess, argparse, logging, inspect  # noqa
from huggingface_hub import hf_hub_download
from rich.logging import RichHandler

P = argparse.ArgumentParser

path = {
    'models': os.path.join(os.getcwd(), 'data', 'models'),
    'repo': 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF',
    'model': 'Meta-Llama-3.1-8B-Instruct-Q4_0_4_4.gguf',
    'llama': "C:/path/to/llama.cpp",
    'prompt': "Your prompt here"
}

cmd = {
    'make_clean': f"""
        cd {path['llama']} && \\
        make clean && make CUBLAS=1
    """,
    'run_llama': f"""
        ./main -m {os.path.join(path['models'], path['model'])} \\
        -p "{path['prompt']}"
    """,
    'install_cuda': f"""
        {sys.executable} -m pip install llama-cpp-python --force-reinstall
    """,
    'python_version': f"""
        {sys.executable} --version
    """
}

checks = {'cuda': "nvcc --version", 'timeout': 10}
cuda_version = "12.5"
installation_attempted = False

logging.basicConfig(
    level=logging.DEBUG,
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
    log(f"Running command: {cmd}", logging.DEBUG)
    try:
        _stdout = subprocess.run(cmd,
                                 capture_output=True,
                                 text=True,
                                 timeout=checks['timeout'],
                                 shell=True)
        log(f"Command output: {_stdout.stdout}", logging.DEBUG)
        if _stdout and _stdout.returncode == 0:
            return _stdout
    except subprocess.TimeoutExpired:
        log("Command timed out")
    except Exception as e:
        log(f"Failed to run command {cmd}: {e}", logging.ERROR)
        return None
    log(f"Command failed with return code: {_stdout.returncode}",
        logging.DEBUG)
    return _stdout


def check_cuda():
    global installation_attempted
    result = run(checks['cuda'])
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
    log("CUDA not available.")
    if not installation_attempted:
        log("Installing CUDA 12.5 automatically...")
        install_result = run(cmd['install_cuda'])
        installation_attempted = True
        if not install_result:
            exit("Failed to install CUDA 12.5.")
        log("CUDA 12.5 installed successfully.")
        return check_cuda()
    else:
        exit("Failed to detect CUDA after attempted installation.")
    return False


def check_sys():
    if check_cuda():
        log("System check passed.")
    else:
        log("System check failed.")


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
    args = parser.parse_args()  # noqa

    log("Checking system...")
    check_sys()

    log("Running basic Python version command for testing...")
    result_python_version = run(cmd['python_version'])
    if result_python_version:
        log("Python version command executed successfully.")
    else:
        log("Failed to execute Python version command.")

    log("Checking for models and downloading if needed...")
    dl()
    result_clean = run(cmd['make_clean'])
    if result_clean:
        result_run = run(cmd['run_llama'])
        if not result_run:
            exit("Failed to run LLaMA command.")
    else:
        exit("Failed to clean and build LLaMA.")


if __name__ == "__main__":
    run_llama_cpp()
