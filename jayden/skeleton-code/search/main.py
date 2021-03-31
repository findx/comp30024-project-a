"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!

Written By: Jun Cheng Woo (1045457) <woojw@student.unimelb.edu.au>
"""

# Import all the neccessary libraries
import copy
from collections import defaultdict
from itertools import product
import json
import math
from queue import PriorityQueue
import sys

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing


def main():
    """
    The main entry point of the program which control the main flow of the 
    simulation of the single player RoPaSci 360 game.
    """

    # Read the data from the given json file and load them into a dictionary
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

    # Refine the data from the json into separate dictionaries each for a 
    # type of token or block in the game
    ally_dict, enemy_dict, block_dict = read_file(data)

    # Run the best first search and find the solution for the problem
    path = best_first_search(ally_dict, enemy_dict, block_dict)

    # Retrace the states and find the actions taken by each token
    prev_state_dict = {}
    time = 0
    for state in path:
        ally_dict, enemy_dict = state

        # Populate the dictonary with states of each tokens in current state
        curr_state_dict = {}
        for key, values in ally_dict.items():
            for token in values:
                curr_state_dict[token] = key

        # Find the actions taken and print it to stdout
        if len(prev_state_dict) != 0:
            for token in curr_state_dict:
                prev_r, prev_q = prev_state_dict[token]
                curr_r, curr_q = curr_state_dict[token]
                distance = hex_distance((prev_r, prev_q), (curr_r, curr_q))
                # It's a slide action
                if distance == 1:
                    print_slide(time, prev_r, prev_q, curr_r, curr_q)
                # It's a swing action
                elif distance == 2:
                    print_swing(time, prev_r, prev_q, curr_r, curr_q)
                else:
                    print("# Unknown Move")

        prev_state_dict = copy.deepcopy(curr_state_dict)
        time += 1

    # # For printing out the board nicely
    #     ally, enemy = state
    #     board_dict = {}
    #     # Add lower token (enemies) onto the board to be printed
    #     for key, values in enemy.items():
    #         if len(values) == 1:
    #             string = f"({values[0]})"
    #         else:
    #             string = "("
    #             for value in values:
    #                 string = string+value+")"
    #         board_dict[key] = string
    #     # Add upper token (allies) onto the board to be printed
    #     for key, values in ally.items():
    #         if key not in board_dict:
    #             if len(values) == 1:
    #                 string = f"({values[0].upper()})"
    #             else:
    #                 string = "("
    #                 for value in values:
    #                     string = string+value.upper()+")"
    #             board_dict[key] = string
    #         else:
    #             for value in values:
    #                 board_dict[key] = board_dict[key]+value.upper()+")"
    #     # Add the blocks onto the board to be printed
    #     for key, value in block_dict.items():
    #         board_dict[key] = "[ ]"
    #     divider = "-------------------------------------------------------"
    #     print_board(board_dict, divider)


def read_file(data):
    """
    Return the 3 dictionaries containing the refined data of the coordinates 
    and type of each token and blocks on the board.
    """

    ally_dict = defaultdict(list)
    enemy_dict = defaultdict(list)
    block_dict = defaultdict(list)

    # Keep track of the amount of each token types for ally
    token_dict = {"r": 0, "p": 0, "s": 0}

    # Separate each input data into different specific dictionaries
    for key in data:
        for token, r, q in data[key]:
            # Assign an ID for each token
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
    the hex distance formula as shown in 
    https://www.redblobgames.com/grids/hexagons/.
    """

    x_r, x_q = x
    y_r, y_q = y

    return (abs(x_q - y_q) 
          + abs(x_q + x_r - y_q - y_r)
          + abs(x_r - y_r)) / 2


