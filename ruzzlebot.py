#!/usr/bin/env python2

# Make sure the 'tools' folder from your Android SDK is in the PATH for ADB
# TODO 0 solutions for python3

import sys
import re
import zipfile
import os
import time
from socket import *

# TODO http://www.pygtk.org/pygtk2tutorial/ch-GettingStarted.html
# import pygtk
# pygtk.require('2.0')
# import gtk

def ord_compat(x): # http://python3porting.com/problems.html#binary-data-in-python-2-and-python-3
    if sys.version < '3':
        return ord(x)
    else:
        return x


def adb_command(cmd): # https://github.com/rbrady/python-adb/blob/master/adb/utils.py
    return os.popen('adb %s' % cmd, 'r').read()


def open_dictionary(language):
    dictionary_path = 'assets/dictionaries/%s.jet' % language
    
    if not os.path.exists(dictionary_path):
        print('Downloading APK...')
        apk_path = adb_command('pm path se.maginteractive.rumble.free').split(':')[1].strip()
        adb_command('pull %s ruzzle.apk' % apk_path)
        
        print('Extracting dictionary...')
        zf = zipfile.ZipFile('ruzzle.apk')
        zf.extract(dictionary_path)
    
    return open(dictionary_path, 'rb')


def monkey_connect():
    port = 12345
    adb_command('forward tcp:%d tcp:%d' % (port, port))
    adb_command('shell monkey --port %d' % port)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('127.0.0.1', port))
    
    return sock.makefile('rw')


def monkey_command(sock, cmd):
    sock.write(cmd + '\n')
    sock.flush() # It's a file, not a socket, so it needs to be flushed.
    
    response = sock.readline()
    if response.startswith('OK:'):
        return response[3:-1]
    elif response.startswith('OK'):
        return True
    elif response.startswith('ERROR'):
        print(response)
        return False
    else:
        print('Unknown command')
        return False


def monkey_getvar(sock, var):
    return int(monkey_command(sock, 'getvar %s' % var))


SCORES = { 'A':  1, 'B':  3, 'C':  3, 'D':  2, 'E':  1, 'F':  4, 'G':  2,
           'H':  4, 'I':  1, 'J':  8, 'K': 10, 'L':  2, 'M':  2, 'N':  1,
           'O':  1, 'P':  3, 'Q':  8, 'R':  1, 'S':  1, 'T':  1, 'U':  1,
           'V':  5, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10  };


def get_board():
    # TODO line = MonkeyRunner.input('What are the letters?', 'ABCD EFGH IJKL MNOP')
    line = 'ABCD EFGH IJKL MNOP'
    clean = re.findall('[A-Z]', line.upper())

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
            current_path = list(current_path) # Cloning.
            current_path.append( (i, j) )

            if ord_compat(input_f[index * 4 + 1]) & 0x10: # This node is a valid word.
                paths.append(current_path)

            child_index = (ord_compat(input_f[index * 4 + 1]) & 0x0F) * 256 * 256 \
                     + ord_compat(input_f[index * 4 + 2]) * 256 \
                     + ord_compat(input_f[index * 4 + 3])

            if child_index != 0:
                for a in [-1, 0, 1]:
                    for b in [-1, 0, 1]:
                        explore(board, input_f, child_index, i + a, j + b, current_path, paths)
            break

        if ord_compat(input_f[index * 4 + 1]) & 0x20:
            break # This node does not have any more sibling.

        index += 1


class Solution:
    pass


def type_solution(sock, screen_size, solution):
    last_coords = False
    solution.path = [(0, 0), (0, 3), (3, 3), (3, 0)]
    for (i, j) in solution.path:
        new_coords = (screen_size[0] / 8 * (2 * i + 1),
                      screen_size[0] / 8 * (2 * j - 3) + screen_size[1] / 2)
        
        if not last_coords:
            monkey_command(sock, 'touch down %d %d' % new_coords)
        else:
            monkey_command(sock, 'touch move %d %d' % new_coords)
        
        last_coords = new_coords
    
    time.sleep(1)
    monkey_command(sock, 'touch up %d %d' % last_coords)


def main():
    f = open_dictionary('fr')
    print('Reading dictionary...')
    input_f = f.read()
    input_f = input_f[8:] # Skip the header.
    f.close()
    
    print('Getting board...')
    board = get_board()
    
    print('Exploring board...')
    paths = []
    for i in range(4):
        for j in range(4):
            explore(board, input_f, 1, i, j, [], paths)
    print(' Found %d solutions' % len(paths))
    
    
    print('Waiting for device...')
    adb_command('wait-for-device')
    
    print('Launching monkey...')
    # TODO MonkeyRunner.waitForConnection()
    sock = monkey_connect()
    screen_size = (monkey_getvar(sock, 'display.width'),
                   monkey_getvar(sock, 'display.height'))
    
# TODO   pic = device.takeSnapshot()
#        pic.writeToFile('screenshot.png','png')

    print('Sorting...')
    solutions = []
    for path in paths:
        solution = Solution()
        solution.path = path
        solution.word = ''.join([board[i][j] for (i,j) in path])
        solution.score = len(solution.word) #TODO
        solutions.append(solution)
    solutions = sorted(solutions, key=lambda sol: -sol.score)
    
    print('Playing...')
    words = set()
    for solution in solutions:
        if solution.word in words:
            continue # Skip duplicates.

        words.add(solution.word)
        
        sys.stdout.write(' ' + solution.word)
        sys.stdout.flush()
        type_solution(sock, screen_size, solution)
    print('\nDone.')
    

if __name__ == '__main__':
    main()
