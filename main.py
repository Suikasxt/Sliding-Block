#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import random
import subprocess
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread

Worker = 'algorithm\work.exe'

class gameWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.grid = QGridLayout()
		self.widgets = []
		self.setLayout(self.grid)
	
	def initUI(self, width, height, state):
		for w in self.widgets:
			w.setParent(None)
		self.widgets = []
		
		positions = [(i, j) for i in range(width) for j in range(height)]
		for position, number in zip(positions, state):
			if number!=0:
				button = QPushButton(str(number))
				self.grid.addWidget(button, *position)
				self.widgets.append(button)

class myEdit(QWidget):
	def __init__(self, label, text, type = 0):
		super().__init__()
		
		hlayout = QHBoxLayout()
		self.setLayout(hlayout)
		
		self.label = QLabel(label)
		if type == 0:
			self.edit = QLineEdit(text)
		elif type == 1:
			self.edit = QTextEdit(text)
		hlayout.addWidget(self.label, 1)
		hlayout.addWidget(self.edit, 3)

class solvingThread(QThread):
	gameMove = pyqtSignal(int, int, list)
	
	def __init__(self, parent, width, height, state):
		super(solvingThread, self).__init__(parent)
		self.width = width
		self.height = height
		self.state = state
		
	def run(self):
		self.worker = subprocess.Popen(Worker, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		self.worker.stdin.write((str(self.width) + ' ' + str(self.height) + '\n').encode(encoding='utf-8'))
		for x in self.state:
			self.worker.stdin.write((str(x) + ' ').encode(encoding='utf-8'))
		self.worker.stdin.write('\n'.encode(encoding='utf-8'))
		self.worker.stdin.flush()
		while (True):
			try:
				self.sleep(1)
				res = self.worker.stdout.readline().decode('utf-8')
				print(res)
				if (res[0] == 'O'):
					break
				self.gameMove.emit(self.width, self.height, [int(x) for x in res.split()])
			except:
				break
		
		self.worker.terminate()
				
class tools(QWidget):
	def __init__(self, game):
		super().__init__()
		self.game = game
		self.solving = False
		self.initUI()
	
	def getRandomState(self, width, height):
		res = [x for x in range(width*height)]
		random.shuffle(res)
		return res
		
	def getParameter(self, stateCheck = True):
		if (self.solving):
			return False
		try:
			self.width = int(self.widthEdit.edit.text())
			self.height = int(self.heightEdit.edit.text())
			if stateCheck:
				self.state = [int(x) for x in self.stateEdit.edit.toPlainText().split(',')]
				
				assert len(self.state) == self.width*self.height
				tmp = self.state.copy()
				tmp.sort()
				for i in range(self.width*self.height):
					assert i == tmp[i]
			return True
		except:
			QMessageBox.information(self, 'Error', 'Data Error.')
			return False
	def solve(self):
		if (self.solving):
			self.solveButton.setText('Solve')
			self.thread.terminate()
			return
			
		if (not self.update()):
			return
		self.thread = solvingThread(self, self.width, self.height, self.state)
		self.thread.started.connect(self.threadStart)
		self.thread.finished.connect(self.threadStop)
		self.thread.gameMove.connect(self.game.initUI)
		self.thread.start()
		self.solveButton.setText('Stop')
		
	def threadStart(self):
		self.solving = True
	def threadStop(self):
		self.solving = False
		
		
	
	def update(self):
		if (self.getParameter()):
			self.game.initUI(self.width, self.height, self.state)
			return True
		return False
	
	def setRandomState(self):
		if (not self.getParameter(False)):
			return
		self.stateEdit.edit.setPlainText(', '.join(str(x) for x in self.getRandomState(self.width, self.height)))
		return self.update()
	
	
	def initUI(self):
		vlayout = QVBoxLayout()
		self.setLayout(vlayout)
		
		self.widthEdit = myEdit('Width', '3')
		self.heightEdit = myEdit('Height', '3')
		self.stateEdit = myEdit('State', ', '.join(str(x) for x in self.getRandomState(3, 3)), 1)
		self.solveButton = QPushButton('Solve')
		self.solveButton.clicked.connect(self.solve)
		self.stateButton = QPushButton('Generate Random State')
		self.stateButton.clicked.connect(self.setRandomState)
		self.updateButton = QPushButton('Update')
		self.updateButton.clicked.connect(self.update)
		
		vlayout.addWidget(self.widthEdit)
		vlayout.addWidget(self.heightEdit)
		vlayout.addWidget(self.stateEdit)
		vlayout.addWidget(self.solveButton)
		vlayout.addWidget(self.stateButton)
		vlayout.addWidget(self.updateButton)
		
		self.update()
		
		

class mainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
	
	def initUI(self):
		hlayout = QHBoxLayout()
		self.setLayout(hlayout)
		
		self.game = gameWidget()
		self.tools = tools(self.game)
		hlayout.addWidget(self.game)
		hlayout.addWidget(self.tools)
		self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = mainWindow()
    w.show()
    sys.exit(app.exec_())