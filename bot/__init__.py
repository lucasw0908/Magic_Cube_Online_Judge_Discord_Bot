import sys

MIN_PYTHON_VERSION = (3, 8, 0)
if sys.version_info < MIN_PYTHON_VERSION:
    print(f"Your python version is {sys.version}.\nPlease update to python {'.'.join(map(str, MIN_PYTHON_VERSION))} or above.")
    sys.exit(1)

__VERSION__ = "1.0.0"