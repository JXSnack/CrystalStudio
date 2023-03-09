import os
import platform
import subprocess

from crys.crystal import *

version = "1.1.0-SNAPSHOT [public-01]"

def open_file(path: str) -> None:
	if platform.system() == "Windows":
		os.startfile(path)
	elif platform.system() == "Darwin":
		subprocess.Popen(["open", path])
	else:
		subprocess.Popen(["xdg-open", path])


def translate_builder(text: str) -> BuilderType:
	if text.lower().startswith(("htmlplus", "html+")):
		return BuilderType.HTMLPlus
	elif text.lower().startswith("html"):
		return BuilderType.HTML
	elif text.lower().startswith("python"):
		return BuilderType.PYTHON
	else:
		raise ValueError(f"Not translatable: {text}")

def install_requirements() -> None:
	os.system("python3 -m pip install PyQt6")
	os.system("python3 -m pip install requests")
