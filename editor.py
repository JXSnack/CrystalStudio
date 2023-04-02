import json
import os
import re
import shutil
import io
import sys
import time
import zipfile

try:
	from PyQt6.QtCore import *
	from PyQt6.QtGui import *
	from PyQt6.QtWidgets import *

	from crys import QExtension
	from crys.script import MemCheck
	import crys.crystal

	import requests
except (ImportError, ModuleNotFoundError):
	import crys.helper as helper

	helper.install_requirements()
	print("\nPlease start the editor again! If it said something with the Microsoft store, please do these three commands in the PyCharm command line:\npip install --upgrade pip\npip install PyQt6\npip install requests")
	sys.exit(0)

import crys.crystal
import crys.helper as helper
from crys.script import MemCheck

class Creator(QMainWindow):
	def __init__(self):
		super().__init__()

		self.adjusted = []
		self.pointed = []

		self.settings = helper.get_settings()

		self.w = None  # no extra window yet

		self.build_ui()

	def build_ui(self):

		self.setWindowTitle("CrystalStudio - (Main menu)")

		self.pic = QLabel(self)
		self.pic.setPixmap(QPixmap("crys/storage/icon/" + settings["icon"][1] + ".png"))
		self.pic.setScaledContents(True)
		self.pic.setGeometry(int(10 * self.settings["ui_scale"][1]), int(1 * self.settings["ui_scale"][1]),
							 int(64 * self.settings["text_scale"][1]), int(64 * self.settings["text_scale"][1]))

		self.anl = QLabel(self)  # anl means app_name_label
		self.anl.move(int(76 * self.settings["ui_scale"][1]), int(10 * self.settings["ui_scale"][1]))
		self.anl.setText("CrystalStudio")
		self.anl.setStyleSheet(helper.generate_stylesheet())
		self.anl.adjustSize()

		self.avl = QLabel(self)  # avl means app_version_label
		self.avl.setText(helper.version)
		self.avl.adjustSize()
		self.avl.move(int(76 * self.settings["ui_scale"][1]), int(31 * self.settings["ui_scale"][1]))
		self.avl.setStyleSheet(helper.generate_stylesheet() + " QLabel {color: gray; font-size: " + str(
			int(12 * self.settings["text_scale"][1])) + "px;}")
		self.avl.adjustSize()

		new_project = QPushButton("New project", self)
		new_project.clicked.connect(self.new_project_fnc)
		new_project.setToolTip("Create a new project")
		new_project.move(int(25 * self.settings["ui_scale"][1]), int(80 * self.settings["ui_scale"][1]))

		self.pointed.append(new_project)
		self.adjusted.append(new_project)

		open_project = QPushButton("Open Project", self)
		open_project.setToolTip("Open a saved project")
		open_project.clicked.connect(self.open_project_fnc)
		open_project.move(int(25 * self.settings["ui_scale"][1]), int(110 * self.settings["ui_scale"][1]))
		self.pointed.append(open_project)
		self.adjusted.append(open_project)

		setting_btn = QPushButton("Settings", self)
		setting_btn.setToolTip("Open settings")
		setting_btn.clicked.connect(lambda: self.open_settings())
		setting_btn.move(int(25 * self.settings["ui_scale"][1]), int(140 * self.settings["ui_scale"][1]))
		self.pointed.append(setting_btn)
		self.adjusted.append(setting_btn)

		add_bookmark_btn = QPushButton("+", self)
		add_bookmark_btn.setToolTip("Add a bookmark to the bookmark list")
		add_bookmark_btn.clicked.connect(lambda: self.open_bookmarks())
		add_bookmark_btn.move(int(900 * self.settings["ui_scale"][1]), int(80 * self.settings["ui_scale"][1]))
		add_bookmark_btn.adjustSize()
		add_bookmark_btn.setFixedSize(int(40 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		add_bookmark_btn.setStyleSheet(helper.generate_extra_style()["bookmark-projects-add"])
		self.pointed.append(add_bookmark_btn)

		self.setStatusBar(QStatusBar(self))

		self.setFixedSize(int(960 * self.settings["ui_scale"][1]), int(540 * self.settings["ui_scale"][1]))

		self.fix_css()
		self.build_bookmark_projects()

	def open_bookmarks(self):
		if self.w is None:
			self.w = BookmarksDialog(self)
		self.w.show()
		self.hide()

	def build_bookmark_projects(self):
		background = QLabel(self)
		background.move(int(280 * self.settings["ui_scale"][1]), int(80 * self.settings["ui_scale"][1]))
		background.setFixedSize(int(600 * self.settings["ui_scale"][1]), int(370 * self.settings["ui_scale"][1]))
		background.setStyleSheet(helper.generate_extra_style()["bookmark-projects-background"])

		num = 1
		bookmarked_project = self.settings["bookmarked_projects"]
		# bookmarked_project.reverse()

		for project in bookmarked_project:
			if num != 11:
				label = QLabel(self)
				label.setText(project)
				label.adjustSize()
				label.setStyleSheet(helper.generate_extra_style()["bookmark-projects-name"])
				label.move(int(295 * self.settings["ui_scale"][1]),
						   int(60 * self.settings["ui_scale"][1] + (num * 35 * self.settings["ui_scale"][1])))

				open_btn = QPushButton(self)
				open_btn.setToolTip("Open the project")
				open_btn.setText("Open")
				open_btn.move(int(730 * self.settings["ui_scale"][1]),
							  int(60 * self.settings["ui_scale"][1] + (num * 35 * self.settings["ui_scale"][1])))
				open_btn.adjustSize()
				open_btn.setFixedSize(int(85 * self.settings["ui_scale"][1]), int(30 * self.settings["ui_scale"][1]))
				open_btn.clicked.connect(lambda throw_away, label=label: self.open_project_from_bookmark(label))

				remove_btn = QPushButton(self)
				remove_btn.setToolTip("Remove project from bookmarks")
				remove_btn.setText("X")
				remove_btn.move(int(830 * self.settings["ui_scale"][1]),
								int(60 * self.settings["ui_scale"][1] + (num * 35 * self.settings["ui_scale"][1])))
				remove_btn.setStyleSheet(helper.generate_extra_style()["bookmark-projects-rm"])
				remove_btn.adjustSize()
				remove_btn.setFixedSize(int(30 * self.settings["ui_scale"][1]), int(30 * self.settings["ui_scale"][1]))
				remove_btn.clicked.connect(lambda throw_away, num=num: self.bookmark_remove(num))

				self.pointed.append(open_btn)
				self.pointed.append(remove_btn)
				num += 1

				self.fix_css()
			else:
				break

		self.fix_css()

	def save(self):
		safe_file = open("crys/storage/settings.json", "w")
		json.dump(self.settings, safe_file)

	def bookmark_remove(self, num):
		self.hide()
		BookmarkRemoveDialog(self, num)

	def open_project_from_bookmark(self, label: QLabel):
		try:
			mem_file = open("editor/" + label.text() + "/save.json", "r")
			mem = json.load(mem_file)
			Editor(mem["info"]["name"], ", ".join(mem["info"]["authors"]), mem["info"]["out"]).show()
			self.hide()
		except FileNotFoundError:
			print("Error, invalid bookmark name. Cannot load project " + label.text())

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
		# checkbox.check(int(20 * self.settings["ui_scale"][1]), int(20 * self.settings["ui_scale"][1]))

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

		self.np_dlg.setFixedSize(int(480 * self.settings["ui_scale"][1]), int(270 * self.settings["ui_scale"][1]))

		checkbox.toggled.connect(input_out.setEnabled)
		self.fix_css()

		self.np_dlg.exec()

	def open_project_fnc(self):
		file = str(QFileDialog.getExistingDirectory(None, "Select project directory"))
		try:
			mem_file = open(file + "/save.json", "r")
			mem = json.load(mem_file)
			Editor(mem["info"]["name"], ", ".join(mem["info"]["authors"]), mem["info"]["out"]).show()
			self.hide()
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

				file = "editor/" + name

			except FileExistsError as err:
				print("ERROR:", err, "| Please pick a different name.")
				sys.exit(1)

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

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


class BookmarkRemoveDialog(QMessageBox):
	def __init__(self, parent, num):
		super().__init__(parent)

		self.settings = helper.get_settings()

		qm = QMessageBox()
		qm.setWindowTitle("Are you sure?")
		ret = qm.information(self, 'Are you sure?',
							 f"Are you sure to delete \"{self.settings['bookmarked_projects'][num - 1]}\"?",
							 qm.StandardButton.Yes | qm.StandardButton.No, qm.StandardButton.No)

		if ret == qm.StandardButton.Yes:
			self.settings['bookmarked_projects'].pop(num - 1)
			self.save()
			qm.hide()

		qm.setGeometry(500, 500, int(200 * self.settings["ui_scale"][1]), int(100 * self.settings["ui_scale"][1]))

		# self.show()
		Creator().show()

	# Creator().bookmark_remove(1)

	def save(self):
		try:
			file = open("crys/storage/settings.json", "w")
			json.dump(self.settings, file)
		except:
			print("Error while removing bookmark")


class BookmarksDialog(QDialog):
	def __init__(self, parent):
		super().__init__(parent)

		self.settings = helper.get_settings()
		self.setWindowTitle("Add bookmark")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()
		self.layout3 = QHBoxLayout()
		self.info = QLabel("")
		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())

		if len(self.settings["bookmarked_projects"]) < 10:
			message1 = QLabel("Project name:")
			save = QPushButton("Add")
			save.clicked.connect(lambda: self.add_btn_clicked())
			self.text = QLineEdit()

			self.layout2.addWidget(message1)
			self.layout2.addWidget(self.text)
			self.layout3.addWidget(save)
		else:
			self.info.setText("Maximum amount of bookmarks reached!")

		self.layout1.addWidget(self.info)
		self.layout3.addWidget(cancel)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)

		self.setLayout(self.layout)

		self.setFixedSize(int(800 * self.settings["ui_scale"][1]), int(300 * self.settings["ui_scale"][1]))

		self.fix_css()

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

	def add_btn_clicked(self):
		if self.text.text() != "":
			try:
				os.mkdir("editor/" + self.text.text())
				os.rmdir("editor/" + self.text.text())
				self.info.setText("That project doesn't exist! Please pick a different name.")
			except:
				self.settings["bookmarked_projects"].append(self.text.text())
				self.save()
				self.hide()
				Creator().show()

	def save(self):
		file = open("crys/storage/settings.json", "w")
		json.dump(self.settings, file)

	def cancel(self):
		self.hide()
		Creator().show()

	def closeEvent(self, event):
		self.cancel()


