import os
import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None
target_name = "server.exe" if sys.platform == "win32" else "server.bin"

cwd = os.getcwd()

setup(
    executables=[
        Executable(
            os.path.join(cwd, "src", "gbmessserver12345", "server.py"),
            base=base,
            target_name=target_name,
        )
    ]
)