def get_all_slides(coordinate, block_dict):
    """
    Return a list containing all the slide actions that could be made from a 
    certain coordinate on the board without hitting any blocks.
    """

    input_r, input_q = coordinate
    # The maximum range a hex could be from the centre
    board_range = 4
    # The amount of distance a token can move through a slide action
    delta_coord = [-1, 0, 1]
    adj_cells = []

    for delta_r in delta_coord:
        for delta_q in delta_coord:
            r = input_r+delta_r
            q = input_q+delta_q
            # Check if it is a valid move from the curent hex
            if ((delta_r != delta_q) and 
                (hex_distance((r,q), (0,0)) <= board_range)):
                adj_cells.append((r,q))

    return [coord for coord in adj_cells if coord not in block_dict]


def get_all_swings(coordinate, ally_dict, block_dict):
    """
    Return a list containing all the swing actions that could be made around 
    an ally token from a certain coordinate on the board without hitting 
    any blocks.
    """

    adj_cells = get_all_slides(coordinate, block_dict)
    ally_adj_cells = []

    # Find any adjacent cells from adjacent allies that could be reached
    for cell in adj_cells:
        if cell in ally_dict:
            ally_adj_cells += get_all_slides(cell, block_dict)

    return [x for x in ally_adj_cells if ((x not in adj_cells) and 
                                          (x not in block_dict) and 
                                          (x != coordinate))]


def get_all_actions(coordinate, ally_dict, block_dict):
    """
    Return a sorted list containing all the actions that could be made from a 
    certain coordinate in a board without violating any rules.
    """

    return sorted(get_all_slides(coordinate, block_dict) 
                  + get_all_swings(coordinate, ally_dict, block_dict))


def battle(ally_dict, enemy_dict):
    """
    Carry out the battling action for every hex that is occupied by more than 
    one token and remove any tokens that lost from the hex.
    """

    tokens_dict = {"r": 0, "p": 1, "s": 2}
    visited_cells = set()

    for cell in ally_dict:
        # Reset the type of tokens in cell
        tokens_present = [False, False, False]
        # Find which type of tokens are present in the cell
        for token in ally_dict[cell]:
            tokens_present[tokens_dict[token[0]]] = True
        if cell in enemy_dict:
            for token in enemy_dict[cell]:
                tokens_present[tokens_dict[token]] = True
        # Find which type of token to keep in the cell
        if all(tokens_present):
            tokens_present = [False] * 3
        else:
            tokens_present = [not tokens_present[(i+1)%3] for i in range(3)]
        # Remove any tokens that lost
        ally_dict[cell] = [token for token in ally_dict[cell] 
                if tokens_present[tokens_dict[token[0]]]]
        if cell in enemy_dict:
            enemy_dict[cell] = [token for token in enemy_dict[cell] 
                                if tokens_present[tokens_dict[token]]]
        # Keep track of visited cells
        visited_cells.add(cell)
    
    # Clean up any empty cells in the dictionaries
    for dictionary in [ally_dict, enemy_dict]:
        for cell in list(dictionary.keys()):
            if dictionary[cell] == []:
                dictionary.pop(cell)


def has_won(enemy_dict):
    """
    Return a boolean indicating if the game has won by the 'upper' player.
    """

    # If no more enemies are left then the game is won
    if len(enemy_dict) == 0:
        return True
    for cell in enemy_dict:
        if len(enemy_dict[cell]) != 0:
            return False
    return True


def can_win(ally_dict, enemy_dict):
    """
    Return a boolean indicating if the game is still winnable by the 'upper' 
    player with the current board configurations.
    """

    board_dict = [ally_dict, enemy_dict]
    ally_tokens_dict = {"r": False, "p": False, "s": False}
    enemy_tokens_dict = {"r": False, "p": False, "s": False}
    token_dict = [ally_tokens_dict, enemy_tokens_dict]

    # Find out what type of tokens are left for both players
    for i in range(2):
        for cell in board_dict[i]:
            for token in board_dict[i][cell][0]:
                token_dict[i][token] = True

    # Check if there is an enemy token that the 'upper' player cannot defeat
    for i in range(3):
        if list(ally_tokens_dict.values())[i] == False:
            if list(enemy_tokens_dict.values())[(i-1)%3] == True:
                return False
    
    return True


