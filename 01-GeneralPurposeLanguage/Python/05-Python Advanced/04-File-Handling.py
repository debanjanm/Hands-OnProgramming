import os

# 01. File Handling - Introduction
# ------------------------------------
# - Python reads/writes files via a file object returned by open().
# - Always close files when done - `with` does this automatically.

print("# 01. File Handling - Introduction")
print("# ------------------------------------")

# 02. File Modes (reference)
# ------------------------------------
print("\n# 02. File Modes (reference)")
print("# 'r'  read (default, error if file doesn't exist)")
print("# 'w'  write (creates file, OVERWRITES existing content)")
print("# 'a'  append (creates file if missing, adds to the end)")
print("# 'x'  exclusive create (error if file already exists)")
print("# 'b'  binary mode (e.g. 'rb', 'wb')")
print("# 't'  text mode (default)")
print("# '+'  read and write (e.g. 'r+')")

# 03. Writing to a File with `with` (auto-closes, even on error)
# ------------------------------------
print("\n# 03. Writing to a File")
with open("temp_demo.txt", "w") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")
print("file written, closed automatically:", f.closed)

# 04. Reading an Entire File
# ------------------------------------
print("\n# 04. Reading an Entire File")
with open("temp_demo.txt", "r") as f:
    content = f.read()
print(repr(content))

# 05. Reading Line by Line
# ------------------------------------
print("\n# 05. Reading Line by Line")
with open("temp_demo.txt", "r") as f:
    for line in f:  # memory-efficient - reads one line at a time
        print("line:", line.strip())

# 06. readline() and readlines()
# ------------------------------------
print("\n# 06. readline() and readlines()")
with open("temp_demo.txt", "r") as f:
    first_line = f.readline()
    print("readline():", repr(first_line))

with open("temp_demo.txt", "r") as f:
    all_lines = f.readlines()
    print("readlines():", all_lines)

# 07. Appending to a File
# ------------------------------------
print("\n# 07. Appending to a File")
with open("temp_demo.txt", "a") as f:
    f.write("Line 3 (appended)\n")

with open("temp_demo.txt", "r") as f:
    print(f.read())

# 08. Writing Multiple Lines at Once
# ------------------------------------
print("\n# 08. writelines()")
lines = ["A\n", "B\n", "C\n"]
with open("temp_demo.txt", "w") as f:
    f.writelines(lines)
with open("temp_demo.txt", "r") as f:
    print(f.read())

# 09. seek() and tell() - Moving the File Cursor
# ------------------------------------
print("\n# 09. seek() and tell()")
with open("temp_demo.txt", "r") as f:
    print("cursor position at start:", f.tell())
    f.read(2)
    print("cursor position after reading 2 chars:", f.tell())
    f.seek(0)  # move back to start
    print("after seek(0):", f.tell())

# 10. Binary File Handling
# ------------------------------------
print("\n# 10. Binary File Handling")
with open("temp_demo.bin", "wb") as f:
    f.write(bytes([72, 101, 108, 108, 111]))  # "Hello" as bytes

with open("temp_demo.bin", "rb") as f:
    data = f.read()
print("binary data:", data)
print("decoded:", data.decode())

# 11. Checking Existence Before Opening
# ------------------------------------
print("\n# 11. Checking Existence Before Opening")
if os.path.exists("temp_demo.txt"):
    print("temp_demo.txt exists")

try:
    open("does_not_exist.txt", "r")
except FileNotFoundError:
    print("Caught FileNotFoundError for missing file")

# 12. The encoding= Parameter - Avoiding Platform-Default Bugs
# ------------------------------------
# - Without encoding=, Python uses the OS's default text encoding, which
#   differs across machines (e.g. UTF-8 on Linux/macOS, cp1252 on some
#   Windows setups). A file written on one machine can fail to read
#   correctly on another. ALWAYS pass encoding="utf-8" explicitly for text
#   you care about being portable.
print("\n# 12. encoding= Parameter")
with open("temp_demo.txt", "w", encoding="utf-8") as f:
    f.write("café, naïve, 日本語\n")  # non-ASCII characters
