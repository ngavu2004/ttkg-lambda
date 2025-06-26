import os
import subprocess
import sys
import shutil

# Create layer directory structure
os.makedirs("layer/python", exist_ok=True)

# Install packages using pip with constraints
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "--only-binary=:all:",
    "-r", "layer-requirements.txt",
    "-c", "constraints.txt",  # Add constraints file
    "-t", "layer/python"
])

print("Layer successfully created!")