class Editor(QWidget):
	def __init__(self, name: str = None, author: str = None, out: str = None):
		super().__init__()

		self.name = name
		self.author = author
		self.out = out

		self.settings = helper.get_settings()

		self.preview = []

		try:
			file = open(f"editor/{name}/save.json", "r")
			self.mem_data = json.load(file)
			file.close()
		except FileNotFoundError:
			file = open(f"editor/{name}/save.json", "w")

			self.mem_data = {
				"info": {"name": name, "authors": author.split(", "), "out": self.out},
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

		try:
			file = open(f"editor/{name}/script.json", "r")
			self.script_data = json.load(file)
			file.close()
		except FileNotFoundError:
			file = open(f"editor/{name}/script.json", "w")

			self.script_data = {"global_variables": {},
								"functions": {},
								"checks": {},
								}

			json.dump(self.script_data, file)
			file.close()

		self.save_file = open(f"editor/{name}/save.json", "r")
		self.editor_file = open(f"editor/{name}/editor.json", "r")

		self.build_ui()

	def build_ui(self):
		self.fix_css()

		self.layout = QVBoxLayout(self)
		self.layout.setContentsMargins(int(200 * self.settings["ui_scale"][1]), int(200 * self.settings["ui_scale"][1]),
									   int(200 * self.settings["ui_scale"][1]), int(200 * self.settings["ui_scale"][1]))

		self.setLayout(self.layout)

		self.setFixedSize(int(1920 * self.settings["ui_scale"][1]), int(1080 * self.settings["ui_scale"][1]))
		self.setWindowTitle("CrystalStudio - " + self.name)

		add_scene_btn = QPushButton(self)
		add_scene_btn.setText("+")
		add_scene_btn.clicked.connect(lambda: self.add_scene())
		add_scene_btn.adjustSize()
		add_scene_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		add_button_btn = QPushButton(self)
		add_button_btn.setText("+ Button")
		add_button_btn.clicked.connect(lambda: self.add_button())
		add_button_btn.adjustSize()
		add_button_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		add_input_btn = QPushButton(self)
		add_input_btn.setText("+ Input field")
		add_input_btn.clicked.connect(lambda: self.add_input())
		add_input_btn.adjustSize()
		add_input_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		remove_scene_btn = QPushButton(self)
		remove_scene_btn.setText("-")
		remove_scene_btn.clicked.connect(lambda: self.remove_scene())
		remove_scene_btn.adjustSize()
		remove_scene_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		build_btn = QPushButton(self)
		build_btn.setText("Build game")
		build_btn.adjustSize()
		build_btn.clicked.connect(lambda: self.open_build_menu())

		self.save_btn = QPushButton(self)
		self.save_btn.setText("Save")
		self.save_btn.adjustSize()

		back_to_mainmenu = QPushButton(self)
		back_to_mainmenu.setText("Back to main menu")
		back_to_mainmenu.adjustSize()

		name = QLabel(self)
		name.setText("Editing " + self.name + " (" + self.out + ")")
		authors = QLabel(self)
		authors.setText("Made by " + self.author)
		authors.adjustSize()
		name.adjustSize()

		self.scenes_widget = QComboBox(self)
		self.refresh_scenes_widget()

		self.scenes_widget.currentIndexChanged.connect(lambda: self.build_preview())

		self.scenes_widget.setCurrentIndex(self.editor_data["current_scene"])

		name.move(int(10 * self.settings["ui_scale"][1]), int(5 * self.settings["ui_scale"][1]))
		authors.move(int(10 * self.settings["ui_scale"][1]), int(29 * self.settings["ui_scale"][1]))
		self.scenes_widget.move(int(1780 * self.settings["ui_scale"][1]), int(10 * self.settings["ui_scale"][1]))
		self.scenes_widget.setFixedSize(int(130 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		add_scene_btn.move(int(1877 * self.settings["ui_scale"][1]), int(60 * self.settings["ui_scale"][1]))
		add_scene_btn.setStyleSheet(
			'color: white; background-color: rgb(59, 171, 130); border: 1px solid rgb(59, 171, 130);')
		add_scene_btn.setFixedSize(int(32 * self.settings["ui_scale"][1]), int(32 * self.settings["ui_scale"][1]))

		add_button_btn.move(int(1780 * self.settings["ui_scale"][1]), int(100 * self.settings["ui_scale"][1]))
		add_button_btn.setFixedSize(int(130 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		add_button_btn.setStyleSheet(
			'color: white; background-color: rgb(59, 171, 130); border: 1px solid rgb(59, 171, 130);')

		add_input_btn.move(int(1780 * self.settings["ui_scale"][1]), int(150 * self.settings["ui_scale"][1]))
		add_input_btn.setFixedSize(int(130 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		add_input_btn.setStyleSheet('color: white; background-color: rgb(59, 171, 130); border: 1px solid rgb(59, 171, 130);')

		remove_scene_btn.move(int(1780 * self.settings["ui_scale"][1]), int(60 * self.settings["ui_scale"][1]))
		remove_scene_btn.setStyleSheet(
			'color: white; background-color: rgb(179, 0, 0); border: 1px solid rgb(179, 0, 0);')
		remove_scene_btn.setFixedSize(int(32 * self.settings["ui_scale"][1]), int(32 * self.settings["ui_scale"][1]))

		back_to_mainmenu.move(int(1530 * self.settings["ui_scale"][1]), int(1020 * self.settings["ui_scale"][1]))
		back_to_mainmenu.setFixedSize(int(200 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		self.save_btn.move(int(1740 * self.settings["ui_scale"][1]), int(1020 * self.settings["ui_scale"][1]))
		self.save_btn.setFixedSize(int(60 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))
		build_btn.move(int(1810 * self.settings["ui_scale"][1]), int(1020 * self.settings["ui_scale"][1]))
		build_btn.setFixedSize(int(100 * self.settings["ui_scale"][1]), int(40 * self.settings["ui_scale"][1]))

		back_to_mainmenu.clicked.connect(lambda: self.back_to_mm())
		self.save_btn.clicked.connect(lambda: self.save())

		self.build_preview()

	def build_preview(self):
		# print(self.preview)
		for prev in self.preview:
			try:
				prev.deleteLater()
			except:
				continue

		# print(self.preview)
		lab = QLabel(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["title"])
		lab.setStyleSheet("font-size: " + str(int(32 * self.settings["ui_scale"][1])) + "px;}")
		lab.adjustSize()
		self.preview.append(lab)
		self.layout.addWidget(lab)
		throw_away = 0
		num = 0
		for i1000 in range(len(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"])):
			try:
				if type(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][0]) == str: # button
					btn = QPushButton(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][0])
					btn.clicked.connect(
						lambda throw_away, btn=btn, num=num: self.btn_editor(btn, self.scenes_widget.currentIndex(), num))
					self.preview.append(btn)
					self.layout.addWidget(btn)
					num += 1
				elif self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][0] == 1: # input
					inp_lay = QHBoxLayout()
					inp_lab = QLabel(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][1])
					inp = QExtension.ClickableLineEdit()
					inp.setDisabled(True)
					inp.setText(self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][i1000][2])
					inp.mousePressEvent = lambda throw_away, scene_id=self.scenes_widget.currentIndex(), num=num, label=inp_lab, inp=inp: self.input_editor(scene_id, num, label, inp)
					inp_lab.mousePressEvent = lambda throw_away, scene_id=self.scenes_widget.currentIndex(), num=num, label=inp_lab, inp=inp: self.input_editor(scene_id, num, label, inp)
					self.preview.append(inp_lab)
					self.preview.append(inp)
					inp_lay.addWidget(inp_lab)
					inp_lay.addWidget(inp)
					self.layout.addLayout(inp_lay)
					num += 1
			except IndexError:
				continue

		lab.mousePressEvent = lambda throw_away, scene_id=self.scenes_widget.currentIndex(), lab=lab: self.txt_editor(
			lab, scene_id)

		self.fix_css()
		self.save()

	def fix_css(self):
		self.setStyleSheet('background-color: rgb(37, 37, 37);')

		self.setStyleSheet(helper.generate_stylesheet())

	def open_build_menu(self):
		BuildMenu(self, self.mem_data, self.editor_data).show()
		self.hide()

	def btn_editor(self, btn, scene_id, btn_id):
		self.hide()

		dlg = ButtonEditor(self, btn, scene_id, self.mem_data, btn_id, self.editor_data)
		dlg.exec()

	def input_editor(self, scene_id, id_, lab, inp):
		self.hide()

		dlg = InputEditor(self, lab, scene_id, self.mem_data, id_, self.editor_data, inp)
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

	def remove_input(self, id):
		del self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][id]
		self.save()
		self.build_preview()
		self.show()

	def change_btn_text(self, button: int, update):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][0] = update
		self.save()

	def change_btn_note(self, button: int, note):
		self.editor_data["scenes"][self.scenes_widget.currentIndex()][button]["notes"] = note
		self.save()

	def change_btn_exec(self, button: int, exec_, function: str = None):
		if type(exec_) == int:
			self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][1] = exec_ + 1
			self.save()
		elif type(exec_) == str:
			self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][1] = exec_
			try:
				self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button][2] = function
				self.save()
			except IndexError:
				self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][button].append(function)
				self.save()

	def change_label_text(self, text):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["title"] = text
		self.save()

	def change_input_label(self, input_id: int, text: str):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][input_id][1] = text
		self.save()

	def change_input_default_value(self, input_id: int, text: str):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"][input_id][2] = text
		self.save()

	def change_input_note(self, input_id: int, text: str):
		self.editor_data["scenes"][self.scenes_widget.currentIndex()][input_id]["notes"] = text
		self.save()

	def back_to_mm(self):
		w = Creator()
		w.show()
		self.hide()

	def add_scene(self):
		self.mem_data["scenes"].append(
			{"title": "Scene " + str(self.scenes_widget.count() + 1), "buttons": [["Button 1", 1], ["Button 2", 1]]})
		self.editor_data["scenes"].append([{"notes": ""}, {"notes": ""}])
		self.save()

		self.refresh_scenes_widget()
		self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 1)

	def add_button(self):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"].append(["Button", 1])
		self.editor_data["scenes"][self.scenes_widget.currentIndex()].append({"notes": ""})

		self.save()

		self.build_preview()

	def add_input(self):
		self.mem_data["scenes"][self.scenes_widget.currentIndex()]["buttons"].append([1, "Input: ", "Default value"])
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
					f"An error occurred. This is probably because:\n -> You tried to delete scene number 1 (main scene cannot be removed)\n\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

			elif self.scenes_widget.currentIndex() == self.scenes_widget.count() - 1:
				del self.mem_data["scenes"][self.scenes_widget.currentIndex()]
				del self.editor_data["scenes"][self.scenes_widget.currentIndex()]

				self.save()
				self.refresh_scenes_widget()
				self.scenes_widget.setCurrentIndex(self.scenes_widget.count() - 1)
			else:
				print(
					f"An error occurred. This is probably because:\n -> You tried to delete scene number 1 (main scene cannot be removed)\nIf this is not the case, please report this issue on Github\nMore info: \"ScenesWidget.currentIndex() in [0 and count-1]\" removing bug")

		except IndexError as err:
			print(
				f"An error occurred. \n\nPlease report this issue on Github\nMore info: \"[IndexError] {err} --- tried remove_scene(self)")

	def closeEvent(self, event):
		self.save()
		self.hide()
		Creator().show()


