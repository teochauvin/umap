import subprocess
import webbrowser
import os
import time

# Directory where your HTML file is located (replace with your path)
directory = "/home/tfsw/@work/D1/umap"

# Start the local server
os.chdir(directory)
server_process = subprocess.Popen(["python3", "-m", "http.server", "8000"])

# Wait for the server to start (a small delay)
time.sleep(2)

# Optionally, you can wait for the server process to finish
server_process.wait()
