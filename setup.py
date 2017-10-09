import sys
from cx_Freeze import setup, Executable

setup(  name = "auto_engoo",
        version = "1.0",
        description = "automatically reserving",
        author = "dizwe",
        executables = [Executable("auto_engoo.py"),Executable("type_info.py")])