class SettingsWindow(QTabWidget):
	def __init__(self, parent=None):
		super(SettingsWindow, self).__init__(parent)

		self.settings = helper.get_settings()

		self.setFixedSize(int(self.settings["ui_scale"][1] * 540), int(self.settings["ui_scale"][1] * 640))

		self.build_ui()

	def build_ui(self):
		self.tab1 = QWidget()
		self.tab2 = QWidget()
		self.tab3 = QWidget()
		self.tab4 = QWidget()

		self.addTab(self.tab1, "General settings")
		self.addTab(self.tab2, "Color and themes")
		self.addTab(self.tab4, "Icon")
		self.addTab(self.tab3, "Save")

		self.build_tab1UI()
		self.build_tab2UI()
		self.build_tab4UI()
		self.build_tab3UI()

		self.fix_css()

		self.setWindowTitle("CrystalStudio - (Settings)")

	def build_tab1UI(self):
		layout1 = QHBoxLayout()
		layout2 = QHBoxLayout()
		layout = QVBoxLayout()
		layout.addLayout(layout1)
		layout.addLayout(layout2)
		label1 = QLabel("UI scale: ")
		self.selector1 = QComboBox(self)
		self.selector1.insertItem(0, "2 (Large)")
		self.selector1.insertItem(1, "1 (Default)")
		self.selector1.insertItem(2, "0.5 (Small)")
		self.selector1.insertItem(3, "0.25 (Mini)")
		self.selector1.insertItem(4, "Custom (Beta)")
		self.selector1.setCurrentIndex(self.settings["ui_scale"][0])

		self.selector1.currentIndexChanged.connect(lambda: self.save())

		self.custom_size_wid = QLineEdit(str(self.settings["ui_scale"][1]))
		self.custom_size_wid.textChanged.connect(lambda: self.save())

		if self.selector1.currentText().startswith("Custom"):
			self.custom_size_wid.setEnabled(True)
		else:
			self.custom_size_wid.setDisabled(True)

		layout1.addWidget(label1)
		layout1.addWidget(self.selector1)
		layout1.addWidget(self.custom_size_wid)

		self.setTabText(0, "General settings")
		self.tab1.setLayout(layout)

	def build_tab2UI(self):
		layout = QVBoxLayout()
		layout1 = QHBoxLayout()
		layout2 = QHBoxLayout()
		layout3 = QVBoxLayout()
		prev_layout = QVBoxLayout()
		layout.addLayout(layout1)
		layout.addLayout(layout2)
		layout.addLayout(layout3)
		layout.addLayout(prev_layout)
		label1 = QLabel("Theme: ")
		label2 = QLabel("Custom theme: ")
		label3 = QLabel("\n\n\n\n\n\n\n")
		layout3.addWidget(label3)
		layout3.setAlignment(label3, Qt.AlignmentFlag.AlignCenter)
		layout2.addWidget(label2)
		self.custom_theme = QTextEdit()
		layout2.addWidget(self.custom_theme)
		self.selector3 = QComboBox(self)
		self.selector3.insertItem(0, "Midnight")
		self.selector3.insertItem(1, "Dark (Default)")
		self.selector3.insertItem(2, "Light")
		self.selector3.insertItem(3, "Eyeburn")
		self.selector3.insertItem(4, "Sync")
		self.selector3.setCurrentIndex(self.settings["theme"][0])
		self.custom_theme.setText(self.settings["custom_theme"])
		self.custom_theme.textChanged.connect(lambda: self.save())

		prev2 = QPushButton("Preview")
		prev3 = QComboBox()
		prev3.addItem("Preview 1")
		prev3.addItem("Preview 2")
		prev4 = QLineEdit()
		prev4.setText("Preview")
		prev5 = QTextEdit()
		prev5.setText("Preview")
		prev_layout.addWidget(prev2)
		prev_layout.addWidget(prev3)
		prev_layout.addWidget(prev4)
		prev_layout.addWidget(prev5)

		self.selector3.currentIndexChanged.connect(lambda: self.save())

		layout1.addWidget(label1)
		layout1.addWidget(self.selector3)

		self.setTabText(1, "Color and themes")
		self.tab2.setLayout(layout)

	def build_tab3UI(self):
		layout = QHBoxLayout()

		self.save_btn = QPushButton("Save")
		self.save_btn.clicked.connect(lambda: self.save())
		self.exit_btn = QPushButton("Save and exit")
		self.exit_btn.clicked.connect(lambda: self.exit())
		layout.addWidget(self.save_btn)
		layout.addWidget(self.exit_btn)

		self.setTabText(3, "Save")
		self.tab3.setLayout(layout)

	def build_tab4UI(self):
		layout = QVBoxLayout()
		layout1 = QHBoxLayout()
		layout2 = QHBoxLayout()
		layout3 = QHBoxLayout()

		label = QLabel("Current Icon:")
		self.selected_icon = QComboBox()
		self.selected_icon.addItem("Default Icon")
		self.selected_icon.addItem("Mix")
		self.selected_icon.addItem("Legacy")
		self.selected_icon.setCurrentIndex(settings["icon"][0])
		self.selected_icon.currentIndexChanged.connect(lambda: self.save())

		credit = QLabel("Restart CrystalStudio to see change\nBig thank you to VlogFox for making these good looking new icons")

		self.preview_icon = QLabel()
		self.preview_icon.setPixmap(QPixmap("crys/storage/icon/" + settings["icon"][1] + ".png"))
		self.preview_icon.setScaledContents(True)
		self.preview_icon.setFixedSize(int(128 * self.settings["ui_scale"][1]),
									   int(128 * self.settings["ui_scale"][1])),

		layout1.addWidget(label)
		layout1.addWidget(self.selected_icon)
		layout2.addWidget(credit)
		layout3.addWidget(self.preview_icon)

		layout.addLayout(layout1)
		layout.addLayout(layout2)
		layout.addLayout(layout3)
		self.setTabText(2, "Icon")
		self.tab4.setLayout(layout)

	def save(self):
		self.settings["theme"] = [self.selector3.currentIndex(), self.selector3.currentText().split()[0].lower()]
		if not self.selector1.currentText().lower().startswith("custom"):
			self.settings["ui_scale"] = [self.selector1.currentIndex(),
										 float(self.selector1.currentText().split()[0].lower())]
			self.settings["text_scale"] = self.settings["ui_scale"]
			self.custom_size_wid.setDisabled(True)
		else:
			self.custom_size_wid.setEnabled(True)
			if self.custom_size_wid.text().replace(".", "").isnumeric():
				if not self.custom_size_wid.text().startswith(".") and not self.custom_size_wid.text().startswith("0"):
					self.custom_size = float(self.custom_size_wid.text())

					if 3 > float(self.custom_size_wid.text()):
						self.settings["ui_scale"] = [self.selector1.currentIndex(),
													 float(self.custom_size)]
						self.settings["text_scale"] = self.settings["ui_scale"]
				elif self.custom_size_wid.text().startswith("0"):
					splitted = self.custom_size_wid.text().split(".")
					if splitted[0] is not None:
						if not splitted[0].startswith("0"):
							if splitted[0].isnumeric():
								if splitted[1] is not None:
									if splitted[1].isnumeric():
										if float(self.custom_size_wid.text()) < 3 and float(
												self.custom_size_wid.text()) > 0.15:
											self.custom_size = float(self.custom_size_wid.text())

											self.settings["ui_scale"] = [self.selector1.currentIndex(),
																		 float(self.custom_size)]
											self.settings["text_scale"] = self.settings["ui_scale"]
						elif splitted[0].startswith("0"):
							try:
								if splitted[0].isnumeric():
									if splitted[1] is not None:
										if splitted[1] != "0":
											if splitted[1].isnumeric():
												if float(self.custom_size_wid.text()) < 3 and float(
														self.custom_size_wid.text()) > 0.15:
													self.custom_size = float(self.custom_size_wid.text())

													self.settings["ui_scale"] = [self.selector1.currentIndex(),
																				 float(self.custom_size)]
													self.settings["text_scale"] = self.settings["ui_scale"]
							except IndexError:
								pass
			else:
				pass

		self.settings["custom_theme"] = self.custom_theme.toPlainText()
		new_icon_text = self.selected_icon.currentText()
		if new_icon_text == "Default Icon":
			self.settings["icon"][1] = "new_icon"
		elif new_icon_text == "Mix":
			self.settings["icon"][1] = "middle"
		else:
			self.settings["icon"][1] = "legacy"

		self.settings["icon"][0] = self.selected_icon.currentIndex()
		settings_file = open(helper.settings_filepath(), "w")
		json.dump(self.settings, settings_file)
		settings_file.close()
		self.preview_icon.setPixmap(QPixmap("crys/storage/icon/" + settings["icon"][1] + ".png"))

		self.fix_css()

	def exit(self):
		self.save()
		Creator().show()
		self.hide()

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())
		self.setFixedSize(int(self.settings["ui_scale"][1] * 540), int(self.settings["ui_scale"][1] * 640))
		self.preview_icon.setFixedSize(int(128 * self.settings["ui_scale"][1]), int(128 * self.settings["ui_scale"][1]))
		self.preview_icon.setPixmap(QPixmap("crys/storage/icon/" + settings["icon"][1] + ".png"))

	def closeEvent(self, event):
		self.exit()

