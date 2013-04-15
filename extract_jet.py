#!/usr/bin/env python3

# Use this script to extract a text dictionary from .dex binary file.
# You need numpy installed.

# To generate your own dictionary from a list of txt dictionaries you
# could otherwise run :
# cat *.txt | iconv -f utf8 -t ascii//TRANSLIT | tr '[a-z]' '[A-Z]' | sed '/[^a-z]/d' | sort | uniq

# The reverse-engineered structure of Ruzzle's .dex files is as follows:
#
# == Header ==
# 4 bytes : always "WBDF" (maybe a file signature)
# 4 bytes : the file size (in bytes) minus the 8 header bytes
# 
# == Trie Node Format ==
# Each node is 4 byte long.
# 
# The first byte is the upper-case ASCII letter.
# The second is made of two nibbles :
#      * The high order nibble is a bitfield with the following flags:
#           - 0x10 if this node is the end of a valid word.
#           - 0x20 if this node is the last child of its parent.
#      * The low order nibble is the high order part of the child index.
# The last two bytes are the lower part of the child index.
# The child index is counted from the end of the header.
# An index of 0 means that the node does not have any child.
# The offset of the child from the first byte of the file is 8 + 4 * index.
# 
# == Trie Format ==
# After the header the file is just list of nodes.
#
# The first node is always the null character (0x00) with both flags set.
# The reason might be that C strings need a null character at the end.
#
# The second node is most likely 'A', the first letter of the first word.
# All other nodes can be reached by following the siblings and children
# of this node.


from numpy import *


def explore(input_f, output_f, index, partial_word):
	letter = chr(input_f[index * 4])
	
	if input_f[index * 4 + 1] & 0x10: # This node is a valid word.
		output_f.write(partial_word + letter + '\n')
	
	child_index = (input_f[index * 4 + 1] & 0x0F) * 256 * 256 \
	             + input_f[index * 4 + 2] * 256 \
	             + input_f[index * 4 + 3]
	
	if child_index == 0:
		pass # This node does not have any child.
	else:
		explore(input_f, output_f, child_index, partial_word + letter)
	
	if input_f[index * 4 + 1] & 0x20:
		pass # This node does not have any more sibling.
	else:
		explore(input_f, output_f, index + 1, partial_word)


def main(input_path, output_path):
	input_f = fromfile(input_path, 'u1') # read all bytes
	input_f = input_f[8:] # discard header
	
	output_f = open(output_path, 'w')
	explore(input_f, output_f, 1, '') # start from the second node


if __name__ == '__main__':
    main('fr.jet',
         'fr.txt')
