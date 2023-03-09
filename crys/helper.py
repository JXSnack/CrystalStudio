import os
import platform
import subprocess

from crys.crystal import *

version = "1.1.0-SNAPSHOT [public-08]"

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


def generate_stylesheet(settings: dict) -> str:
	rv = "".join(open("crys/storage/themes/" + settings["theme"][1] + ".theme", "r").readlines()) # rv means return value
	rv+= " QTabBar::tab {font-size: " + str(int(16*settings["text_scale"][1])) + "px;}"
	rv+= " QLabel {font-size: " + str(int(16*settings["text_scale"][1])) + "px;}"
	rv+= " QComboBox {font-size: " + str(int(16*settings["text_scale"][1])) + "px;}"
	rv+= " QComboBox {font-size: " + str(int(16*settings["text_scale"][1])) + "px;}"
	rv+= " QLineEdit {font-size: " + str(int(14*settings["text_scale"][1])) + "px;}"
	rv+= " QPushButton {font-size: " + str(int(16*settings["text_scale"][1])) + "px;}"

	return rv