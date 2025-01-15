# @file run_hf_server.py
# @description Simple HTTP server that handles only JSON
# @version 1.0.4
# @license MIT
# flake8: noqa

import sys, subprocess, traceback, importlib  # noqa
from rich.console import Console

app = None
console = Console()

cmd = {
    'install_flask':
    f"{sys.executable} -m pip install flask",
    'install_transformers':
    f"{sys.executable} -m pip install transformers",
    'install_torch':
    f"{sys.executable} -m pip install torch --index-url https://download.pytorch.org/whl/cu124"
}


def log(message):
    console.print(message)


def run(command):
    process = subprocess.Popen(command,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = collect_output(process)
    if process.returncode != 0:
        raise RuntimeError("Command failed with return code "
                           f"{process.returncode}: {stderr}")
    return stdout, stderr


def collect_output(process):
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


def error(msg):
    tb = traceback.format_exc(limit=2)
    log(f"[red]An error occurred:[/red] {msg}")
    log(f"[red]Traceback:[/red]\n{tb}")
    return {"error": msg}, 500


def dynamic_import(package_name):
    try:
        module = importlib.import_module(package_name)
        return module
    except ImportError:
        log(f"[red]Failed to import package: {package_name}[/red]")
        raise


def install_flask():
    log("[green]Starting installation of Flask[/green]")
    try:
        run(cmd['install_flask'])
        log("[green]Installation of Flask completed successfully[/green]")
    except Exception as e:
        return error(f"Failed to install Flask: {e}")


def install_transformers():
    log("[green]Starting installation of Transformers[/green]")
    try:
        run(cmd['install_transformers'])
        log("[green]Installation of Transformers completed successfully[/green]"
            )
    except Exception as e:
        return error(f"Failed to install Transformers: {e}")


def install_torch():
    log("[green]Starting installation of torch[/green]")
    try:
        run(cmd['install_torch'])
        log("[green]Installation of torch completed successfully[/green]")
    except Exception as e:
        return error(f"Failed to install torch: {e}")


def initialize():
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

    messages = [
        {
            "role": "user",
            "content": "Who are you?"
        },
    ]

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