class ButtonEditor(QDialog):
	def __init__(self, parent, btn: QPushButton, scene_id, memory, btn_id, editor):
		super().__init__(parent)

		labels = []
		lines = []
		buttons = []

		self.settings = helper.get_settings()
		self.w = None

		self.editor = editor
		self.mem = memory
		self.scene_id = scene_id
		self.btn_id = btn_id
		self.btn = btn

		self.setWindowTitle(f"Editing button {self.btn_id} in scene {self.scene_id}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()
		self.layout3 = QHBoxLayout()
		self.layout4 = QVBoxLayout()
		self.layout5 = QHBoxLayout()
		message1 = QLabel("Button text:")
		labels.append(message1)
		self.btn_text = QLineEdit()
		self.btn_text.setText(self.btn.text())
		lines.append(self.btn_text)

		message2 = QLabel("Button action:")
		message_script = QLabel("Script function:")
		self.script_function = QComboBox(self)
		for func in MemCheck(self.mem).get_all_functions():
			self.script_function.addItem(func)

		self.args_btn = QPushButton("Function arguments")
		self.args_btn.setDisabled(True)
		self.args_btn.clicked.connect(lambda: self.open_function_args())

		labels.append(message2)
		self.scenes_widget = QComboBox(self)
		self.scenes_widget.addItem(f"Script")
		for i in range(len(memory["scenes"])):
			self.scenes_widget.addItem(f"Go to {i + 1}")
		if self.mem["scenes"][scene_id]["buttons"][btn_id][1] == "script":
			self.scenes_widget.setCurrentIndex(0)
			self.script_function.setCurrentText(self.mem["scenes"][scene_id]["buttons"][btn_id][2])
			self.script_function.setEnabled(True)
			self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][2] = self.script_function.currentText()
			if self.script_function.currentText() != "":
				function_ = self.script_function.currentText()
				script_file = open(f"editor/{self.mem['info']['name']}/script.json", "r")
				script = json.load(script_file)
				if script["functions"][function_]["args"] != {}:
					self.args_btn.setEnabled(True)
					args = []
					for arg in script["functions"][function_]["args"]:
						args.append(arg)

					num = 0
					values = []
					for arg2 in args:
						if num == 0:
							try:
								self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3] = []
							except IndexError:
								self.mem["scenes"][self.scene_id]["buttons"][self.btn_id].append([])

						try:
							value_txt = self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]
						except IndexError:
							value_txt = script["functions"][self.mem['scenes'][scene_id]['buttons'][btn_id][2]]['args'][arg2]

						values.append(value_txt)

						self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3].append(values[num])
						num += 1
						json.dump(self.mem, open(f"editor/{self.mem['info']['name']}/save.json", "w"))

		else:
			self.scenes_widget.setCurrentIndex(self.mem["scenes"][scene_id]["buttons"][btn_id][1])
			self.script_function.setDisabled(True)
			self.args_btn.setDisabled(True)

		self.scenes_widget.currentIndexChanged.connect(lambda: self.update_selector())

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
		buttons.append(self.args_btn)
		buttons.append(save)

		for button in buttons:
			button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.btn_text)
		self.layout2.addWidget(message2)
		self.layout2.addWidget(self.scenes_widget)
		self.layout3.addWidget(message_script)
		self.layout3.addWidget(self.script_function)
		self.layout4.addWidget(message3)
		self.layout4.addWidget(self.notes)
		self.layout5.addWidget(remove_btn)
		self.layout5.addWidget(cancel)
		self.layout5.addWidget(self.args_btn)
		self.layout5.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)
		self.layout.addLayout(self.layout4)
		self.layout.addLayout(self.layout5)

		self.setLayout(self.layout)

		self.fix_css()

		self.setFixedSize(int(800 * self.settings["ui_scale"][1]), int(300 * self.settings["ui_scale"][1]))

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

	def update_selector(self):
		if self.scenes_widget.currentText() == "Script":
			self.script_function.setEnabled(True)
			function_ = self.script_function.currentText()
			script_file = open(f"editor/{self.mem['info']['name']}/script.json", "r")
			script = json.load(script_file)
			if script["functions"] != {}:
				if script["functions"][function_]["args"] != {}:
					self.args_btn.setEnabled(True)
				else:
					self.args_btn.setDisabled(True)
		else:
			self.script_function.setDisabled(True)
			self.args_btn.setDisabled(True)

	def open_function_args(self):
		if self.w is None:
			self.w = FunctionArgsUI(self, self.mem, self.editor, self.btn, self.btn_id, self.scene_id)
		self.w.show()

	def remove_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]), self.mem["info"]["out"]).remove_btn(
			self.btn_id)
		self.hide()

	def save_btn_clicked(self):
		if self.scenes_widget.currentIndex() != 0:
			Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
				   self.mem["info"]["out"]).change_btn_exec(self.btn_id, self.scenes_widget.currentIndex() - 1)
		else:
			Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
				   self.mem["info"]["out"]).change_btn_exec(self.btn_id, "script", self.script_function.currentText())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_btn_note(self.btn_id, self.notes.toPlainText())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_btn_text(self.btn_id, self.btn_text.text())
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()

	def cancel(self):
		self.w = Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]), self.mem["info"]["out"])
		self.w.show()

		self.hide()

	def closeEvent(self, event):
		self.cancel()

