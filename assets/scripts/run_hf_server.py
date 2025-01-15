# @file assets/scripts/run_hf_serve.py
# @description Simple HTTP server that handles only JSON
# @version 1.0.1
# @license MIT
# flake8: qa

import sys, subprocess, traceback, importlib  # noqa
from rich.console import Console

app = None
console = Console()

packages = {'py': ['flask', 'tqdm', 'requests', 'huggingface_hub']}

cmd = {
    'install_pkgs':
    f"{sys.executable} -m pip install {' '.join(packages['py'])}"
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


def install_pkgs():
    log("[green]Starting installation of required Python packages[/green]")
    try:
        run(cmd['install_pkgs'])
        log("[green]Installation of required Python "
            "packages completed successfully[/green]")
    except Exception as e:
        return error(f"Failed to install Python packages: {e}")


if __name__ == "__main__":
    try:
        install_pkgs()

        flask = dynamic_import('flask')
        global Flask, request, jsonify
        Flask = flask.Flask
        request = flask.request
        jsonify = flask.jsonify

        app = Flask(__name__)

        @app.route('/install_pkgs', methods=['POST'])
        def install_pkgs_route():
            result = install_pkgs()
            if "error" in result:
                return jsonify(result), 500
            return jsonify({"status": "success"})

        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        error(f"Failed to start server: {e}")
