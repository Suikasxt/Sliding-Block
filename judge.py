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
	file = open(args.data, 'r')
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
			continue
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
	
	#所有选手操作执行完毕，每个位置正确的方块可以获得100分
	for i in range(H*W-1):
		if (S[i] == i+1):
			score += 100
	return score
	
if __name__ == "__main__":
	#命令行参数设置，可以通过命令行输入ai可执行文件路径与数据路径
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-ai', '--ai', help="player's AI")
	parser.add_argument('-d', '--data', help="Input data for test")
	args=parser.parse_args()

	#从提供的数据路径读取数据（长、宽、初始地图状态）
	Height, Width, State = getData(args.data)

	#用subprocess模块启动ai可执行文件，规定标准输入输出通道
	AI = subprocess.Popen(args.ai, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	#把地图大小、初始状态写入ai程序，并刷新其输入缓冲区
	AI.stdin.write((str(Height) + ' ' + str(Width) + '\n').encode(encoding='utf-8'))
	AI.stdin.write((' '.join([str(x) for x in State]) + '\n').encode(encoding='utf-8'))
	AI.stdin.flush()
	answer = []
	
	#读取ai输出的过程，写成过程方便线程调用
	def AIwork():
		#count用来记录选手输出的数量，免得输出太多把裁判程序搞炸
		count = 0
		while (count < outputLimit):
			count+=1
			#用try来处理使得如果选手输出不合法，这边没办法转成数字，就直接退出
			#务必善用try避免裁判程序会因为选手程序不合法而崩溃
			try:
				#读取一行
				res = AI.stdout.readline().decode('utf-8')
				#如果是O开头（其实就是Over）就结束
				if (res[0] == 'O'):
					break
				#否则转成数字塞进int里面
				answer.append(int(res))
			except:
				break
	
	#开启一个监听ai输出的线程
	th = threading.Thread(target=AIwork)
	#记录选手程序用的时间
	start_time = time.time()
	#线程启动，并等待线程结束（即选手输出结束），设置timeout如果选手程序运行时间过长就强行终止
	th.start()
	th.join(timeout=TimeLimit)
	timeUsed = time.time() - start_time
	AI.terminate()
	
	#获取选手得分并输出
	score = judgeAnswer(Height, Width, State, answer)
	print(score, timeUsed)