class InputEditor(QDialog):
	def __init__(self, parent, label: QLabel, scene_id, memory, id, editor, inp: QLineEdit):
		super().__init__(parent)
		self.settings = helper.get_settings()

		self.editor = editor
		self.mem = memory
		self.scene_id = scene_id
		self.id = id
		self.label = label
		self.input = inp

		self.setWindowTitle(f"Editing input field {self.id} in scene {self.scene_id}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QHBoxLayout()
		self.layout3 = QHBoxLayout()
		self.layout4 = QVBoxLayout()
		self.layout5 = QHBoxLayout()
		message1 = QLabel("Label text:")
		self.label_text = QLineEdit()
		self.label_text.setText(self.label.text())

		message2 = QLabel("Input field default value:")
		self.input_field_default_value = QLineEdit(self.input.text())

		message3 = QLabel("Notes:")
		self.notes = QTextEdit()
		self.notes.setText(editor["scenes"][self.scene_id][self.id]["notes"])

		remove_btn = QPushButton("Remove")
		remove_btn.clicked.connect(lambda: self.remove_btn_clicked())
		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())
		save = QPushButton("Save")
		save.clicked.connect(lambda: self.save_btn_clicked())

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.label_text)
		self.layout2.addWidget(message2)
		self.layout2.addWidget(self.input_field_default_value)
		self.layout4.addWidget(message3)
		self.layout4.addWidget(self.notes)
		self.layout5.addWidget(remove_btn)
		self.layout5.addWidget(cancel)
		self.layout5.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)
		self.layout.addLayout(self.layout4)
		self.layout.addLayout(self.layout5)

		self.setLayout(self.layout)

		self.fix_css()

		self.setFixedSize(int(800 * self.settings["ui_scale"][1]), int(300 * self.settings["ui_scale"][1]))

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

	def remove_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]), self.mem["info"]["out"]).remove_input(
			self.id)
		self.hide()

	def save_btn_clicked(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_input_note(self.id, self.notes.toPlainText())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_input_label(self.id, self.label_text.text())
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).change_input_default_value(self.id, self.input_field_default_value.text())
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()

	def cancel(self):
		self.hide()
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
			   self.mem["info"]["out"]).show()

	def closeEvent(self, event):
		self.cancel()

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

		self.settings = helper.get_settings()

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

		self.setFixedSize(int(800 * self.settings["ui_scale"][1]), int(300 * self.settings["ui_scale"][1]))

		self.fix_css()

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

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

	def closeEvent(self, event):
		self.cancel()


