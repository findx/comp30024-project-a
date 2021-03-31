"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
import numpy as np
import time
import itertools

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing, hex_direction, hex_distance

def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).

    #All possible operators for each piece.
    moves = [(1,-1), (1,0), (0,1), (-1,1), (-1,0), (0,-1)]

    upper = data['upper']
    lower = data['lower']
    block = data['block']

    #reformatting data from ('p', x, y) -> ('p', (x, y))
    new_upper = []
    for each in data['upper']:
        new_upper.append((each[0],(each[1],each[2]))) #perhaps make coords np.array
    
    data['upper'] = new_upper

    new_lower = []
    for each in data['lower']:
        new_lower.append((each[0],(each[1],each[2])))
    
    data['lower'] = new_lower

    #changing format of data['block'] as '' is not necessary.
    blocks = []
    for cell in block:
        blocks.append((cell[1], cell[2]))

    data['block'] = blocks

    #to draw board
    board_dict = {}
    print(blocks)
    for cell in blocks:
        board_dict[(cell[0], cell[1])] = "[ ]"

    for cell in new_upper:
        board_dict[(cell[1][0], cell[1][1])] = cell[0]
    for cell in new_lower:
        board_dict[(cell[1][0], cell[1][1])] = cell[0]

    start = time.time()
    moves = generate_moves(data, moves)
    
    for each in moves:
        print("h")
        for e in each:
            print(e)

    # if len(moves) == 3:
    #     x = moves[0]
    #     y = moves[1]
    #     z = moves[2]

    #     all_possible_moves = np.array(np.meshgrid(x, y ,z)).T.reshape(-1,3)
    # elif len(moves) == 2:
    #     x = moves[0]
    #     y = moves[1]

    #     all_possible_moves = np.array(np.meshgrid(x, y)).T.reshape(-1,2)
    # else:
    #     all_possible_moves = moves[0]

    all_possible_moves = list(itertools.product(*moves))

    print(all_possible_moves)
    print(len(all_possible_moves))
    end = time.time()
    print(end - start)

    print_board(board_dict, "", ansi=False)
    
    # a = np.array((2,2))
    # b = np.array((1,2))
    # res = a - b
    #print(res)

#takes in transformed data of just upper and lower types
def utility(trans_data):
    #win state if all lower pieces removed.
    if not trans_data['lower']:
        return 10
    #lose state if any enemy piece is un-capturable (may be too intense for utl.)
    elif 'p' in trans_data['lower'] and 's' not in trans_data['upper']:
        return -10
    elif 'r' in trans_data['lower'] and 'p' not in trans_data['upper']:
        return -10
    elif 's' in trans_data['lower'] and 'r' not in trans_data['upper']:
        return -10
    else:
        eval_value = 10 - len(trans_data['lower'])
        return eval_value
    



def is_legal(data, move):
    x = move[0]
    y = move[1]
    if abs(x) > 4 or abs(y) > 4:
        return False
    elif (x, y) in data['block']:
        return False
    else:
        return True

def is_end(data):
    return 0

def choose_operator(data, trans_data, moves):

    score, move = minimax(0, data, trans_data)

def minimax(curr_depth, data, trans_data, possible_moves):
    if (curr_depth == 10) or (utility(trans_data) != 0):
        return utility(trans_data)

    best_value = float('inf')
    target = ""

    for move in moves:
        return 0

def generate_moves(data, moves):
    
    all_moves = []
    for upper_cell in data['upper']:
        all_moves.append(generate_node_moves(data, upper_cell, moves))

    return all_moves

def generate_node_moves(data, node, moves):
#generates all possible moves for a given node and game data (state).
    output = []
    #start = time.time()
    for move in moves:
        
        new_move = tuple(map(sum, zip(node[1],move))) #node[1] + move
        if (is_legal(data, new_move)):
            print(new_move)
            output.append((node, (node[0], new_move)))

    for each in data['upper']:
        if (hex_distance(node[1], each[1]) == 1):
            direction = tuple(map(lambda i, j: j - i, node[1], each[1]))

            for swing in moves:
                possible_swing = tuple(map(sum, zip(each[1],swing)))
                if (hex_distance(possible_swing, node[1]) > 1) and is_legal(data, possible_swing):
                    output.append((node, (node[0], possible_swing)))
    #end = time.time()
    #print(end-start)
    return output
    