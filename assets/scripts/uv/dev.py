# @file dev.py
# @description Script to create and activate the virtual environment using `uv`
# @version 1.0.0
# @license MIT

import subprocess
import os

def main():
    try:
        # Check if virtual environment exists
        if not os.path.exists('.venv'):
            # Create virtual environment using uv
            subprocess.check_call(['uv', 'venv', '.venv'])
        
        # Install dependencies including optional dev dependencies
        subprocess.check_call(['uv', 'pip', 'install', '-e', '.[dev]'])
        
        # Activate virtual environment
        if os.name == 'nt':
            activate_script = '.venv\\Scripts\\activate.bat'
            subprocess.check_call(['cmd.exe', '/c', activate_script])
        else:
            activate_script = '.venv/bin/activate'
            subprocess.check_call(['bash', '-c', f'source {activate_script}'])
        
        print("Virtual environment activated.")
        print()
        print("Hello from 🌌")
        print()
    except subprocess.CalledProcessError as e:
        print(f"Failed to create or activate virtual environment: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
