import os
import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None
target_name = "client.exe" if sys.platform == "win32" else "client.bin"

cwd = os.getcwd()

setup(
    executables=[
        Executable(
            os.path.join(cwd, "src", "gbmessclient12345", "client.py"),
            base=base,
            target_name=target_name,
        )
    ]
)