class BuildMenu(QDialog):
	def __init__(self, parent, memory, editor):
		super().__init__(parent)

		self.labels = []
		self.lines = []
		self.buttons = []

		self.settings = helper.get_settings()

		self.editor = editor
		self.mem = memory

		self.setWindowTitle(f"Build {self.mem['info']['name']}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout3 = QHBoxLayout()
		self.layout2 = QHBoxLayout()

		message1 = QLabel("Builder type:")
		message2 = QLabel("Replace old build:")
		self.labels.append(message1)
		self.builder_type = QComboBox()
		self.builder_type.insertItem(0, "Web application (JavaScript, HTML, CSS)")
		self.lines.append(self.builder_type)

		self.replace_check = QCheckBox()
		self.replace_check.setChecked(True)

		cancel = QPushButton("Cancel")
		cancel.clicked.connect(lambda: self.cancel())
		save = QPushButton("Build")
		save.clicked.connect(lambda: self.build_btn_clicked())
		self.buttons.append(cancel)
		self.buttons.append(save)

		self.layout1.addWidget(message1)
		self.layout1.addWidget(self.builder_type)
		self.layout3.addWidget(message2)
		self.layout3.addWidget(self.replace_check)
		self.layout2.addWidget(cancel)
		self.layout2.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout3)
		self.layout.addLayout(self.layout2)

		self.setLayout(self.layout)

		self.setFixedSize(int(800 * self.settings["ui_scale"][1]), int(300 * self.settings["ui_scale"][1]))

		self.fix_css()

	def fix_css(self):
		self.replace_check.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
		self.setStyleSheet(helper.generate_stylesheet())

	def build_btn_clicked(self):
		try:
			crys.crystal.Game(self.mem, helper.translate_builder(self.builder_type.currentText()), True, self.replace_check.checkState()).build()
			helper.open_file(f"editor/{self.mem['info']['name']}/{self.mem['info']['out']}")
			self.hide()
			Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]),
				   self.mem["info"]["out"]).show()

		except FileExistsError:
			print("ERROR: already exported this once. Delete the old folder and build again!")
			helper.open_file(f"editor/{self.mem['info']['name']}/{self.mem['info']['out']}")

	def cancel(self):
		Editor(self.mem["info"]["name"], ", ".join(self.mem["info"]["authors"]), self.mem["info"]["out"]).show()
		self.hide()

	def closeEvent(self, event):
		self.cancel()

