import json
import os
import sys

import crys.crystal
import crys.helper as helper

try:
	from PyQt6.QtCore import *
	from PyQt6.QtGui import *
	from PyQt6.QtWidgets import *

	import requests
except ImportError:
	helper.install_requirements()
	print("\nPlease start the editor again!")
	sys.exit(0)


class Creator(QMainWindow):
	def __init__(self):
		super().__init__()

		self.adjusted = []
		self.pointed = []

		self.w = None  # no extra window yet

		self.build_ui()

	def build_ui(self):

		self.setWindowTitle("CrystalStudio - (Main menu)")

		self.label = QLabel("Recent projects feature coming soon!")
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.setCentralWidget(self.label)

		self.pic = QLabel(self)
		self.pic.setPixmap(QPixmap("crys/storage/icon.png"))
		self.pic.setScaledContents(True)
		self.pic.setGeometry(10, 0, int(128 / 2), int(128 / 2))

		self.anl = QLabel(self)  # anl means app_name_label
		self.anl.move(76, 6)
		self.anl.setText("CrystalStudio")
		self.anl.setStyleSheet("color: white; font-size: 14px; background-color: none;")

		self.avl = QLabel(self)  # avl means app_version_label
		self.avl.setText(helper.version)
		self.avl.adjustSize()
		self.avl.move(76, 31)
		self.avl.setStyleSheet("color: gray; font-size: 12px; background-color: none;")

		new_project = QPushButton("New project", self)
		new_project.clicked.connect(self.new_project_fnc)
		new_project.setToolTip("Create a new project")
		new_project.move(25, 80)

		self.pointed.append(new_project)
		self.adjusted.append(new_project)

		open_project = QPushButton("Open Project", self)
		open_project.setToolTip("Open a saved project")
		open_project.clicked.connect(self.open_project_fnc)
		open_project.move(25, 115)
		self.pointed.append(open_project)
		self.adjusted.append(open_project)

		setting_btn = QPushButton("Settings", self)
		setting_btn.setToolTip("Open settings")
		setting_btn.clicked.connect(lambda: self.open_settings())
		setting_btn.move(25, 150)
		self.pointed.append(setting_btn)
		self.adjusted.append(setting_btn)

		self.setStatusBar(QStatusBar(self))

		self.setFixedSize(960, 540)

		self.fix_css()

	def open_settings(self):
		if self.w is None:
			self.w = SettingsWindow()
		self.w.show()
		self.hide()

	def new_project_fnc(self):
		self.np_dlg = QDialog(self)
		self.np_dlg.setWindowTitle("New project")

		layout = QVBoxLayout(self.np_dlg)
		layout2 = QHBoxLayout(self.np_dlg)
		layout3 = QHBoxLayout(self.np_dlg)
		layout4 = QHBoxLayout(self.np_dlg)
		layout5 = QHBoxLayout(self.np_dlg)
		label = QLabel(self.np_dlg)
		label.setText("Project name:")
		input_name = QLineEdit(self.np_dlg)

		label2 = QLabel(self.np_dlg)
		label2.setText("Authors:")
		input_authors = QLineEdit(self.np_dlg)
		label2_help = QLabel(self.np_dlg)
		label2_help.setText("(seperate by comma)")

		label3 = QLabel(self.np_dlg)
		label3.setText("Out folder:")
		input_out = QLineEdit(self.np_dlg)
		input_out.setText("out/")
		input_out.setDisabled(True)
		checkbox = QCheckBox(self.np_dlg)

		btn = QPushButton(self.np_dlg)
		btn.setText("Create project")
		btn.clicked.connect(lambda: self.create_project(input_name.text(), input_authors.text(), input_out.text()))

		layout2.addWidget(label)
		layout2.addWidget(input_name)
		layout3.addWidget(label2)
		layout3.addWidget(input_authors)
		layout3.addWidget(label2_help)
		layout4.addWidget(label3)
		layout4.addWidget(input_out)
		layout4.addWidget(checkbox)
		layout5.addWidget(btn)
		layout.addLayout(layout2)
		layout.addLayout(layout3)
		layout.addLayout(layout4)
		layout.addLayout(layout5)

		self.pointed.append(btn)

		self.np_dlg.setLayout(layout)

		self.np_dlg.setFixedSize(480, 270)

		checkbox.toggled.connect(input_out.setEnabled)
		self.fix_css()

		self.np_dlg.exec()

	def open_project_fnc(self):
		file = str(QFileDialog.getExistingDirectory(self, "Select project directory"))
		try:
			mem_file = open(file + "/save.json", "r")
			mem = json.load(mem_file)
			self.hide()
			Editor(mem["info"]["name"], ", ".join(mem["info"]["authors"]), mem["info"]["out"]).show()
		except FileNotFoundError:
			print("INVALID DIRECTORY. PLEASE PICK A VALID PROJECT")

	def create_project(self, name, author, out):
		if name:
			if author:
				if out:
					allow = True
				else:
					allow = False
			else:
				allow = False
		else:
			allow = False

		if allow:
			self.np_dlg.hide()
			self.hide()

		try:
			os.mkdir("editor/" + name)
			os.mkdir("editor/" + name + "/" + out)

			if self.w is None:
				self.w = Editor(name, author, out)
			self.w.show()

			self.hide()

		except FileExistsError as err:
			print("ERROR:", err, "| Please pick a different name.")
			sys.exit(1)

	def fix_css(self):
		for i in self.pointed:
			try:
				i.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
				i.adjustSize()
			except RuntimeError:
				continue

		for i in self.adjusted:
			try:
				i.adjustSize()
			except RuntimeError:
				continue

		self.setStyleSheet("""
		QWidget { background-color: rgb(37, 37, 37); } 
		QCheckBox::indicator:unchecked {background-color: rgba(255, 90, 90, 0.5); border-radius: 3px;} 
		QCheckBox::indicator::checked {background-color: rgba(90, 255, 90, 0.5); border-radius: 3px;}
		QLineEdit:disabled {color: gray; font-size: 14px; border: 1px solid gray;}
		QLineEdit:enabled {color: white; font-size: 14px; border: 1px solid white;}
		QPushButton {color: white; background-color: rgb(51, 51, 51); font-size: 16px; border: 3px solid rgb(51, 51, 51);}
		QLabel {color: white; font-size: 16px;}
		
""")


