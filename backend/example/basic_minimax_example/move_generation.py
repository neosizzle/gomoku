import grpc
import time

import game_pb2_grpc
import game_pb2
import utils

def measure_duration_ns(func):
    """Decorator to measure the duration of a function in nanoseconds."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start timing
        result = func(*args, **kwargs)     # Call the function
        end_time = time.perf_counter()      # End timing
        duration_ns = (end_time - start_time) * 1_000_000_000  # Convert to nanoseconds
        print(f"Function '{func.__name__}' took {duration_ns:.2f} ns")
        return result
    return wrapper

def expand_all_directions(idx: int, depth: int, BOARD_SIZE: int):
	res = []
	dir_fns = [utils.get_top_idx, utils.get_btm_idx, utils.get_left_idx, utils.get_right_idx, utils.get_top_left_idx, utils.get_top_right_idx, utils.get_btm_left_idx, utils.get_btm_right_idx]
	for dir in dir_fns:
		last_dir_res = idx
		for i in range(depth):
			new_dir_res = dir(last_dir_res, BOARD_SIZE)
			if new_dir_res == -1:
				break
			res.append(new_dir_res)
			last_dir_res = new_dir_res
	return res

# generates a list of next states based on the initial state given 
def generate_possible_moves(state: game_pb2.GameState, BOARD_SIZE: int, piece: int) -> list[game_pb2.GameState]:
	curr_board = state.board
	dims = BOARD_SIZE * BOARD_SIZE
	res = []
	indices_to_check = set() # set for no dupes

	# we only select cells to fill if they are already near a piece
	for i in range(dims):
		# indices_to_check.add(i)
		# ignore cells which are blank
		if curr_board[i] == 0:
			continue
		
		# get all indices from all directions within a 2 depth range
		directional_indices = expand_all_directions(i, 2, BOARD_SIZE)
		for val in directional_indices:
			indices_to_check.add(val)

	# iterate through all cells in dimensions
	for i in indices_to_check:
		# ignore cells which are occupied
		if curr_board[i] != 0:
			continue

		# clone new board for game state, TODO optimize this to preallocation
		new_board = bytearray(curr_board[:])
		# place piece in empty space, TODO check for capture and win and heuristics
		new_board[i] = piece
		new_board = bytes(new_board)

		game_state = game_pb2.GameState(
			board=new_board,
			p1_captures=state.p1_captures,
			p0_captures=state.p0_captures,
			num_turns=state.num_turns + 1,
			is_end=False,
			time_to_think_ns=0
		)
		
		res.append(game_state)

	# pretty_print_board(curr_board, BOARD_SIZE)

	return res

def generate_move_tree(state: game_pb2.GameState, BOARD_SIZE: int, piece: int, depth: int) -> list[list[game_pb2.GameState | list[game_pb2.GameState]]]:
	res = [] # adjacency list

	for i in range(depth):
		curr_piece = piece
		if i % 2 != 0:
			if piece == 1:
				curr_piece = 2
			else:
				curr_piece = 1
		# generate fisrt depth and append leaves to the tree
		if len(res) == 0:
			root_children = generate_possible_moves(state, BOARD_SIZE, curr_piece)
			res.append([state, root_children])
			for state in root_children:
				res.append([state, None])
		else :
			new_leaves = []

			# iterate the adjacency list to find leaves
			for j in range(len(res)):
				if res[j][1] == None:
					# generate children of leaf
					leaf_children = generate_possible_moves(res[j][0], BOARD_SIZE, curr_piece)
					res[j][1] = leaf_children
					new_leaves.append(leaf_children)

			# update adjacency list to include all new leaves
			for leaf in new_leaves:
				for state in leaf:
					res.append([state, None])
	return res

def main():
	
	# some metadata here
	BOARD_SIZE = 19

	board = bytes([
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	]
	)

	# BOARD_SIZE = 9

	# board = board = bytes([0] * 81)
	# p0 is 0, p1 is 2
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=0,
		p0_captures=0,
		num_turns=0,
		is_end=False,
		time_to_think_ns=0
	)

	move_tree = generate_move_tree(game_state, BOARD_SIZE, 1, 3)
	print(f"{len(move_tree)}")
	# for node in move_tree:
	# 	pretty_print_board(node[0].board, BOARD_SIZE)
	# 	print("")

	# possible_moves = generate_possible_moves(game_state, BOARD_SIZE, 1)
	# print(f"{len(possible_moves)}")
	# for state in possible_moves:
	# 	pretty_print_board(state.board, BOARD_SIZE)
	# 	print("")
