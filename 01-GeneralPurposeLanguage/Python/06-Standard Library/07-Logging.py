import logging

# 01. Logging - Introduction
# ------------------------------------
# - print() is fine for quick checks; logging is the real tool for apps -
#   severity levels, timestamps, output to file/console, filterable.

print("# 01. Logging - Introduction")
print("# ------------------------------------")

# 02. Basic Configuration and Logging Levels
# ------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

print("\n# 02. Basic Configuration and Logging Levels")
logging.debug("Debug message - detailed diagnostic info")
logging.info("Info message - confirms things work as expected")
logging.warning("Warning message - something unexpected happened")
logging.error("Error message - a real problem occurred")
logging.critical("Critical message - program may be unable to continue")

# 03. Level Order (lowest to highest severity)
# ------------------------------------
print("\n# 03. Level Order (reference)")
print("# DEBUG < INFO < WARNING < ERROR < CRITICAL")
print("# - basicConfig(level=X) shows X and everything MORE severe than X.")

# 04. Named Loggers (per-module, the recommended pattern)
# ------------------------------------
logger = logging.getLogger(__name__)  # __name__ = module's own name

print("\n# 04. Named Loggers")
logger.info("Message from a named logger: %s", __name__)

# 05. Logging Exceptions with Traceback
# ------------------------------------
print("\n# 05. Logging Exceptions with Traceback")
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Caught an exception")  # includes full traceback

# 06. Logging to a File
# ------------------------------------
print("\n# 06. Logging to a File")
file_logger = logging.getLogger("file_demo")
file_handler = logging.FileHandler("temp_app.log")
file_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
file_logger.addHandler(file_handler)
file_logger.setLevel(logging.INFO)
file_logger.propagate = False  # don't also print via the root logger's console handler

file_logger.info("This line goes to temp_app.log")

with open("temp_app.log") as f:
    print("file content:", f.read().strip())

# 07. Cleanup
# ------------------------------------
import os
file_handler.close()
os.remove("temp_app.log")
print("\n# 07. Cleanup")
print("temp_app.log removed")

# 08. print() vs logging - When to Use Which
# ------------------------------------
print("\n# 08. print() vs logging")
print("# - print(): quick one-off debugging, CLI tool output for the user")
print("# - logging: real applications - severity, timestamps, can be turned")
print("#   off/on per module without editing code, goes to files/services")

# 09. Logger Hierarchy and Propagation
# ------------------------------------
# - Loggers form a tree based on dotted names: "app" is the parent of
#   "app.module", which is the parent of "app.module.sub".
# - A message logged on a child propagates UP to every ancestor's handlers
#   (unless propagate=False, as used for file_logger above).
print("\n# 09. Logger Hierarchy and Propagation")
parent_logger = logging.getLogger("app")
child_logger = logging.getLogger("app.module")
print("child's parent:", child_logger.parent.name)
print("child propagates to parent:", child_logger.propagate)
child_logger.warning("this bubbles up through 'app' to the root logger's handlers")

# 10. getLogger(__name__) - Why It Matters at Scale
# ------------------------------------
# - __name__ is the dotted module path (e.g. "myapp.utils.parser"), so
#   every module's logger automatically slots into the right place in the
#   hierarchy. You can then silence or redirect one subsystem
#   (logging.getLogger("myapp.utils").setLevel(logging.WARNING)) without
#   touching every print statement or a single global logger's config.
print("\n# 10. getLogger(__name__) at Scale")
print("# - one shared/root logger: can't tell which module logged what,")
print("#   can't tune verbosity per-subsystem.")
print("# - getLogger(__name__) per module: log records carry their origin,")
print("#   and each subsystem's level/handlers can be tuned independently.")

# 11. RotatingFileHandler - Log Rotation by Size
# ------------------------------------
from logging.handlers import RotatingFileHandler

print("\n# 11. RotatingFileHandler")
rotating_logger = logging.getLogger("rotating_demo")
rotating_logger.propagate = False
rotating_handler = RotatingFileHandler(
    "temp_rotating.log", maxBytes=200, backupCount=2
)
rotating_logger.addHandler(rotating_handler)
rotating_logger.setLevel(logging.INFO)
for i in range(20):
    rotating_logger.info(f"log line number {i} - padded to trigger rotation soon")

import glob
rotating_handler.close()
rotated_files = sorted(glob.glob("temp_rotating.log*"))
print("files created by rotation:", rotated_files)
for f in rotated_files:
    os.remove(f)

# 12. logging.config.dictConfig - Structured Configuration
# ------------------------------------
# - basicConfig() is fine for one quick setup; dictConfig() lets you define
#   multiple loggers/handlers/formatters declaratively (e.g. loaded from a
#   YAML/JSON config file) instead of imperative setup calls.
import logging.config

dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "dictconfig_demo": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
logging.config.dictConfig(dict_config)
print("\n# 12. logging.config.dictConfig")
logging.getLogger("dictconfig_demo").info("configured entirely via a dict")

# 13. extra= - Adding Contextual Info to Log Records
# ------------------------------------
print("\n# 13. extra= for Contextual Info")
context_logger = logging.getLogger("context_demo")
context_logger.propagate = False
context_handler = logging.StreamHandler()
context_handler.setFormatter(logging.Formatter("%(levelname)s - user=%(user_id)s - %(message)s"))
context_logger.addHandler(context_handler)
context_logger.setLevel(logging.INFO)
context_logger.info("processing request", extra={"user_id": 42})