class Editor(QWidget):
	def __init__(self, name: str = None, author: str = None, out: str = None):
		super().__init__()

		self.name = name
		self.author = author
		self.out = out

		self.preview = []

		try:
			file = open(f"editor/{name}/save.json", "r")
			self.mem_data = json.load(file)
			file.close()
		except FileNotFoundError:
			file = open(f"editor/{name}/save.json", "w")

			self.mem_data = {
				"info": {"name": name, "authors": author.split(", "), "out": "out/"},
				"scenes": [{"title": "Scene 1", "pointed": [["Go to scene 2", 2], ["Go to scene 3", 3]]},
						   {"title": "Scene 2", "pointed": [["Go to scene 1", 1], ["Go to scene 3", 3]]},
						   {"title": "Scene 3", "pointed": [["Go to scene 1", 1], ["Go to scene 2", 2]]}
						   ]
			}

			json.dump(self.mem_data, file)
			file.close()

		try:
			file = open(f"editor/{name}/editor.json", "r")
			self.editor_data = json.load(file)
			file.close()
		except FileNotFoundError:
			file = open(f"editor/{name}/editor.json", "w")

			self.editor_data = {"current_scene": 0,
								"scenes": [[{"notes": ""}, {"notes": ""}, {"notes": ""}],
										   [{"notes": ""}, {"notes": ""}, {"notes": ""}],
										   [{"notes": ""}, {"notes": ""}, {"notes": ""}]]
								}

			json.dump(self.editor_data, file)
			file.close()

		self.save_file = open(f"editor/{name}/save.json", "r")
		self.editor_file = open(f"editor/{name}/editor.json", "r")

		self.build_ui()

	def build_ui(self):
		self.layout = QGridLayout(self)
		self.layout.setContentsMargins(200, 200, 200, 200)

		self.setLayout(self.layout)

		self.setFixedSize(1920, 1080)
		self.setWindowTitle("CrystalStudio - " + self.name)

		self.labels = []
		self.lists = []
		self.buttons = []
		self.titles = []

		add_scene_btn = QPushButton(self)
		add_scene_btn.setText("+")
		add_scene_btn.clicked.connect(lambda: self.add_scene())
		add_scene_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		add_button_btn = QPushButton(self)
		add_button_btn.setText("+ Button")
		add_button_btn.clicked.connect(lambda: self.add_button())
		add_button_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		remove_scene_btn = QPushButton(self)
		remove_scene_btn.setText("-")
		remove_scene_btn.clicked.connect(lambda: self.remove_scene())
		remove_scene_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		build_btn = QPushButton(self)
		build_btn.setText("Build game")
		build_btn.clicked.connect(lambda: BuildMenu(self, self.mem_data, self.editor_data).show())

		self.save_btn = QPushButton(self)
		self.save_btn.setText("Save")

		name = QLabel(self)
		name.setText("Editing " + self.name + " (" + self.out + ")")
		authors = QLabel(self)
		authors.setText("Made by " + self.author)

		self.scenes_widget = QComboBox(self)
		self.refresh_scenes_widget()

		self.scenes_widget.currentIndexChanged.connect(lambda: self.build_preview())

		self.scenes_widget.setCurrentIndex(self.editor_data["current_scene"])

		self.lists.append(self.scenes_widget)

		self.labels.append(name)
		self.labels.append(authors)

		self.buttons.append(build_btn)
		self.buttons.append(self.save_btn)

		name.move(10, 5)
		authors.move(10, 29)
		self.scenes_widget.move(1780, 10)
		self.scenes_widget.setFixedSize(130, 40)
		add_scene_btn.move(1877, 60)
		add_scene_btn.setStyleSheet(
			'color: white; background-color: rgb(59, 171, 130); font-size: 16px; border: 1px solid rgb(59, 171, 130);')
		add_scene_btn.setFixedSize(32, 32)

		add_button_btn.move(1780, 100)
		add_button_btn.setFixedSize(130, 40)
		add_button_btn.setStyleSheet(
			'color: white; background-color: rgb(59, 171, 130); font-size: 16px; border: 1px solid rgb(59, 171, 130);')

		remove_scene_btn.move(1780, 60)
		remove_scene_btn.setStyleSheet(
			'color: white; background-color: rgb(179, 0, 0); font-size: 16px; border: 1px solid rgb(179, 0, 0);')
		remove_scene_btn.setFixedSize(32, 32)

		self.save_btn.move(1740, 1020)
		self.save_btn.setFixedSize(60, 40)
		build_btn.move(1810, 1020)
		build_btn.setFixedSize(100, 40)

		self.save_btn.clicked.connect(lambda: self.save())

		self.fix_css()
		self.build_preview()

	def build_preview(self):
		# print(self.preview)
		for prev in self.preview:
			try:
				prev.deleteLater()
			except:
				continue

		self.preview = []
		# print(self.preview)
		lab = QLabel(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["title"])
		self.preview.append(lab)
		self.layout.addWidget(lab, 0, 0)
		self.titles.append(lab)
		throw_away = 0
		num = 0
		for i1000 in range(len(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"])):
			try:
				btn = QPushButton(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"][i1000][0])
				btn.clicked.connect(
					lambda throw_away, btn=btn, num=num: self.btn_editor(btn, self.scenes_widget.currentIndex(), num))
				self.preview.append(btn)
				self.layout.addWidget(btn)
				self.buttons.append(btn)
				num += 1
			except IndexError:
				continue

		lab.mousePressEvent = lambda throw_away, scene_id=self.scenes_widget.currentIndex(), lab=lab: self.txt_editor(
			lab, scene_id)

		self.fix_css()
		self.save()

	def fix_css(self):
		self.setStyleSheet('background-color: rgb(37, 37, 37);')
		for i in self.titles:
			try:
				i.setStyleSheet('color: white; font-size: 36px;')
				i.adjustSize()
			except RuntimeError:
				continue

		for i in self.labels:
			try:
				i.setStyleSheet('color: white; font-size: 16px;')
				i.adjustSize()
			except RuntimeError:
				continue

		for i in self.lists:
			try:
				i.setStyleSheet('color: white; background-color: gray; font-size: 18px; border: 0px solid gray;')
				i.adjustSize()
			except RuntimeError:
				continue

		for i in self.buttons:
			try:
				i.setStyleSheet('color: white; background-color: gray; font-size: 16px; border: 1px solid gray;')
				i.adjustSize()
				i.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
			except RuntimeError:
				continue

	def btn_editor(self, btn, scene_id, btn_id):
		self.hide()

		dlg = ButtonEditor(self, btn, scene_id, self.mem_data, btn_id, self.editor_data)
		dlg.exec()

	def txt_editor(self, label, scene_id):
		self.hide()

		dlg = TextEditor(self, label, scene_id, self.mem_data, self.editor_data)
		dlg.exec()

	def save(self):
		self.save_btn.setVisible(False)

		self.editor_data["current_scene"] = self.scenes_widget.currentIndex()

		file = open(f"editor/{self.name}/save.json", "w")
		json.dump(self.mem_data, file)
		file.close()

		file = open(f"editor/{self.name}/editor.json", "w")
		json.dump(self.editor_data, file)
		file.close()

		self.save_btn.setVisible(True)

	def refresh_scenes_widget(self):
		last_scene = self.scenes_widget.currentIndex()
		self.scenes_widget.clear()
		for i in range(len(self.mem_data["scenes"])):
			self.scenes_widget.insertItem(i, f"Scene {i + 1}")
			self.scenes_widget.setCurrentIndex(last_scene)

	def remove_btn(self, value):
		del self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"][value]
		self.save()
		self.build_preview()
		self.show()

	def change_btn_text(self, button: int, update):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"][button][0] = update
		self.save()

	def change_btn_note(self, button: int, note):
		self.editor_data["scenes"][self.scenes_widget.currentIndex()][button]["notes"] = note
		self.save()

	def change_btn_exec(self, button: int, exec_: int):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"][button][1] = exec_ + 1
		self.save()

	def change_label_text(self, text):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["title"] = text
		self.save()

	def add_scene(self):
		self.mem_data["scenes"].append(
			{"title": "Scene " + str(self.scenes_widget.count() + 1), "pointed": [["Button 1", 1], ["Button 2", 1]]})
		self.editor_data["scenes"].append([{"notes": ""}, {"notes": ""}])
		self.save()

		self.refresh_scenes_widget()
		self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 1)

	def add_button(self):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["pointed"].append(["Button", 1])
		self.editor_data["scenes"][self.scenes_widget.currentIndex()].append({"notes": ""})

		self.save()

		self.build_preview()

	def remove_scene(self):
		try:
			if not self.scenes_widget.currentIndex() in [0, self.scenes_widget.count() - 1]:
				del self.mem_data["scenes"][self.scenes_widget.currentIndex()]
				del self.editor_data["scenes"][self.scenes_widget.currentIndex()]
				self.save()

				self.refresh_scenes_widget()
				self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 2)
			elif self.scenes_widget.currentIndex() == 0:
				print(
					f"An error occurred. This is probably why:\n -> You tried to delete scene number 1 (main scene cannot be removed)\n\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

			elif self.scenes_widget.currentIndex() == self.scenes_widget.count() - 1:
				del self.mem_data["scenes"][self.scenes_widget.currentIndex()]
				del self.editor_data["scenes"][self.scenes_widget.currentIndex()]

				self.save()
				self.refresh_scenes_widget()
				self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 1)
			else:
				print(
					f"An error occurred. This is probably why:\n -> You tried to delete scene number 1 (main scene cannot be removed)\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

		except IndexError as err:
			print(
				f"An error occurred. \n\nPlease report this issue on Github\nMore info: \"[IndexError] {err} --- tried remove_scene(self)")


class SettingsWindow(QTabWidget):
	def __init__(self, parent=None):
		super(SettingsWindow, self).__init__(parent)
		self.settings_filepath = "crys/storage/settings.json"
		settings_file = open(self.settings_filepath, "r")
		self.settings = json.load(settings_file)

		self.setFixedSize(540, 640)

		self.build_ui()

	def build_ui(self):
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.tab3 = QWidget()

		self.addTab(self.tab1, "General settings")
		self.addTab(self.tab2, "Color and themes")
		self.addTab(self.tab3, "Save")

		self.build_tab1UI()
		self.build_tab2UI()
		self.build_tab3UI()

		self.save_btn.move(100, 100)

		self.fix_css()

		self.setWindowTitle("Settings")

	def build_tab1UI(self):
		layout1 = QHBoxLayout()
		layout2 = QHBoxLayout()
		layout = QVBoxLayout()
		layout.addLayout(layout1)
		layout.addLayout(layout2)
		label1 = QLabel("UI scale: ")
		selector1 = QComboBox(self)
		selector1.insertItem(0, "0.5 (Large)")
		selector1.insertItem(1, "1 (Default)")
		selector1.insertItem(2, "1.5 (Small)")
		selector1.insertItem(3, "2 (Mini)")
		selector1.setCurrentIndex(1)

		label2 = QLabel("Text scale: ")
		selector2 = QComboBox(self)
		selector2.insertItem(0, "0.5 (Large)")
		selector2.insertItem(1, "1 (Default)")
		selector2.insertItem(2, "1.5 (Small)")
		selector2.insertItem(3, "2 (Mini)")
		selector2.setCurrentIndex(1)

		layout1.addWidget(label1)
		layout1.addWidget(selector1)

		layout2.addWidget(label2)
		layout2.addWidget(selector2)

		self.setTabText(0, "General settings")
		self.tab1.setLayout(layout)

	def build_tab2UI(self):
		layout = QHBoxLayout()
		label1 = QLabel("Theme: ")
		selector1 = QComboBox(self)
		selector1.insertItem(0, "Midnight")
		selector1.insertItem(1, "Dark (Default)")
		selector1.insertItem(2, "Light")
		selector1.insertItem(3, "Eyeburn")
		selector1.setCurrentIndex(1)

		layout.addWidget(label1)
		layout.addWidget(selector1)

		self.setTabText(1, "Color and themes")
		self.tab2.setLayout(layout)

	def build_tab3UI(self):
		layout = QHBoxLayout()

		self.save_btn = QPushButton("Apply and save")
		self.save_btn.clicked.connect(lambda: self.save())
		self.exit_btn = QPushButton("Apply, save and exit")
		self.exit_btn.clicked.connect(lambda: self.exit())
		layout.addWidget(self.save_btn)
		layout.addWidget(self.exit_btn)

		self.setTabText(2, "Save")
		self.tab3.setLayout(layout)

	def save(self):
		settings_file = open(self.settings_filepath, "w")
		json.dump(self.settings, settings_file)

	def exit(self):
		self.save()
		Creator().show()
		self.hide()

	def fix_css(self):
		self.setStyleSheet("".join(open("crys/storage/themes/" + self.settings["theme"] + ".theme", "r").readlines()))


class ButtonEditor(QDialog):
	def __init__(self, parent, btn: QPushButton, scene_id, memory, btn_id, editor):
		super().__init__(parent)

		labels = []
		lines = []
		buttons = []

		self.editor = editor
		self.mem = memory
		self.scene_id = scene_id
		self.btn_id = btn_id
		self.btn = btn

		self.setWindowTitle(f"Editing button {self.btn_id} in scene {self.scene_id}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()
		self.layout3 = QVBoxLayout()
		self.layout4 = QHBoxLayout()
		message1 = QLabel("Button text:")
		labels.append(message1)
		self.btn_text = QLineEdit()
		self.btn_text.setText(self.btn.text())
		lines.append(self.btn_text)

		message2 = QLabel("Button action:")
		labels.append(message2)
		self.scenes_widget = QComboBox(self)
		for i in range(len(memory["scenes"])):
			self.scenes_widget.insertItem(i, f"Go to {i + 1}")
		self.scenes_widget.setCurrentIndex(self.mem["scenes"][scene_id]["pointed"][btn_id][1])
		lines.append(self.scenes_widget)

		message3 = QLabel("Notes:")
		labels.append(message3)
		self.notes = QTextEdit()
		self.notes.setText(editor["scenes"][self.scene_id][self.btn_id]["notes"])
		lines.append(self.notes)

		remove_btn = QPushButton("Remove")
		remove_btn.clicked.connect(lambda: self.remove_btn_clicked())
		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())
		save = QPushButton("Save")
		save.clicked.connect(lambda: self.save_btn_clicked())
		buttons.append(remove_btn)
		buttons.append(cancel)
		buttons.append(save)

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.btn_text)
		self.layout2.addWidget(message2)
		self.layout2.addWidget(self.scenes_widget)
		self.layout3.addWidget(message3)
		self.layout3.addWidget(self.notes)
		self.layout4.addWidget(remove_btn)
		self.layout4.addWidget(cancel)
		self.layout4.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)
		self.layout.addLayout(self.layout4)

		self.setLayout(self.layout)

		self.setFixedSize(800, 300)

		for label in labels:
			label.setStyleSheet("color: white; font-size: 16px;")
			label.adjustSize()

		for line in lines:
			line.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			line.adjustSize()

		for button in buttons:
			button.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			button.adjustSize()

	def remove_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]), self.mem["info"]["out"]).remove_btn(
			self.btn_id)
		self.hide()

	def save_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_btn_exec(self.btn_id, self.scenes_widget.currentIndex())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_btn_note(self.btn_id, self.notes.toPlainText())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_btn_text(self.btn_id, self.btn_text.text())
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()

	def cancel(self):
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()


