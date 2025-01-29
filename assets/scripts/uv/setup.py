# @file setup.py
# @description Script to create and activate the virtual environment using `uv`
# @version 1.0.3
# @license MIT

import subprocess
import os

def _print_greeting_message():
    print()
    print("Hello from 🌌")
    print()

def _print_usage_instructions():
    print("Use 'uv run setup' to reactivate this environment.")
    print()
    print("Example: 'thinking-dataset download'")
    print()
    print("Available commands:")
    print("- download: Download datasets")
    print("- process: Process downloaded data")
    print("- load: Load data into the database")
    print("- generate: Generate synthetic data")
    print("- export: Export processed data")
    print("- upload: Upload data to HuggingFace")
    print("- clean: Clean data directory")
    print("- ls: List files in the dataset directory")
    print()
    print("For more information, visit: https://github.com/MultiTonic/thinking-dataset")
    print()

def main():
    try:
        # Check if virtual environment exists
        if not os.path.exists('.venv'):
            # Create virtual environment using uv
            subprocess.check_call(['uv', 'venv', '.venv'])

        # Install dependencies first
        subprocess.check_call(['uv', 'pip', 'install', '-e', '.[dev]'])

        # Install thinking-dataset as a tool
        subprocess.check_call(['uv', 'tool', 'install', '-e', '.'])

        # Activate virtual environment
        if os.name == 'nt':
            activate_script = '.venv\\Scripts\\activate.bat'
            subprocess.check_call(['cmd.exe', '/c', activate_script])
        else:
            activate_script = '.venv/bin/activate'
            subprocess.check_call(['bash', '-c', f'source {activate_script}'])

        _print_greeting_message()
        _print_usage_instructions()
    except subprocess.CalledProcessError as e:
        print(f"Failed to create or activate virtual environment: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
