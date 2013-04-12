#!/usr/bin/env monkeyrunner

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from collections import defaultdict


def build_dict():
	root = tree()
	
	f = open('dict.txt', 'r')
	for word in f:
		word = word.strip()
		if len(word) > 0:
			insert_word(root, word)
	f.close()
	
	return root


def tree():
	return defaultdict(tree)


def insert_word(branch, word):
	if not word:
		branch['valid'] = True
	else:
		insert_word(branch[word[0]], word[1:])


def get_board():
	str = MonkeyRunner.input('What are the letters?', 'XXXX XXXX XXXX XXXX').lower()
	
	board = [[''] * 4 for i in range(4)]
	i = 0
	j = 0
	for letter in str:
		if letter.isalpha():
			board[i][j] = letter
			i += 1
			if i >= 4:
				i = 0
				j += 1
	
	if i <> 0 or j <> 4:
		print("Wrong number of letters!") # TODO fail
	
	return board


class solution:
	path = []
	score = 0
	word = ''


def search_branch(board, solutions, branch, i, j, partial_word = '', partial_path = [], partial_score = 0, partial_multiplier = 1):
	if i < 0 or i >= 4 or j < 0 or j >= 4:
		return

	if (i, j) in partial_path:
		return
	
	branch = branch[board[i][j]]
	if not branch:
		return

	partial_word += board[i][j]
	partial_path = list(partial_path) # clone it
	partial_path.append( (i, j) )
	partial_score += 1; # TODO
	partial_multiplier *= 1; # TODO

	if branch['valid']:
		s = solution()
		s.word = partial_word
		s.path = partial_path
		s.score = partial_score * partial_multiplier # TODO    bonus = (word.length() - 4 ) * 5; // Bonus de longueur.
		solutions.append(s)

	for a in [-1, 0, 1]:
		for b in [-1, 0, 1]:
			search_branch(board, solutions, branch, i + a, j + b, partial_word, partial_path, partial_score, partial_multiplier)


def main():
	board = get_board()
	
	root = build_dict()
	solutions = []
	for i in range(4):
		for j in range(4):
			search_branch(board, solutions, root, i, j)
	
	for s in solutions:
		print(s.word)
	
#	device = MonkeyRunner.waitForConnection()
#	pic = device.takeSnapshot()
#	pic.writeToFile('screenshot.png','png')


if __name__ == '__main__':
    main()

# ABCD EFGH IJKL MNOP
