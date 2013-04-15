#!/usr/bin/env python

import fileinput
import re
from unidecode import unidecode

def main():
	dict = []
	for line in fileinput.input():
		word = unidecode(line.strip()).lower()
		if re.search("[^a-z]", word):
			continue
		
		if len(word) < 2 or len(word) > 16:
			continue
		
		dict.append(word)
	
	print("\n".join(sorted(set(dict))))


if __name__ == "__main__":
    main()
