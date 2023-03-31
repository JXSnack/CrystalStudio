# This file is made to add missing features from PyQt that we need in CrystalStudio

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class ClickableLineEdit(QLineEdit):
	clicked = pyqtSignal()  # emit signal when clicked

	def mousePressEvent(self, event: QMouseEvent) -> None:
		if event.button() == Qt.MouseButton:
			self.clicked.emit()
		else:
			super().mousePressEvent(event)
