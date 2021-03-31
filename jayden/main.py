"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
from collections import defaultdict
from itertools import product
import copy
from queue import PriorityQueue
import math

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing


def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TO-DO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).

    print(data)
    ally_dict, enemy_dict, block_dict = read_file(data)

    print_board(ally_dict)
    print_board(enemy_dict)
    path = best_first_search(ally_dict, enemy_dict, block_dict)
    print(path)

    # prev_state_dict = defaultdict(list)
    # for state in path:
    #     ally_dict, enemy_dict = state

    #     # Populate the dictonary with states of each tokens in current state
    #     curr_state_dict = defaultdict(list)
    #     for key, values in ally_dict.items():
    #         for token in values:
    #             path_dict[token] += key

    #     # First state hence no previous path
    #     if len(prev_state_dict) == 0:
    #         continue
    #     else:
    #         for token in curr_state_dict:
    #             if len()



    for state in path:
        ally, enemy = state
        board_dict = {}
        # Add lower token (enemies) onto the board to be printed
        for key, values in enemy.items():
            if len(values) == 1:
                string = f"({values[0]})"
            else:
                string = "("
                for value in values:
                    string = string+value+")"
            board_dict[key] = string
        # Add upper token (allies) onto the board to be printed
        for key, values in ally.items():
            if key not in board_dict:
                if len(values) == 1:
                    string = f"({values[0].upper()})"
                else:
                    string = "("
                    for value in values:
                        string = string+value.upper()+")"
                board_dict[key] = string
            else:
                for value in values:
                    board_dict[key] = board_dict[key]+value.upper()+")"
        # Add the blocks onto the board to be printed
        for key, value in block_dict.items():
            board_dict[key] = "[ ]"
        print_board(board_dict, "Next State")


def read_file(data):
    ally_dict = defaultdict(list)
    enemy_dict = defaultdict(list)
    block_dict = defaultdict(list)

    # Keep track of the amount of token types for ally
    token_dict = {"r": 0, "p": 0, "s": 0}

    for key in data:
        for token, r, q in data[key]:
            if key == "upper":
                ally_dict[(r,q)] = [token+str(token_dict[token])]
                token_dict[token] += 1
            elif key == "lower":
                enemy_dict[(r,q)] = [token]
            else:
                block_dict[(r,q)] = [token]
    
    return ally_dict, enemy_dict, block_dict


def hex_distance(x, y):
    """
    Outputs the Manhattan distance between two hex coordinates modified from 
    the hex distance formula as given in 
    https://www.redblobgames.com/grids/hexagons/ 
    """

    x_r, x_q = x
    y_r, y_q = y

    return (abs(x_q - y_q) 
          + abs(x_q + x_r - y_q - y_r)
          + abs(x_r - y_r)) / 2


def get_all_slides(coordinate, block_dict):
    input_r, input_q = coordinate
    board_range = 4
    delta_coord = [-1, 0, 1]
    adj_cells = []

    for delta_r in delta_coord:
        for delta_q in delta_coord:
            r = input_r+delta_r
            q = input_q+delta_q
            if (delta_r != delta_q) and (hex_distance((r,q), (0,0)) <= board_range):
                adj_cells.append((r,q))

    return [coord for coord in adj_cells if coord not in block_dict]


def get_all_swings(coordinate, ally_dict, block_dict):
    adj_cells = get_all_slides(coordinate, block_dict)
    ally_adj_cells = []

    for cell in adj_cells:
        if cell in ally_dict:
            ally_adj_cells += get_all_slides(cell, block_dict)

    return [x for x in ally_adj_cells if (x not in adj_cells) and (x not in block_dict) and (x != coordinate)]


def get_all_actions(coordinate, ally_dict, block_dict):
    return sorted(get_all_slides(coordinate, block_dict) 
                  + get_all_swings(coordinate, ally_dict, block_dict))


