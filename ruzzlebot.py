#!/usr/bin/env python

# You need ADB in your PATH ('tools' folder from the Android SDK).
# PIL isn't compatible with python 3 yet.


import os
from PIL import Image, ImageFilter
import re
from socket import *
import sys
import time
import zipfile


def ord_compat(x):
    if sys.version < '3':
        return ord(x)
    else:
        return x
def chr_compat(x):
    if sys.version < '3':
        return x
    else:
        return chr(x)


try:
    from StringIO import StringIO # Python 2
except ImportError:
    from io import StringIO


try:
    input = raw_input
except NameError:
    pass # Python 2


SCORES = { 'A':  1, 'B':  3, 'C':  3, 'D':  2, 'E':  1, 'F':  4, 'G':  2,
           'H':  4, 'I':  1, 'J':  8, 'K': 10, 'L':  2, 'M':  2, 'N':  1,
           'O':  1, 'P':  3, 'Q':  8, 'R':  1, 'S':  1, 'T':  1, 'U':  1,
           'V':  5, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10 }

COLORS = [ (236, 237, 236, (1, 1)), # R, G, B, bonus (L, W)
           (45,  169,  36, (2, 1)),
           (55,  122, 180, (3, 1)),
           (241, 199,  88, (1, 2)),
           (228,  71,  71, (1, 3)) ]


def adb_command(cmd):
    return os.popen('adb %s' % cmd, 'r').read()


def open_dictionary(language):
    dictionary_path = 'assets/dictionaries/%s.jet' % language
    
    if not os.path.exists(dictionary_path):
        print('Downloading APK...')
        apk_path = adb_command('shell pm path se.maginteractive.rumble.free').split(':')[1].strip()
        adb_command('pull %s ruzzle.apk' % apk_path)
        
        print('Extracting dictionary...')
        zf = zipfile.ZipFile('ruzzle.apk')
        zf.extract(dictionary_path)
    
    return open(dictionary_path, 'rb')


def monkey_connect():
    port = 12345
    adb_command('root')
    adb_command('forward tcp:%d tcp:%d' % (port, port))
    adb_command('shell monkey --port %d' % port)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('127.0.0.1', port))
    
    return sock.makefile('rw')


def monkey_command(sock, cmd):
    sock.write(cmd + '\n')
    sock.flush() # It's a file, not a socket, so it needs to be flushed.
    
    response = sock.readline()
    if response.startswith('OK'):
        return response[3:-1]
    else:
        raise IOError(response)


def monkey_getvar(sock, var):
    return int(monkey_command(sock, 'getvar %s' % var))


def get_screenshot():
    png = adb_command('shell screencap -p')
    png = png.replace('\r\n', '\n') # ADB inserts carriage returns.
    
    return Image.open(StringIO(png))


def process_screen():
    img = get_screenshot()
    img = img.filter(ImageFilter.BLUR)
    img = img.filter(ImageFilter.BLUR)
    
    red = img.split()[0]
    red = red.point(lambda i: (i > 150) * 255) # Threshold on red channel.
    
    cell = img.size[0] / 4 # Estimated dimension.
    try:
        top  = [cell / 2, img.size[1] / 4]
        while red.getpixel(tuple(top)) == 0:
            top[1] += 1 # Move down until reaching the first cell.
        
        left = [0, top[1] + cell / 2]
        while red.getpixel(tuple(left)) == 0:
            left[0] += 1 # Move right.
    except IndexError:
        print("Error: Ruzzle is not running.")
        sys.exit()
    
    cell    = ((img.size[0] - left[0]) / 4,
               cell)
    corner  = (left[0] + cell[0] / 2, top[1] + cell[1] / 2) # Center of the first cell.
    bonuses = [[(1, 1)] * 4 for j in range(4)]

    pixels = img.load()
    for i in range(4):
        for j in range(4):
            rgba = pixels[corner[0] + (j - .45) * cell[0],
                          corner[1] + (i - .45) * cell[1]]
            
            pixels[corner[0] + (j - .45) * cell[0],
                   corner[1] + (i - .45) * cell[1]] = (0, 0, 0, 255) # Debug.
            
            m = min(COLORS, key=lambda (r, g, b, _):
                                    abs(rgba[0] - r)
                                  + abs(rgba[1] - g)
                                  + abs(rgba[2] - b))
            
            bonuses[i][j] = m[3]
            sys.stdout.write({ (1, 1): " []",
                               (2, 1): " DL",
                               (3, 1): " TL",
                               (1, 2): " DW",
                               (1, 3): " TW"  }[m[3]]); # Display the bonuses.
        print('')
    
    return (cell, corner, bonuses)


def input_board():
    clean = []
    while len(clean) < 16:
        clean += re.findall('[A-Z]', input().upper())

    return [[clean[i + j * 4] for i in range(4)] for j in range(4)]


def explore(board, input_f, index, i, j, current_path, paths):
    if i < 0 or i >= 4 or j < 0 or j >= 4:
        return

    if (i, j) in current_path:
        return

    letter = board[i][j]
    
    # Try to find a sibling with this letter.
    while True:
        if chr_compat(input_f[index * 4]) == letter:
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
    def __init__(self, board, bonuses, path):
        word = ''
        score = 0
        multi = 1
        for (i, j) in path:
            word += board[i][j]
            score += bonuses[i][j][0] * SCORES[board[i][j]]
            multi *= bonuses[i][j][1]
        
        self.path = path
        self.word = word
        self.score = score * multi
        
        if len(word) >= 5:
            self.score += 5 * (len(word) - 4)


def type_solution(sock, cell, corner, solution):
    last_coords = False
    
    for (i, j) in solution.path:
        new_coords = (corner[0] + j * cell[0],
                      corner[1] + i * cell[1])
        
        if not last_coords:
            monkey_command(sock, 'touch down %d %d' % new_coords)
        else:
            monkey_command(sock, 'touch move %d %d' % new_coords)
        
        last_coords = new_coords
    
    time.sleep(.15)
    monkey_command(sock, 'touch up %d %d' % last_coords)


def main():
    print('Waiting for a phone...')
    adb_command('wait-for-device')
    
    f = open_dictionary('fr')
    print('Reading dictionary...')
    input_f = f.read()[8:] # Skip the header.
    f.close()
    
    print('What are the 16 letters?')
    board = input_board()
    
    print('Exploring board...')
    paths = []
    for i in range(4):
        for j in range(4):
            explore(board, input_f, 1, i, j, [], paths)
    print('=> Found %d solutions' % len(paths))
    
    print('Launching monkey...')
    sock = monkey_connect()
    
    print('Processing screen...')
    (cell, corner, bonuses) = process_screen()
    
    print('Sorting...')
    solutions = []
    for path in paths:
        solutions.append(Solution(board, bonuses, path))
    solutions = sorted(solutions, key=lambda solution: -solution.score)
    
    print('Playing...')
    words = set()
    score = 0
    for solution in solutions:
        if solution.word in words:
            continue # Skip duplicates.
        
        words.add(solution.word)
        
        sys.stdout.write(solution.word)
        sys.stdout.write(':%d ' % solution.score)
        sys.stdout.flush()
        type_solution(sock, cell, corner, solution)
        score += solution.score
    print('\n=> Total score of %d\nDone.' % score)


if __name__ == '__main__':
    main()
