#!/usr/bin/env monkeyrunner

# Install jython
# Make sure the "tools" folder from your Android SDK is in the PATH


import re
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from com.android.monkeyrunner.MonkeyDevice import *


SCORES = { 'A':  1, 'B':  3, 'C':  3, 'D':  2, 'E':  1, 'F':  4, 'G':  2,
           'H':  4, 'I':  1, 'J':  8, 'K': 10, 'L':  2, 'M':  2, 'N':  1,
           'O':  1, 'P':  3, 'Q':  8, 'R':  1, 'S':  1, 'T':  1, 'U':  1,
           'V':  5, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10  };


def get_board():
	line = MonkeyRunner.input('What are the letters?', 'ABCD EFGH IJKL MNOP').upper()
	clean = re.findall('[A-Z]', line)
	
	return [[clean[i + j * 4] for i in range(4)] for j in range(4)]


def explore(board, input_f, index, i, j, current_path, paths):
	if i < 0 or i >= 4 or j < 0 or j >= 4:
		return
	
	if (i, j) in current_path:
		return
	
	letter = board[i][j]
	
	# Try to find a sibling with this letter.
	while True:
		if input_f[index * 4] == letter:
			current_path = list(current_path) # cloning
			current_path.append( (i, j) )
			
			if ord(input_f[index * 4 + 1]) & 0x10: # This node is a valid word.
				paths.append(current_path)
			
			child_index = (ord(input_f[index * 4 + 1]) & 0x0F) * 256 * 256 \
			             + ord(input_f[index * 4 + 2]) * 256 \
			             + ord(input_f[index * 4 + 3])
			
			if child_index <> 0:
				for a in [-1, 0, 1]:
					for b in [-1, 0, 1]:
						explore(board, input_f, child_index, i + a, j + b, current_path, paths)
			break
		
		if ord(input_f[index * 4 + 1]) & 0x20:
			break # This node does not have any more sibling.
		
		index += 1


class Solution:
	pass


def main():
	print("Reading dictionary...")
	f = open('fr.jet', 'r')
	input_f = f.read()
	input_f = input_f[8:]
	f.close()
	
	print("Getting board...")
	board = get_board()
	
	print("Searching...")
	paths = []
	for i in range(4):
		for j in range(4):
			explore(board, input_f, 1, i, j, [], paths)
	
	print("Connecting...")
	device = MonkeyRunner.waitForConnection()
	# TODO print" package:%s" % device.getProperty('am.current.package')
	
#	pic = device.takeSnapshot()
#	pic.writeToFile('screenshot.png','png')
	
	print("Sorting...")
	solutions = []
	for path in paths:
		solution = Solution()
		solution.path = path
		solution.word = ''.join([board[i][j] for (i,j) in path])
		solution.score = len(solution.word) #TODO
		solutions.append(solution)
	solutions = sorted(solutions, key=lambda sol: -sol.score)
	
	print("Playing...")
	width = device.getProperty('display.width')
	height = device.getProperty('display.height')
	words = set()
	for solution in solutions:
		if solution.word in words:
			continue # Skip duplicates.
		
		words.add(solution.word)
		print(solution.word)
		
		for (i, j) in solution.path:
			x = 50 + i * 50
			y = 200 + j * 50
			device.touch(x, y, DOWN)
			MonkeyRunner.sleep(.5)
		device.touch(x, y, UP) # TODO drag?


if __name__ == '__main__':
    main()
