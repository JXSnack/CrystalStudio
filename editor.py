import os
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class Creator(QMainWindow):
	def __init__(self):
		super().__init__()
		self.build_ui()
		self.w = None # no extra window yet
	def build_ui(self):
		self.setWindowTitle("CrystalStudio Editor")

		self.label = QLabel("No recent projects found...")
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.setCentralWidget(self.label)

		toolbar = QToolBar("Toolbar")
		toolbar.setIconSize(QSize(16, 16))
		self.addToolBar(toolbar)

		new_project = QAction("New project", self)
		new_project.setStatusTip("Create a new project")
		new_project.triggered.connect(self.new_project_fnc)
		toolbar.addAction(new_project)

		toolbar.addSeparator()

		open_project = QAction("Open Project", self)
		open_project.setStatusTip("Open a project that is saved")
		open_project.triggered.connect(self.open_project_fnc)
		toolbar.addAction(open_project)

		toolbar.addAction(open_project)

		self.setStatusBar(QStatusBar(self))

		self.setMinimumSize(960, 540)

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

		self.np_dlg.setFixedSize(int(960 / 2), int(540 / 2))

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

class Editor(QWidget):
	def __init__(self, name, author, out):
		super().__init__()

		self.name = name
		self.author = author
		self.out = out
		self.scene = 0

		self.build_ui()

	def build_ui(self):
		self.setFixedSize(1920, 1080)
		self.setWindowTitle("CrystalStudio - " + self.name)

		labels = []
		lists = []
		buttons = []

		add_scene_btn = QPushButton(self)
		add_scene_btn.setText("+")

		remove_scene_btn = QPushButton(self)
		remove_scene_btn.setText("-")

		build_btn = QPushButton(self)
		build_btn.setText("Build game")

		save_btn = QPushButton(self)
		save_btn.setText("Save")

		name = QLabel(self)
		name.setText("Editing " + self.name)
		authors = QLabel(self)
		authors.setText("Made by " + self.author)

		scenes_widget = QListWidget(self)
		scenes_widget.insertItem(0, "Scene 1")
		scenes_widget.insertItem(1, "Scene 2")
		scenes_widget.insertItem(2, "Scene 3")

		lists.append(scenes_widget)

		labels.append(name)
		labels.append(authors)

		buttons.append(add_scene_btn)
		buttons.append(remove_scene_btn)
		buttons.append(build_btn)
		buttons.append(save_btn)

		layout = QVBoxLayout(self)


		self.setStyleSheet('background-color: rgb(37, 37, 37);')
		for i in labels:
			i.setStyleSheet('color: white; font-size: 16px;')
			i.adjustSize()

		for i in lists:
			i.setStyleSheet('color: white; background-color: gray; font-size: 18px;')
			i.adjustSize()

		for i in buttons:
			i.setStyleSheet('color: white; background-color: gray; font-size: 16px; border: 1px solid gray;')
			i.adjustSize()
			i.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

		name.move(10, 5)
		authors.move(10, 29)
		scenes_widget.move(1810, 10)
		scenes_widget.setFixedSize(100, 1000)
		add_scene_btn.move(1877, 1020)
		add_scene_btn.setStyleSheet('color: white; background-color: rgb(59, 171, 130); font-size: 16px; border: 1px solid rgb(59, 171, 130);')
		add_scene_btn.setFixedSize(32, 32)

		remove_scene_btn.move(1810, 1020)
		remove_scene_btn.setStyleSheet('color: white; background-color: rgb(179, 0, 0); font-size: 16px; border: 1px solid rgb(179, 0, 0);')
		remove_scene_btn.setFixedSize(32, 32)

		save_btn.move(10, 1020)
		save_btn.setFixedSize(60, 40)
		build_btn.move(80, 1020)
		build_btn.setFixedSize(100, 40)

		self.setLayout(layout)


if __name__ == "__main__":
	app = QApplication(sys.argv)

	window = Editor("test", "JX_Snack", "out/")
	window.show()

	app.exec()
