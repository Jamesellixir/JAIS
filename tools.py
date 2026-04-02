import os
import subprocess

def create_file(filepath: str, content: str) -> str:
    """
    Creates a file at the specified path with the given content.
    """
    try:
        # Ensure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file at {filepath}"
    except Exception as e:
        return f"Error creating file {filepath}: {str(e)}"

def run_local_command(command: str) -> str:
    """
    Runs a shell command locally and returns the output.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return f"Command executed successfully. Output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}. Error output:\n{e.stderr}"

AVAILABLE_TOOLS = {
    "create_file": {
        "function": create_file,
        "description": "Create a file at a given path with specified string content."
    },
    "run_local_command": {
        "function": run_local_command,
        "description": "Run a shell command on the host Windows machine."
    }
}
