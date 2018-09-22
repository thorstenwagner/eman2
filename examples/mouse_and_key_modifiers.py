from __future__ import print_function
from __future__ import division
from eman2_gui.PyQt import QtCore, QtGui

class MouseAndKeyModifiers(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		
		layout = QtGui.QVBoxLayout()
		label = QtGui.QLabel("Click here to test mouse buttons: Left, Right, Middle\nand keyboard modifiers: Ctrl, Alt, Shift, and Command (a Mac key)")
		self.text_browser = QtGui.QTextBrowser()
		layout.addWidget(label)
		layout.addWidget(self.text_browser)
		
		self.setLayout(layout)
	
	def mousePressEvent(self, event):
		self.text_browser.clear()
		self.text_browser.append("Mouse press info...")
		if event.buttons()&Qt.LeftButton:
			self.text_browser.append("Left Button")
		if event.buttons()&Qt.MidButton:
			self.text_browser.append("Middle Button")
		if event.buttons()&Qt.RightButton:
			self.text_browser.append("Right Button")
		if event.modifiers()&Qt.ShiftModifier:
			self.text_browser.append("Shift Modifier")
		if event.modifiers()&Qt.ControlModifier:
			#Apple/Command key on a Mac... NOT CONTROL KEY ON A MAC!
			self.text_browser.append("Control Modifier")
		if event.modifiers()&Qt.AltModifier:
			#Alt/Option key on a Mac. An EMAN convention is that Alt+Left click works like a middle click.
			self.text_browser.append("Alt Modifier")
		if event.modifiers()&Qt.MetaModifier:
			#Control Key on a Mac. A Mac convention is that Ctrl+Left Click works like a right click.
			self.text_browser.append("Meta Modifier")


if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	window = MouseAndKeyModifiers()
	window.show()
	window.raise_()
	sys.exit(app.exec_())