class FunctionArgsUI(QDialog):
	def __init__(self, parent, memory, editor, btn, btn_id, scene_id):
		super().__init__(parent)

		self.settings = helper.get_settings()

		self.editor = editor
		self.mem = json.load(open(f"editor/{memory['info']['name']}/save.json", "r"))
		self.btn = btn
		self.btn_id = btn_id
		self.scene_id = scene_id

		func = self.mem["scenes"][scene_id]["buttons"][btn_id][2]

		script = open(f"editor/{self.mem['info']['name']}/script.json", "r")
		script = json.load(script)
		self.script = script

		self.setWindowTitle(f"Function arguments for {self.mem['scenes'][scene_id]['buttons'][btn_id][2]}")

		self.layout = QVBoxLayout()
		self.layout1 = QHBoxLayout()
		self.layout2 = QVBoxLayout()
		self.layout3 = QHBoxLayout()

		self.args = []
		for arg in self.script["functions"][self.mem['scenes'][scene_id]['buttons'][btn_id][2]]['args']:
			self.args.append(arg)

		self.arg_widgets = []
		self.arg_type_widgets = []
		num = 0
		for arg2 in self.args:
			new_layout = QHBoxLayout()
			pattern = r"([A-Z])"

			result = re.sub(pattern, r' \1', arg2)
			name = QLabel(result)
			arg_type = QComboBox()
			arg_type.addItem("str")
			arg_type.addItem("int")
			arg_type.addItem("float   ")
			print(type(self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]))
			if type(self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]) == str:
				arg_type.setCurrentIndex(0)
			elif type(self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]) == int:
				arg_type.setCurrentIndex(1)
			elif type(self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]) == float:
				arg_type.setCurrentIndex(2)
			else:
				arg_type.setCurrentText("Error")
				arg_type.setDisabled(True)

			try:
				value_txt = self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3][num]
			except IndexError:
				value_txt = self.script["functions"][self.mem['scenes'][scene_id]['buttons'][btn_id][2]]['args'][arg2]

			value = QLineEdit(str(value_txt))
			self.arg_widgets.append(value)
			self.arg_type_widgets.append(arg_type)
			new_layout.addWidget(name)
			new_layout.addWidget(value)
			new_layout.addWidget(arg_type)
			self.layout2.addLayout(new_layout)
			num += 1

		save = QPushButton("Save && Exit")
		save.clicked.connect(lambda: self.exit())

		self.layout3.addWidget(save)

		self.layout.addLayout(self.layout1)
		self.layout.addLayout(self.layout2)
		self.layout.addLayout(self.layout3)

		self.setLayout(self.layout)

		self.setFixedSize(int(500 * self.settings["ui_scale"][1]), int(50 * self.settings["ui_scale"][1] * len(self.args) + 50))

		self.fix_css()

	def fix_css(self):
		self.setStyleSheet(helper.generate_stylesheet())

	def exit(self):
		try:
			num = 0
			for arg in self.args:
				if num == 0:
					try:
						self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3] = []
					except IndexError:
						self.mem["scenes"][self.scene_id]["buttons"][self.btn_id].append([])

				if self.arg_widgets[num].text().isnumeric():
					if self.arg_type_widgets[num].currentIndex() == 1:
						rv = int(self.arg_widgets[num].text())
					elif self.arg_type_widgets[num].currentIndex() == 2:
						rv = float(self.arg_widgets[num].text())
					else:
						rv = str(self.arg_widgets[num].text())
				else:
					rv = str(self.arg_widgets[num].text())

				self.mem["scenes"][self.scene_id]["buttons"][self.btn_id][3].append(rv)
				num += 1
			mem_file = open(f"editor/{self.mem['info']['name']}/save.json", "w")
			json.dump(self.mem, mem_file)
		except Exception as err:
			print(f"Critical error while trying to save save.json. Please report this issue on GitHub!\n{err}")
			sys.exit(0)
		self.hide()

	def closeEvent(self, event):
		json.dump(self.mem, open(f"editor/{self.mem['info']['name']}/save.json", "w"))
		self.exit()