class PriorityEntry(object):
    """
    A wrapper class for state priority to prevent equal priority between states.
    """

    def __init__(self, priority):
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


def calculate_priority(ally_dict, enemy_dict, initial_enemies, block_dict):
    """
    Return a number indicating the priority of reaching this current state of 
    the game. The lower the priority the more favourable this state is.
    """

    # Return the worst possible priority if the game can't be won anymore
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
            if target:
                dist_priority += min([hex_distance(a_cell, e_cell) 
                        for e_cell in target])
            else:
                dist_priority += 0

    # Change the sign as higher number of ally tokens are more preferable
    # Give a slightly higher weight (20 times more) to discourage killing ally
    ally_priority = 20 * (-len(ally_dict))

    # Find the priority associated with number of enemies
    # Give a heavy weight (100 times more) to reducing the number of enemies
    enemy_priority = 100 * (len(enemy_dict)-initial_enemies)

    return PriorityEntry(dist_priority+ally_priority+enemy_priority)


def best_first_search(ally_dict, enemy_dict, block_dict):
    """
    Search for a solution for the problem using greedy best first search and 
    return a path of the states to reach at each time until the final winning 
    state is reached.
    """

    visited = []
    path = [(ally_dict, enemy_dict)]
    n_enemies = len(enemy_dict)

    frontier = PriorityQueue()
    priority = calculate_priority(ally_dict, enemy_dict, n_enemies, block_dict)
    frontier.put((0, priority, ally_dict, enemy_dict, path))

    # Continue until no more states can be explored anymore
    while not frontier.empty():
        depth, priority, ally_dict, enemy_dict, path = frontier.get()

        # Return the path to get to this state if the game has finished
        if has_won(enemy_dict):
            return path+[(copy.deepcopy(ally_dict), copy.deepcopy(enemy_dict))]

        # Keep a record of any visited states to prevent infinite loops
        visited += [(copy.deepcopy(ally_dict), copy.deepcopy(enemy_dict))]

        # Use a priority queue to find the most favourable state to explore
        states = PriorityQueue()
        for state in get_next_states(ally_dict, enemy_dict, block_dict):
            next_ally_dict, next_enemy_dict = state
            priority = calculate_priority(next_ally_dict, next_enemy_dict, 
                                          n_enemies, block_dict)
            states.put((priority, next_ally_dict, next_enemy_dict))

        # Keep searching all the children until a final state is reach
        depth -= 1
        while not states.empty():
            priority, next_ally_dict, next_enemy_dict = states.get()
            # Visit this state if it has not been visited before
            if (next_ally_dict, next_enemy_dict) not in visited:
                if has_won(next_enemy_dict):
                    return path + [(copy.deepcopy(next_ally_dict), 
                                    copy.deepcopy(enemy_dict))]
                # Continue adding the child of the current state to the queue
                new_path = path + [(copy.deepcopy(next_ally_dict), 
                                    copy.deepcopy(enemy_dict))]
                frontier.put((depth, priority, next_ally_dict, 
                              next_enemy_dict, new_path))

    return path


def get_next_states(ally_dict, enemy_dict, block_dict):
    """
    Return a list containing all the possible next states (child) spanning 
    from the current state of the game.
    """

    next_states = []
    possible_actions = []
    tokens = []

    # Get all the possible actions for each token
    for cell in ally_dict:
        for token in ally_dict[cell]:
            possible_actions += [get_all_actions(cell, ally_dict, block_dict)]
            tokens += [token]

    # Find the cross product of all the possible actions to find all the 
    # possible future states
    for action in product(*possible_actions):
        action = list(action)
        new_ally_dict = {}
        for i in range(len(tokens)):
            new_ally_dict[action[i]] = [tokens[i]]
        new_enemy_dict = copy.deepcopy(enemy_dict)
        # Carry out the battling action to remove any lost token of this state
        battle(new_ally_dict, new_enemy_dict)
        next_states.append((new_ally_dict, new_enemy_dict))

    return next_states
