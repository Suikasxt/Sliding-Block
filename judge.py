import sys
import time
import random
import argparse
import threading
import subprocess

TimeLimit = 10
outputLimit = 10**5

def getData(path):
	file = open(args.data, 'r')
	Height, Width = [int(x) for x in file.readline().split()]
	State = [int(x) for x in file.readline().split()]
	file.close()
	return Height, Width, State

def judgeAnswer(H, W, S, a):
	score = 0
	for ope in a:
		score -= 1
		if ope <= 0 or ope > H*W:
			continue
		for i in range(H):
			for j in range(W):
				p = i*W+j
				if S[p] == 0:
					pos0 = (i,j,p)
				if S[p] == ope:
					pos = (i,j,p)
		if (abs(pos0[0] - pos[0]) + abs(pos0[1] - pos[1]) <= 1):
			S[pos0[2]], S[pos[2]] = S[pos[2]], S[pos0[2]]
	
	for i in range(H*W-1):
		if (S[i] == i+1):
			score += 100
	return score
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('-ai', '--ai', help="player's AI")
	parser.add_argument('-d', '--data', help="Input data for test")
	args=parser.parse_args()

	
	Height, Width, State = getData(args.data)

	AI = subprocess.Popen(args.ai, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	AI.stdin.write((str(Height) + ' ' + str(Width) + '\n').encode(encoding='utf-8'))
	AI.stdin.write((' '.join([str(x) for x in State]) + '\n').encode(encoding='utf-8'))
	AI.stdin.flush()
	answer = []
	def AIwork():
		count = 0
		while (count < outputLimit):
			count+=1
			try:
				res = AI.stdout.readline().decode('utf-8')
				if (res[0] == 'O'):
					break
				answer.append(int(res))
			except:
				break
	
	th = threading.Thread(target=AIwork)
	start_time = time.time()
	th.start()
	th.join(timeout=TimeLimit)
	timeUsed = time.time() - start_time
	AI.terminate()
	
	print(judgeAnswer(Height, Width, State, answer))