from pathlib import Path

# 01. pathlib - Introduction
# ------------------------------------
# - Object-oriented filesystem paths, a modern alternative to os.path.
# - Path objects support / for joining and many convenient methods.

print("# 01. pathlib - Introduction")
print("# ------------------------------------")

# 02. Creating Path Objects
# ------------------------------------
current = Path(".")
print("\n# 02. Creating Path Objects")
print("current:", current.resolve())

# 03. Joining Paths with / (instead of os.path.join)
# ------------------------------------
sample = Path("folder") / "subfolder" / "file.txt"
print("\n# 03. Joining Paths with /")
print(sample)

# 04. Path Components
# ------------------------------------
print("\n# 04. Path Components")
print("name:", sample.name)
print("stem (name w/o suffix):", sample.stem)
print("suffix:", sample.suffix)
print("parent:", sample.parent)
print("parts:", sample.parts)

# 05. Checking Existence and Type
# ------------------------------------
print("\n# 05. Checking Existence and Type")
print("exists:", current.exists())
print("is_dir:", current.is_dir())
print("is_file:", current.is_file())

# 06. Creating and Removing Directories/Files
# ------------------------------------
demo_dir = Path("temp_pathlib_dir")
demo_dir.mkdir(exist_ok=True)
print("\n# 06. Creating and Removing Directories/Files")
print("created:", demo_dir.exists())

demo_file = demo_dir / "note.txt"
demo_file.write_text("Hello from pathlib!")
print("file content:", demo_file.read_text())

demo_file.unlink()   # delete file
demo_dir.rmdir()     # delete (now empty) directory
print("cleaned up, exists:", demo_dir.exists())

# 07. Iterating Directory Contents
# ------------------------------------
print("\n# 07. Iterating Directory Contents")
for item in list(current.iterdir())[:5]:
    print(item)

# 08. Pattern Matching with glob()
# ------------------------------------
print("\n# 08. Pattern Matching with glob()")
py_files = list(Path("..").glob("**/*.py"))
print(f"found {len(py_files)} .py files (searched recursively)")

# 09. Absolute vs Relative Paths
# ------------------------------------
print("\n# 09. Absolute vs Relative Paths")
print("is_absolute:", sample.is_absolute())
print("absolute form:", sample.resolve())

# 10. pathlib vs os.path (comparison)
# ------------------------------------
print("\n# 10. pathlib vs os.path")
print("# - pathlib: Path('a') / 'b'          (object-oriented, readable)")
print("# - os.path: os.path.join('a', 'b')   (string-based, older style)")

# 11. rglob() vs glob() - Recursive vs Single-Level
# ------------------------------------
# - glob('*.py') only looks in the current directory.
# - glob('**/*.py') needs the explicit '**' to recurse.
# - rglob('*.py') is shorthand for glob('**/*.py') - always recursive.
print("\n# 11. rglob() vs glob()")
top_level_only = list(current.glob("*.py"))
recursive_manual = list(Path("..").glob("**/*.py"))
recursive_rglob = list(Path("..").rglob("*.py"))
print("glob('*.py') in current dir:", len(top_level_only), "files")
print("glob('**/*.py') count:", len(recursive_manual))
print("rglob('*.py') count:   ", len(recursive_rglob), "(same as above)")

# 12. with_suffix() and with_name() - Path Transformation
# ------------------------------------
print("\n# 12. with_suffix() and with_name()")
original = Path("reports/summary.txt")
print("original:", original)
print("with_suffix('.json'):", original.with_suffix(".json"))
print("with_name('final.txt'):", original.with_name("final.txt"))

# 13. Path.stat() - File Metadata
# ------------------------------------
print("\n# 13. Path.stat()")
from datetime import datetime

this_file = Path(__file__)
info = this_file.stat()
print("size (bytes):", info.st_size)
print("last modified:", datetime.fromtimestamp(info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# 14. PurePath vs Path - Comparing Paths Across Platforms
# ------------------------------------
# - PurePath (PurePosixPath/PureWindowsPath) does pure string manipulation,
#   no filesystem access - works even for paths from a different OS.
# - Path (the concrete class used throughout this file) can also touch the
#   real filesystem (exists(), read_text(), etc.) on the current OS.
from pathlib import PurePosixPath, PureWindowsPath

print("\n# 14. PurePath vs Path")
posix_style = PurePosixPath("/home/user/file.txt")
windows_style = PureWindowsPath(r"C:\Users\user\file.txt")
print("posix parts:", posix_style.parts)
print("windows parts:", windows_style.parts)
print("# PurePath never touches disk; Path does and is OS-specific.")

# 15. expanduser() and Path.home()
# ------------------------------------
print("\n# 15. expanduser() and Path.home()")
print("home():", Path.home())
print("expanduser('~/data'):", Path("~/data").expanduser())
