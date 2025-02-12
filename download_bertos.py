import os
import subprocess

# Define the target directory (current directory)
BERTOS_DIR = os.path.join(os.getcwd(), "BERTOS")
REPO_URL = "https://github.com/usccolumbia/BERTOS.git"

# Clone or update BERTOS
if os.path.isdir(BERTOS_DIR):
    print("BERTOS directory already exists. Pulling latest changes...")
    subprocess.run(["git", "-C", BERTOS_DIR, "pull"], check=True)
else:
    print("Cloning BERTOS repository...")
    subprocess.run(["git", "clone", REPO_URL, BERTOS_DIR], check=True)

print("BERTOS setup completed!")
