# @file assets/scripts/setup.py
# @description Script to create virtual environment and install project dependencies using `uv`
# @version 1.0.1
# @license MIT

import subprocess
import os

def main():
    try:
        # Check if virtual environment exists
        if not os.path.exists('.venv'):
            # Create virtual environment using uv
            subprocess.check_call(['uv', 'venv', '.venv'])
        
        # Install dependencies
        subprocess.check_call(['uv', 'pip', 'install', '-e', '.'])
        
        print("Hello from 🌌")
        
        # Import modules after installing dependencies
        from thinking_dataset.io.files import Files

    except subprocess.CalledProcessError as e:
        print(f"Failed to create or activate virtual environment: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