class TextEditor(QDialog):
	def __init__(self, parent, label: QLabel, scene_id, memory, editor):
		super().__init__(parent)

		labels = []
		lines = []
		buttons = []

		self.editor = editor
		self.mem = memory
		self.scene_id = scene_id
		self.label = label

		self.setWindowTitle(f"Editing text in scene {self.scene_id}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()
		self.layout3 = QVBoxLayout()
		self.layout4 = QHBoxLayout()
		message1 = QLabel("Text:")
		labels.append(message1)
		self.text = QTextEdit()
		self.text.setText(self.label.text())
		lines.append(self.text)

		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())
		save = QPushButton("Save")
		save.clicked.connect(lambda: self.save_btn_clicked())
		buttons.append(cancel)
		buttons.append(save)

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.text)
		self.layout4.addWidget(cancel)
		self.layout4.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)
		self.layout.addLayout(self.layout4)

		self.setLayout(self.layout)

		self.setFixedSize(800, 300)

		for label in labels:
			label.setStyleSheet("color: white; font-size: 16px;")
			label.adjustSize()

		for line in lines:
			line.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			line.adjustSize()

		for button in buttons:
			button.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			button.adjustSize()

	def save_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_label_text(self.text.toPlainText())
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()

	def cancel(self):
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()


class BuildMenu(QDialog):
	def __init__(self, parent, memory, editor):
		super().__init__(parent)

		self.labels = []
		self.lines = []
		self.buttons = []

		self.editor = editor
		self.mem = memory

		self.setWindowTitle(f"Build {self.mem['info']['name']}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()

		message1 = QLabel("Builder type:")
		self.labels.append(message1)
		self.builder_type = QComboBox()
		self.builder_type.insertItem(0, "HTML+ (JavaScript, HTML, CSS)")
		self.builder_type.insertItem(1, "HTML (HTML, CSS)")
		self.builder_type.insertItem(2, "Python (Terminal game)")
		self.lines.append(self.builder_type)

		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())
		save = QPushButton("Build")
		save.clicked.connect(lambda: self.build_btn_clicked())
		self.buttons.append(cancel)
		self.buttons.append(save)

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.builder_type)
		self.layout2.addWidget(cancel)
		self.layout2.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)

		self.setLayout(self.layout)

		self.setFixedSize(800, 300)

		for label in self.labels:
			label.setStyleSheet("color: white; font-size: 16px;")
			label.adjustSize()

		for line in self.lines:
			line.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			line.adjustSize()

		for button in self.buttons:
			button.setStyleSheet("color: white; font-size: 12px; border: 1px solid white;")
			button.adjustSize()

	def build_btn_clicked(self):
		try:
			crys.crystal.Game(self.mem, helper.translate_builder(self.builder_type.currentText()), True).build()
			helper.open_file(f"editor/{self.mem['info']['name']}/{self.mem['info']['out']}")
			self.hide()
			Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
				   self.mem["info"]["out"]).show()

		except FileExistsError:
			print("ERROR: already exported this once. Delete the old folder and build again!")
			helper.open_file(f"editor/{self.mem['info']['name']}/{self.mem['info']['out']}")

	def cancel(self):
		self.hide()


# Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
# 	   self.mem["info"]["out"]).show()


if __name__ == "__main__":
	app = QApplication(sys.argv)

	# window = BuildMenu(Editor("test", "JX_Snack", "out/"), Editor("test", "JX_Snack", "out/").mem_data,
	# 				   Editor("test", "JX_Snack", "out/").editor_data)
	# window = Editor("test", "JX_Snack", "out/")
	window = Creator()
	window.show()

	app.setWindowIcon(QIcon('crys/storage/icon.png'))

	app.exec()
