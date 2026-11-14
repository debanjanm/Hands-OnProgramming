import os
import sys

# 01. os and sys Modules - Introduction
# ------------------------------------
# - os: interact with the operating system (files, directories, env vars).
# - sys: interact with the Python interpreter itself (args, path, exit).

print("# 01. os and sys Modules - Introduction")
print("# ------------------------------------")

# 02. Current Working Directory
# ------------------------------------
print("\n# 02. Current Working Directory")
print("cwd:", os.getcwd())

# 03. Listing Directory Contents
# ------------------------------------
print("\n# 03. Listing Directory Contents")
print(os.listdir("."))

# 04. Creating and Removing Directories
# ------------------------------------
print("\n# 04. Creating and Removing Directories")
os.makedirs("temp_demo_dir", exist_ok=True)
print("created temp_demo_dir, exists:", os.path.exists("temp_demo_dir"))
os.rmdir("temp_demo_dir")
print("removed temp_demo_dir, exists:", os.path.exists("temp_demo_dir"))

# 05. os.path - Path Manipulation
# ------------------------------------
sample_path = os.path.join("folder", "subfolder", "file.txt")
print("\n# 05. os.path")
print("joined path:", sample_path)
print("basename:", os.path.basename(sample_path))
print("dirname:", os.path.dirname(sample_path))
print("splitext:", os.path.splitext(sample_path))
print("absolute path:", os.path.abspath("."))
print("is file '.':", os.path.isfile("."))
print("is dir '.':", os.path.isdir("."))

# 06. Environment Variables
# ------------------------------------
print("\n# 06. Environment Variables")
print("HOME (or None):", os.environ.get("HOME"))
os.environ["MY_CUSTOM_VAR"] = "hello"
print("custom var:", os.environ.get("MY_CUSTOM_VAR"))

# 07. Walking a Directory Tree
# ------------------------------------
print("\n# 07. os.walk()")
count = 0
for root, dirs, files in os.walk("."):
    count += 1
    if count > 2:  # keep demo output short
        break
    print(f"root={root}, dirs={dirs[:3]}, files={files[:3]}")

# 08. sys.argv - Command-Line Arguments
# ------------------------------------
print("\n# 08. sys.argv")
print("script args:", sys.argv)  # sys.argv[0] is the script name itself

# 09. sys.path - Module Search Path
# ------------------------------------
print("\n# 09. sys.path")
print("first entry:", sys.path[0])
print("total entries:", len(sys.path))

# 10. sys.version and sys.platform
# ------------------------------------
print("\n# 10. sys.version and sys.platform")
print("Python version:", sys.version.split()[0])
print("platform:", sys.platform)

# 11. sys.exit() - Exiting a Script (mentioned, not called here)
# ------------------------------------
print("\n# 11. sys.exit()")
print("# - sys.exit(code) stops the script; code 0 means success.")
print("# - Not called here so the rest of the file can still run.")

# 12. os.path vs pathlib - Cross-Reference
# ------------------------------------
print("\n# 12. os.path vs pathlib")
print("# - os.path works with plain strings: os.path.join('a', 'b')")
print("# - pathlib is the modern, object-oriented equivalent: Path('a') / 'b'")
print("# - See 05-Pathlib-Module.py for the full pathlib walkthrough.")

# 13. subprocess.run() - Running Shell Commands Safely
# ------------------------------------
# - Pass the command as a LIST (not a single string with shell=True) so
#   arguments aren't interpreted by a shell - avoids shell-injection risk.
import subprocess

result = subprocess.run(["echo", "hello"], capture_output=True, text=True)
print("\n# 13. subprocess.run()")
print("stdout:", result.stdout.strip())
print("return code:", result.returncode)
print("succeeded:", result.returncode == 0)

# 14. os.getenv() vs os.environ[...] - Default vs KeyError
# ------------------------------------
print("\n# 14. os.getenv() vs os.environ[...]")
print("getenv with default (safe):", os.getenv("DOES_NOT_EXIST", "fallback_value"))
try:
    os.environ["DOES_NOT_EXIST"]  # raises KeyError if the var isn't set
except KeyError as e:
    print("os.environ[...] raised KeyError:", e)

# 15. sys.exit() with Exit Codes (in a subprocess, so this file keeps running)
# ------------------------------------
# - Convention: 0 = success, non-zero = failure. Shells/CI pipelines check
#   this code to decide whether a script "passed".
print("\n# 15. sys.exit() with Exit Codes")
child = subprocess.run(
    [sys.executable, "-c", "import sys; sys.exit(3)"]
)
print("child script exited with code:", child.returncode)

# 16. platform Module - OS Detection
# ------------------------------------
import platform

print("\n# 16. platform Module")
print("system:", platform.system())      # 'Darwin', 'Linux', 'Windows'
print("release:", platform.release())
print("machine:", platform.machine())    # e.g. 'arm64', 'x86_64'
print("python implementation:", platform.python_implementation())