def battle(ally_dict, enemy_dict):
    # tokens_dict = {"r": 0, "p": 1, "s": 2}
    visited_cells = set()

    for cell in ally_dict:
        # Reset the type of tokens in cell
        # tokens_present = [False, False, False]
        tokens_dict = {"r": False, "p": False, "s": False}
        # Find which type of tokens are present in the cell
        for token in ally_dict[cell]:
            # tokens_present[tokens_dict[token]] = True
            tokens_dict[token[0]] = True
        if cell in enemy_dict:
            for token in enemy_dict[cell]:
                # tokens_present[tokens_dict[token]] = True
                tokens_dict[token] = True
        # # Find which type of token to keep in the cell
        # if all(tokens_present):
        #     tokens_present = [False] * 3
        # else:
        #     tokens_present = [not tokens_present[(i+1)%3] for i in range(3)]
        if all(list(tokens_dict.values())):
            tokens_dict = {"r": False, "p": False, "s": False}
        else:
            tokens_dict["r"] = not tokens_dict["p"]
            tokens_dict["p"] = not tokens_dict["s"]
            tokens_dict["s"] = not tokens_dict["r"]
        # Remove any tokens that lost
        # ally_dict[cell] = [token for token in ally_dict[cell] if tokens_present[tokens_dict[token]]]
        ally_dict[cell] = [token for token in ally_dict[cell] if tokens_dict[token[0]]]
        if cell in enemy_dict:
            # enemy_dict[cell] = [token for token in enemy_dict[cell] if tokens_present[tokens_dict[token]]]
            enemy_dict[cell] = [token for token in enemy_dict[cell] if tokens_dict[token]]
        # Keep track of visited cells
        visited_cells.add(cell)
    
    # for cell in enemy_dict:
    #     # Repeat the process for any non-visited cells for enemy tokens
    #     if cell not in visited_cells:
    #         # Reset the type of tokens in cell
    #         # tokens_present = [False, False, False]
    #         tokens_dict = {"r": False, "p": False, "s": False}
    #         # Find which type of tokens are present in the cell
    #         for token in enemy_dict[cell]:
    #             # tokens_present[tokens_dict[token]] = True
    #             tokens_dict[token] = True
    #         # Find which type of token to keep in the cell
    #         # if all(tokens_present):
    #         #     tokens_present = [False] * 3
    #         # else:
    #         #     tokens_present = [not tokens_present[(i+1)%3] for i in range(3)]
    #         if all(list(tokens_dict.values())):
    #             tokens_dict = {"r": False, "p": False, "s": False}
    #         else:
    #             tokens_dict["r"] = not tokens_dict["p"]
    #             tokens_dict["p"] = not tokens_dict["s"]
    #             tokens_dict["s"] = not tokens_dict["r"]
    #         # Remove any tokens that lost
    #         # enemy_dict[cell] = [token for token in enemy_dict[cell] if tokens_present[tokens_dict[token]]]
    #         print(enemy_dict)
    #         print(tokens_dict)
    #         enemy_dict[cell] = [token for token in enemy_dict[cell] if tokens_dict[token]]

    # Clean up any empty cells in the dictionaries
    for dictionary in [ally_dict, enemy_dict]:
        for cell in list(dictionary.keys()):
            if dictionary[cell] == []:
                dictionary.pop(cell)


def has_won(enemy_dict):
    if len(enemy_dict) == 0:
        return True
    for cell in enemy_dict:
        if len(enemy_dict[cell]) != 0:
            return False
    return True


def can_win(ally_dict, enemy_dict):
    board_dict = [ally_dict, enemy_dict]
    ally_tokens_dict = {"r": False, "p": False, "s": False}
    enemy_tokens_dict = {"r": False, "p": False, "s": False}
    token_dict = [ally_tokens_dict, enemy_tokens_dict]

    for i in range(2):
        for cell in board_dict[i]:
            for token in board_dict[i][cell]:
                token_dict[i][token[0]] = True

    # print(ally_tokens_dict)
    # print(enemy_tokens_dict)

    for i in range(3):
        # print(list(ally_tokens_dict.values())[i])
        if list(ally_tokens_dict.values())[i] == False:
            # print(list(enemy_tokens_dict.values())[(i-1)%3])
            if list(enemy_tokens_dict.values())[(i-1)%3] == True:
                return False
    
    return True


# A wrapper class for state priority to prevent equal priority between states
class PriorityEntry(object):

    def __init__(self, priority):
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


def calculate_priority(ally_dict, enemy_dict, initial_enemies, block_dict):
    """
    The lower the priority the better
    """

    print(ally_dict)
    # Return the worst possible priority if the game can't be won
    if not can_win(ally_dict, enemy_dict):
        return PriorityEntry(math.inf)

    # Find the min distance between each ally token and its target enemy token
    dist_priority = 0
    target_dict = {"r": "s", "p": "r", "s": "p"}
    for a_cell in ally_dict:
        for ally in ally_dict[a_cell]:
            target = set()
            # Find all the hex coordinates of its potential targets
            for e_cell in enemy_dict:
                if target_dict[ally[0]] in enemy_dict[e_cell]:
                    target.add(e_cell)

            #dist_priority += min([hex_distance(a_cell, e_cell) for e_cell in target])
            if target:
                dist_priority += min([hex_distance(a_cell, e_cell) for e_cell in target])
            else:
                dist_priority += 0

    # Change the sign as higher number of ally tokens are more preferable
    # Give a slightly higher weight to discourage killing ally
    ally_priority = 10*(-len(ally_dict))

    # Find the priority associated with number of enemies
    # Give a really heavy weight to lowering the number of enemies
    enemy_priority = 100*(len(enemy_dict)-initial_enemies)

    # total = sum([dist_priority, ally_priority, enemy_priority])
    # return PriorityEntry(total)
    return PriorityEntry(dist_priority + ally_priority + enemy_priority)


