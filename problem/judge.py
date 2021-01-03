import os
import sys
import time
import random
import argparse
import threading
import subprocess

TimeLimit = 10
outputLimit = 10**5

def getData(path):
	#根据路径读取数据
	file = open(path, 'r')
	Height, Width = [int(x) for x in file.readline().split()]
	State = [int(x) for x in file.readline().split()]
	file.close()
	return Height, Width, State

def judgeAnswer(H, W, S, a):
	#根据选手输出判断其得分，选手的每个操作代表想要移动的方块的数字（应当在0旁边）
	score = 0
	for ope in a:
		#遍历选手的每个操作，执行一个操作先扣掉一分
		score -= 1
		#判断一下操作是否合法
		if ope <= 0 or ope > H*W:
			return 0, False
		#寻找一下当前0的位置和要移动方块的位置
		for i in range(H):
			for j in range(W):
				p = i*W+j
				if S[p] == 0:
					pos0 = (i,j,p)
				if S[p] == ope:
					pos = (i,j,p)
		#如果要移动方块在0的旁边，那就交换它们的位置
		if (abs(pos0[0] - pos[0]) + abs(pos0[1] - pos[1]) <= 1):
			S[pos0[2]], S[pos[2]] = S[pos[2]], S[pos0[2]]
		else:
			return 0, False
	
	#所有选手操作执行完毕，每个位置正确的方块可以获得100分
	for i in range(H*W-1):
		if (S[i] == i+1):
			score += 100
	return score, True
	
if __name__ == "__main__":
	#命令行参数设置，可以通过命令行输入ai可执行文件路径与数据路径
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-ai', '--ai', help="player's AI")
	args=parser.parse_args()
	path = os.getcwd()
	score = 0
	result = ''
	totalTime = 0

	for i in range(1):
		code = subprocess.Popen('./'+args.ai, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
		Height, Width, State = getData(os.path.join(path, '%02d.in'%(i)))
		answer = []
		def run():
			global answer
			count = 0
			code.stdin.write((str(Height) + ' ' + str(Width) + '\n'))
			code.stdin.write((' '.join([str(x) for x in State]) + '\n'))
			code.stdin.flush()
			while (count < outputLimit):
				count+=1
				try:
					res = code.stdout.readline()
					if (res[0] == 'O'):
						break
					answer.append(int(res))
				except:
					break
		th = threading.Thread(target=run)
		th.start()
		totalTime -= time.time()
		th.join(1)
		totalTime += time.time()


		resultNow = ''
		scoreNow, successful = judgeAnswer(Height, Width, State, answer)
		if successful:
			score += scoreNow
		else:
			status = code.poll()
			if (status == 0):
				resultNow = 'WrongAnswer'
			elif (status == None):
				resultNow = 'TimeLimitExceeded'
			else:
				resultNow = 'RuntimeError'
		code.kill()
		if (resultNow and result==''):
			result = resultNow
		
	if (result == ''):
		result = 'Accept'
	print(result, score, totalTime)
