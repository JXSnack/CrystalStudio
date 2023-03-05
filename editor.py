import json
import os
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import crys.crystal
import crys.helper as helper


class Creator(QMainWindow):
	def __init__(self):
		super().__init__()

		self.titles = []
		self.labels = []
		self.buttons = []
		self.lists = []

		self.w = None  # no extra window yet

		self.build_ui()

	def build_ui(self):

		self.setWindowTitle("CrystalStudio - (Main menu)")

		self.label = QLabel("Recent projects feature coming soon!")
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.labels.append(self.label)

		self.setCentralWidget(self.label)

		new_project = QPushButton("New project", self)
		new_project.setStatusTip("Create a new project")
		new_project.clicked.connect(self.new_project_fnc)

		self.buttons.append(new_project)

		open_project = QPushButton("Open Project", self)
		open_project.setStatusTip("Open a project that is saved")
		open_project.clicked.connect(self.open_project_fnc)

		self.buttons.append(open_project)

		self.setStatusBar(QStatusBar(self))

		self.setMinimumSize(960, 540)

		self.fix_css()

	def new_project_fnc(self):
		self.np_dlg = QDialog(self)
		self.np_dlg.setWindowTitle("New project")

		layout = QGridLayout(self.np_dlg)
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

		layout.addWidget(label, 0, 0)
		layout.addWidget(input_name, 0, 1)
		layout.addWidget(label2, 1, 0)
		layout.addWidget(input_authors, 1, 1)
		layout.addWidget(label2_help, 1, 2)
		layout.addWidget(label3, 2, 0)
		layout.addWidget(input_out, 2, 1)
		layout.addWidget(checkbox, 2, 2)
		layout.addWidget(btn, 3, 2)

		self.np_dlg.setLayout(layout)

		self.np_dlg.setFixedSize(480, 270)
		test = QListWidget()

		test.insertItem(0, "Test")
		test.insertItem(1, "Test2")

		test.currentItemChanged.connect(lambda: print("HELLO"))

		layout.addWidget(test, 2, 2)
		self.name_label = QLabel(self)
		self.name_label.setText("Name")

		checkbox.toggled.connect(input_out.setEnabled)

		self.np_dlg.exec()

	def open_project_fnc(self):
		print("Coming soon!")

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
			# print(name, author, out)
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
				"scenes": [{"title": "Scene 1", "buttons": [["Go to scene 2", 2], ["Go to scene 3", 3]]},
						   {"title": "Scene 2", "buttons": [["Go to scene 1", 1], ["Go to scene 3", 3]]},
						   {"title": "Scene 3", "buttons": [["Go to scene 1", 1], ["Go to scene 2", 2]]}
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
		add_button_btn.setStyleSheet('color: white; background-color: rgb(59, 171, 130); font-size: 16px; border: 1px solid rgb(59, 171, 130);')

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
		for i1000 in range(len(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"])):
			try:
				btn = QPushButton(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][0])
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
		del self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][value]
		self.save()
		self.build_preview()
		self.show()

	def change_btn_text(self, button: int, update):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][0] = update
		self.save()

	def change_btn_note(self, button: int, note):
		self.editor_data["scenes"][self.scenes_widget.currentIndex()][button]["notes"] = note
		self.save()

	def change_btn_exec(self, button: int, exec_: int):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][1] = exec_ + 1
		self.save()

	def change_label_text(self, text):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["title"] = text
		self.save()

	def add_scene(self):
		self.mem_data["scenes"].append({"title": "Scene " + str(self.scenes_widget.count() + 1), "buttons": [["Button 1", 1], ["Button 2", 1]]})
		self.editor_data["scenes"].append([{"notes": ""}, {"notes": ""}])
		self.save()

		self.refresh_scenes_widget()
		self.scenes_widget.setCurrentIndex(self.scenes_widget.count()-1)

	def add_button(self):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"].append(["Button", 1])
		self.editor_data["scenes"][self.scenes_widget.currentIndex()].append({"notes": ""})

		self.save()

		self.build_preview()

	def remove_scene(self):
		try:
			if not self.scenes_widget.currentIndex() in [0, self.scenes_widget.count()-1]:
				del self.mem_data["scenes"][self.scenes_widget.currentIndex()]
				del self.editor_data["scenes"][self.scenes_widget.currentIndex()]
				self.save()

				self.refresh_scenes_widget()
				self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 2)
			elif self.scenes_widget.currentIndex() == 0:
				print(f"An error occurred. This is probably why:\n -> You tried to delete scene number 1 (main scene cannot be removed)\n\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

			elif self.scenes_widget.currentIndex() == self.scenes_widget.count()-1:
				del self.mem_data["scenes"][self.scenes_widget.currentIndex()]
				del self.editor_data["scenes"][self.scenes_widget.currentIndex() ]

				self.save()
				self.refresh_scenes_widget()
				self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 1)
			else:
				print(f"An error occurred. This is probably why:\n -> You tried to delete scene number 1 (main scene cannot be removed)\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

		except IndexError as err:
			print(f"An error occurred. \n\nPlease report this issue on Github\nMore info: \"[IndexError] {err} --- tried remove_scene(self)")


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
		self.scenes_widget.setCurrentIndex(self.mem["scenes"][scene_id]["buttons"][btn_id][1])
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

	app.exec()