def get_next_states(ally_dict, enemy_dict, block_dict):
    next_states = []
    possible_actions = []
    tokens = []

    for cell in ally_dict:
        for token in ally_dict[cell]:
            possible_actions += [get_all_actions(cell, ally_dict, block_dict)]
            tokens += [token]

    for action in product(*possible_actions):
        action = list(action)
        new_ally_dict = {}
        for i in range(len(tokens)):
            new_ally_dict[action[i]] = [tokens[i]]
        new_enemy_dict = copy.deepcopy(enemy_dict)
        battle(new_ally_dict, new_enemy_dict)
        next_states.append((new_ally_dict, new_enemy_dict))
    print(next_states)
    return next_states


def best_first_search(ally_dict, enemy_dict, block_dict):
    visited = []
    path = [(ally_dict, enemy_dict)]
    initial_enemies = len(enemy_dict)
    frontier = PriorityQueue()

    priority = calculate_priority(ally_dict, enemy_dict, initial_enemies, block_dict)
    frontier.put((0, priority, ally_dict, enemy_dict, path))

    while not frontier.empty():
        depth, priority, ally_dict, enemy_dict, path = frontier.get()
        print_board(ally_dict)
        if has_won(enemy_dict):
            return path + [(copy.deepcopy(ally_dict), copy.deepcopy(enemy_dict))]

        visited += [(copy.deepcopy(ally_dict), copy.deepcopy(enemy_dict))]
        states = PriorityQueue()
        for state in get_next_states(ally_dict, enemy_dict, block_dict):
            next_ally_dict, next_enemy_dict = state
            priority = calculate_priority(next_ally_dict, next_enemy_dict, initial_enemies, block_dict)
            print(priority.priority)
            states.put((priority, next_ally_dict, next_enemy_dict))

        depth -= 1
        while not states.empty():
            priority, next_ally_dict, next_enemy_dict = states.get()

            if (next_ally_dict, next_enemy_dict) not in visited:
                if has_won(next_enemy_dict):
                    return path + [(copy.deepcopy(next_ally_dict), copy.deepcopy(enemy_dict))]
                new_path = path + [(copy.deepcopy(next_ally_dict), copy.deepcopy(enemy_dict))]
                frontier.put((depth, priority, next_ally_dict, next_enemy_dict, new_path))

    return path







# ally_dict = {(0,0): ["r0", "p0", "s0"], 
#              (0,1): ["r1", "p1"], 
#              (0,2): ["r2", "r3"], 
#              (0,3): ["r4"], 
#              (0,4): ["p2"], 
#              (0,5): ["s1", "p3"], 
#              (0,6): ["s2"], 
#              (0,7): ["s3", "p4"]
#             }

# enemy_dict = {(0,0): ["r", "p", "s"], 
#               (0,1): ["p", "p"], 
#               (0,2): ["p"],
#               (0,3): ["r"],
#               (0,5): ["p"], 
#               (0,6): ["r"], 
#               (0,7): ["r"]
#              }

# print(ally_dict)
# print(enemy_dict)
# battle(ally_dict, enemy_dict)
# print(ally_dict)
# print(enemy_dict)

# ally_dict = {(0,0): ["r"], 
#              (1,0): ["r", "p"], 
#             }

# enemy_dict = {(0,0): ["r", "p", "s"], 
#               (0,1): ["p", "p"], 
#               (0,2): ["p"],
#              }

# block_dict = {(2,1): [""],  
#               (0,-1): [""], 
#               (-1,0): [""]
#              }

# ally_dict = {(-2,4): ["p"]
#              }

# enemy_dict = {(-2,4): ["r"]
#               }

# block_dict = {}

# print(can_win(ally_dict, enemy_dict))

# print(get_next_states(ally_dict, enemy_dict, block_dict))

    # prev_state_dict = defaultdict(list)
    # for state in path:
    #     ally_dict, enemy_dict = state

    #     # Populate the dictonary with states of each tokens in current state
    #     curr_state_dict = defaultdict(list)
    #     for key, values in ally_dict.items():
    #         for token in values:
    #             path_dict[token] += key

    #     # First state hence no previous path
    #     if len(prev_state_dict) == 0:
    #         continue
    #     else:
    #         for token in curr_state_dict:
    #             if len()