with open("temp_demo.txt", "r", encoding="utf-8") as f:
    print("read back correctly with explicit utf-8:", f.read().strip())

# 13. Buffering Modes - Line-Buffered vs Full, flush()
# ------------------------------------
# - buffering=1 means line-buffered (flushes after each newline, text mode
#   only); buffering=0 is unbuffered (binary mode only); the default is a
#   full buffer sized by the OS, flushed when the buffer fills or the file
#   is closed.
# - flush() forces buffered data to be written NOW, without closing the
#   file - useful for logs you want visible immediately.
print("\n# 13. Buffering Modes and flush()")
with open("temp_demo.txt", "w", buffering=1, encoding="utf-8") as f:
    f.write("line-buffered write\n")
    print("data is likely on disk already (line-buffered flushes on \\n)")

with open("temp_demo.txt", "a", encoding="utf-8") as f:
    f.write("more data")
    f.flush()  # force it out without closing
    print("explicitly flushed before the `with` block even exits")

# 14. Memory-Efficient Large File Processing
# ------------------------------------
# - Reading line-by-line (`for line in f`) is memory-efficient for TEXT
#   files with natural line breaks.
# - For files without lines (binary, huge single-line data), read in fixed
#   size CHUNKS with f.read(size) instead of f.read() (loads everything).
print("\n# 14. Memory-Efficient Large File Processing")
with open("temp_demo.txt", "r", encoding="utf-8") as f:
    line_count = sum(1 for _ in f)  # one line in memory at a time
print("counted lines without loading the whole file:", line_count)

with open("temp_demo.bin", "wb") as f:
    f.write(bytes(range(256)) * 100)  # 25,600 bytes

chunk_size = 1024
bytes_seen = 0
with open("temp_demo.bin", "rb") as f:
    while chunk := f.read(chunk_size):  # read fixed-size chunks until empty
        bytes_seen += len(chunk)
print("counted bytes via chunked reads:", bytes_seen)

# 15. tempfile Module - Scratch Files
# ------------------------------------
# - tempfile creates files/directories in the OS temp location, with unique
#   names, cleaned up automatically when used as a context manager.
import tempfile

print("\n# 15. tempfile Module")
with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=True) as tmp:
    tmp.write("scratch data")
    tmp.seek(0)
    print("wrote to and read from a temp file:", tmp.read())
    print("temp file path:", tmp.name)
print("temp file auto-deleted on exit from `with` block")

# 16. shutil Module - Copy/Move Files (brief)
# ------------------------------------
# - shutil.copy() copies a file's content + permissions; shutil.move()
#   relocates (or renames) a file or directory.
import shutil

print("\n# 16. shutil for Copy/Move")
shutil.copy("temp_demo.txt", "temp_demo_copy.txt")
print("copied file exists:", os.path.exists("temp_demo_copy.txt"))
shutil.move("temp_demo_copy.txt", "temp_demo_moved.txt")
print("after move - old name exists:", os.path.exists("temp_demo_copy.txt"))
print("after move - new name exists:", os.path.exists("temp_demo_moved.txt"))

# 17. CSV / Large-File Streaming (cross-reference)
# ------------------------------------
# - For structured data like CSV, don't hand-parse lines - the csv module
#   handles quoting/escaping correctly, and can stream row-by-row just like
#   the chunked reading above. Full depth (csv + json) lives in the
#   Standard Library file - not duplicated here.
print("\n# 17. CSV / Large-File Streaming (see Standard Library file for csv/json depth)")
print("# - csv.reader(f) / csv.DictReader(f) stream rows lazily, same idea as `for line in f`")

# 18. Cleanup
# ------------------------------------
os.remove("temp_demo.txt")
os.remove("temp_demo.bin")
os.remove("temp_demo_moved.txt")
print("\n# 18. Cleanup")
print("temp files removed")
