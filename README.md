# thinking-dataset
 creating a thinking dataset

### Reproducibility Guide

1. **Open a terminal** (or command prompt) on your computer.

2. **Navigate to the repository folder**:
   - Use the `cd` command to navigate to your local `thinking-dataset` repository.
     ```bash
     cd /path/to/thinking-dataset
     ```

3. **Create a virtual environment**:
   - Run the following command to create a new virtual environment named `.venv` (or any name you prefer).
     ```bash
     python3 -m venv .venv
     ```

4. **Activate the virtual environment**:
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```

5. **Install the required packages**:
   - With the virtual environment activated, install the project as a package with dependencies by running the following in the project root:
     ```bash
     pip install -e .
     ```

7. **Deactivate the virtual environment** (optional):
   - Once you're done, you can deactivate the virtual environment by running:
     ```bash
     deactivate
     ```
