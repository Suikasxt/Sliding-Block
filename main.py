#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import random
import subprocess
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, Qt

waitTime = 10**6
animateTime = 3*10**5
Worker = 'algorithm\work.exe'
Size = 150
MaxSize = 800

class QLabelCenter(QLabel):
	def __init__(self, text = ''):
		super().__init__(text)
		self.setAlignment(Qt.AlignCenter)
	
class myEdit(QWidget):
	def __init__(self, label, text, type = 0):
		super().__init__()
		
		hlayout = QHBoxLayout()
		self.setLayout(hlayout)
		
		self.label = QLabelCenter(label)
		if type == 0:
			self.edit = QLineEdit(text)
		elif type == 1:
			self.edit = QTextEdit(text)
		hlayout.addWidget(self.label, 1)
		hlayout.addWidget(self.edit, 3)

class block(QWidget):
	pushSign = pyqtSignal(int)
	def __init__(self, parent, number, size):
		super().__init__(parent)
		self.number = number
		layout = QHBoxLayout()
		self.setLayout(layout)
		layout.addWidget(QLabelCenter(str(number)))
		self.setFixedSize(size, size)
	def mousePressEvent(self, QMouseEvent):
		self.pushSign.emit(self.number)
	
class moveThread(QThread):
	blockMoveSign = pyqtSignal(float)
		
	def __init__(self, parent, speed):
		super(moveThread, self).__init__(parent)
		self.speed = speed
	def run(self):
		T = 30
		for i in range(T):
			self.blockMoveSign.emit((i+1)/T)
			self.usleep(int(animateTime/T/self.speed))

class gameWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.widgets = []
	
	def initUI(self, width, height, state):
		for w in self.widgets:
			if w:
				w.setParent(None)
		self.widthNumber = width
		self.heightNumber = height
		self.state = state
		self.widgets = [None] * (width*height)
		self.animate = [None] * (width*height)
		
		if (Size*max(width, height) < MaxSize):
			size = Size
		else:
			size = MaxSize//max(width, height)
		self.blockSize = size
		self.setFixedSize(size*width, size*height)
		
		
		positions = [(i, j) for i in range(height) for j in range(width)]
		for position, number in zip(positions, state):
			if number!=0:
				item = block(self, number, size)
				item.pushSign.connect(self.blockMove)
				item.show()
				item.move(position[1]*size, position[0]*size)
				self.widgets[position[0] * width + position[1]] = item
		
	def blockMove(self, number, speed=1):
		for i in range(self.widthNumber * self.heightNumber):
			if self.state[i] == number:
				pos = i
			elif self.state[i] == 0:
				pos0 = i
		if (abs(pos//self.widthNumber - pos0//self.widthNumber) + abs(pos%self.widthNumber - pos0%self.widthNumber) > 1):
			return
		
		w = self.widgets[pos]
		def blockMoveAnimate(p):
			#print(p)
			w.move((pos%self.widthNumber*(1-p) + pos0%self.widthNumber*p) * self.blockSize,
						(pos//self.widthNumber*(1-p) + pos0//self.widthNumber*p) * self.blockSize)
						
		if (self.animate[number]):
			self.animate[number].terminate()
		self.animate[number] = moveThread(self, speed)
		self.animate[number].blockMoveSign.connect(blockMoveAnimate)
		self.animate[number].start()
		self.widgets[pos], self.widgets[pos0] = (self.widgets[pos0], self.widgets[pos])
		self.state[pos], self.state[pos0] = (self.state[pos0], self.state[pos])

class solvingThread(QThread):
	gameMoveSign = pyqtSignal(int, float)
	resultSign = pyqtSignal(int, int)
	
	def __init__(self, parent, width, height, state, speed):
		super(solvingThread, self).__init__(parent)
		self.width = width
		self.height = height
		self.state = state
		self.speed = speed
		
	def run(self):
		self.worker = subprocess.Popen(Worker, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		self.worker.stdin.write((str(self.height) + ' ' + str(self.width) + '\n').encode(encoding='utf-8'))
		for x in self.state:
			self.worker.stdin.write((str(x) + ' ').encode(encoding='utf-8'))
		self.worker.stdin.write('\n'.encode(encoding='utf-8'))
		self.worker.stdin.flush()
		stepNumber = 0
		timeUsed = 0
		while (True):
			try:
				self.usleep(int(waitTime/self.speed))
				res = self.worker.stdout.readline().decode('utf-8')
				if (res[0] == 'O'):
					result = res.split()
					try:
						stepNumber = int(result[1])
						timeUsed = int(result[2])
					except:
						pass
					break
				self.gameMoveSign.emit(int(res), self.speed)
			except:
				break
		self.resultSign.emit(stepNumber, timeUsed)
		self.worker.terminate()
		
class myGridEdit(QWidget):
	def __init__(self, width, height, state):
		super().__init__()
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.myWidget = []
		self.setState(width, height, state)
	
	def setState(self, width, height, state):
		for w in self.myWidget:
			if w:
				w.setParent(None)
		self.myWidget = []
		for i in range(height):
			for j in range(width):
				edit = QLineEdit(str(state[i*width+j]))
				self.grid.addWidget(edit, *(i,j))
				self.myWidget.append(edit)
	def getState(self):
		res = []
		for w in self.myWidget:
			res.append(int(w.text()))
		return res
		
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
			self.speed = float(self.speedEdit.edit.text())
			if stateCheck:
				self.state = self.stateEdit.getState()
				
				assert len(self.state) == self.width*self.height
				tmp = self.state.copy()
				tmp.sort()
				for i in range(self.width*self.height):
					assert i == tmp[i]
			return True
		except:
			QMessageBox.information(self, 'Error', 'Data Error.')
			return False
	def resultChange(self, stepNumber, timeUsed):
		self.resultLabel.setText('StepNumber: ' + str(stepNumber) + '  Time: ' + str(timeUsed/1000) + 's')
		
	def solve(self):
		if (self.solving):
			self.solveButton.setText('Solve')
			self.thread.worker.terminate()
			self.thread.terminate()
			return
			
		if (not self.update()):
			return
		self.thread = solvingThread(self, self.width, self.height, self.state, self.speed)
		self.thread.started.connect(self.threadStart)
		self.thread.finished.connect(self.threadStop)
		self.thread.resultSign.connect(self.resultChange)
		self.thread.gameMoveSign.connect(self.game.blockMove)
		self.thread.start()
		
	def threadStart(self):
		self.solving = True
		self.solveButton.setText('Stop')
	def threadStop(self):
		self.solving = False
		self.solveButton.setText('Solve')
		
		
	
	def update(self):
		if (self.getParameter()):
			self.game.initUI(self.width, self.height, self.state)
			return True
		return False
	
	def setRandomState(self):
		if (not self.getParameter(False)):
			return
		self.stateEdit.setState(self.width, self.height, self.getRandomState(self.width, self.height))
		return self.update()
	
	
	def initUI(self):
		vlayout = QVBoxLayout()
		self.setLayout(vlayout)
		
		self.widthEdit = myEdit('Width', '3')
		self.heightEdit = myEdit('Height', '3')
		self.speedEdit = myEdit('Speed', '3')
		self.stateEdit = myGridEdit(3, 3, self.getRandomState(3, 3))
		self.resultLabel = QLabelCenter('')
		self.solveButton = QPushButton('Solve')
		self.solveButton.clicked.connect(self.solve)
		self.stateButton = QPushButton('Generate Random State')
		self.stateButton.clicked.connect(self.setRandomState)
		self.updateButton = QPushButton('Update')
		self.updateButton.clicked.connect(self.update)
		
		vlayout.addWidget(self.widthEdit)
		vlayout.addWidget(self.heightEdit)
		vlayout.addWidget(self.speedEdit)
		vlayout.addWidget(self.stateEdit)
		vlayout.addWidget(self.resultLabel)
		vlayout.addWidget(self.solveButton)
		vlayout.addWidget(self.stateButton)
		vlayout.addWidget(self.updateButton)
		
		self.update()
		
		

class mainContent(QWidget):
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
		
		
class mainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setCentralWidget(mainContent())
		file = open('main.qss', 'r')
		self.setStyleSheet(file.read())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = mainWindow()
    w.show()
    sys.exit(app.exec_())