class UpdateWindow(QDialog):
	def __init__(self):
		super().__init__()
		self.updating = False
		self.allow_quit = 3

		self.setWindowTitle("CrystalStudio Updater")

		self.QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

		self.buttonBox = QDialogButtonBox(self.QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.layout = QVBoxLayout()
		self.message = QLabel(
			f"There is a new update available.\n\nYour version: {latest_update}\nNew version: {data}\n\nClick OK to continue or CANCEL to use your outdated and unsecure version of CrystalStudio")
		self.message.setOpenExternalLinks(True)
		self.update_state = QLabel(f"")
		self.layout.addWidget(self.message)
		self.layout.addWidget(self.update_state)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)

	def accept(self):
		self.updating = True
		self.message.setText("Updating...")
		self.buttonBox.deleteLater()
		self.update_state.setText("State: Downloading update files")
		download_url = f"https://github.com/JXSnack/CrystalStudio/archive/refs/tags/v{data}.zip"  # set the download url
		r = requests.get(download_url, allow_redirects=True, stream=True)  # get the download
		z = zipfile.ZipFile(io.BytesIO(r.content))  # get the zipfile
		csuf = "CrystalStudioUpdaterFiles"  # set the folder name
		download_name = f"CrystalStudio-{data}"  # set the downloaded file name
		os.mkdir(csuf)  # make the folder
		z.extractall(f"{csuf}/")  # extract the zip
		csuf = csuf + f"/{download_name}"  # set the new folder name

		self.update_state.setText("State: Making a settings backup")
		settings_backup = json.load(open("crys/storage/settings.json"))  # make a settings backup
		self.update_state.setText("State: Removing old code")
		shutil.rmtree("crys")  # remove the old crystal studio code folder

		os.remove("main.py")  # remove the old main.py
		os.remove("editor.py")  # remove old editor.py

		self.update_state.setText("State: Replacing old code with new code")
		shutil.move(csuf + "/crys", os.getcwd())  # move the new code folder to the place where the old one was
		new_mainfile_content = open(csuf + "/main.py", "r").readlines()  # get new content
		new_mainfile = open("main.py", "w").write("".join(new_mainfile_content))  # place it there where it belongs

		new_editor_content = open(csuf + "/editor.py", "r").readlines()  # get new content
		new_editor = open("editor.py", "w").write("".join(new_editor_content))  # place it there where it belongs

		json.dump(settings_backup, open("crys/storage/settings.json", "w"))  # place the settings backup

		shutil.rmtree("CrystalStudioUpdaterFiles")  # clean up the mess that we made
		self.update_state.setText("State: Cleaning up...")
		self.update_state.deleteLater()
		self.allow_quit = 0 # allow quitting
		self.message.setText("Finished! You can now close this window start the editor")

		# Finished
		print(f"Finished updating to {data}!")

	def reject(self):
		if not self.updating:
			self.hide()
			window = Creator()
			window.show()
		else:
			if self.allow_quit != 0:
				print("Warning: This can cause severe issues!")
				self.message.setText(
					f"Updating... EXITING NOW CAN CAUSE SEVERE ISSUES! Click {self.allow_quit} time(s) more if you want to quit")
				self.allow_quit -= 1
			else:
				sys.exit(0)


if __name__ == "__main__":
	settings = helper.get_settings()
	app = QApplication(sys.argv)

	# window = BuildMenu(Editor("test", "JX_Snack", "out/"), Editor("test", "JX_Snack", "out/").mem_data,
	# 				   Editor("test", "JX_Snack", "out/").editor_data)
	# window = Editor("test", "JX_Snack", "out/")
	# window = SettingsWindow()

	app.setWindowIcon(QIcon("crys/storage/icon/" + settings["icon"][1] + ".png"))

	print("Checking for updates...")
	latest_update = open("crys/storage/latest_update.txt", "r").readline().replace("\n", "")
	update_url = "https://snackbag.net/contents/CrystalProject/latest_update.txt"
	try:
		response = requests.get(update_url)
		data = response.text
		if data.startswith("<!DOCTYPE"):
			print(
				f"Critical error while trying to check for last update: Updater not found. \nPLEASE REPORT THIS ISSUE ON GITHUB. THIS IS A CRITICAL BUG (Dev info: Updater gone?)")
			print(f"\nInfo: Latest update: {latest_update}")
			print(f"\rUpdate URL: {update_url}\n")
			input("Type anything if you have copied the error > ")
			print(f"\n\n\n---------------------------- DEV INFO ----------------------------\n{data}")
			input("Type anything if you have copied the dev info > ")
			print("Please report this issue on GitHub!")
			time.sleep(10)
			sys.exit(1)
		else:
			update_num = data.split(".")
			my_update_num = latest_update.split(".")
			if int(my_update_num[0]) < int(update_num[0]) or (my_update_num[1]) < (update_num[1]) or (my_update_num[2]) < (update_num[2]):
				print(f"You are not on the latest version.\nYour version: {latest_update}\nLatest version: {data}")
				window = UpdateWindow()
				window.show()
			else:
				print("You are on the latest version")
				window = Creator()
				window.show()

	except Exception as err:
		print(
			f"Critical error while trying to check latest update: {err} \nPLEASE REPORT THIS ISSUE ON GITHUB. THIS IS A CRITICAL BUG (Dev info: Server not exists?)")
		print(f"\nInfo: Latest update: {latest_update}")
		print(f"\rUpdate URL: {update_url}\n")
		input("Type anything if you have copied the error > ")
		print("Please report this issue on GitHub!")
		time.sleep(10)
		sys.exit(1)

	app.exec()
