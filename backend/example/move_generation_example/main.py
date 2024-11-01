import grpc
import time

import game_pb2_grpc
import game_pb2
import static_eval

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

def pretty_print_board(buffer, BOARD_SIZE):
	counter = 0
	for byte in buffer:
		print(f" {int(byte)} ", end='')
		counter += 1
		if counter == BOARD_SIZE:
			print("")
			counter = 0

def get_top_idx(idx, BOARD_SIZE):
	if idx < BOARD_SIZE:
		return -1
	return idx - BOARD_SIZE

def get_btm_idx(idx, BOARD_SIZE):
	dim = (BOARD_SIZE * BOARD_SIZE)
	if idx >= (dim - BOARD_SIZE - 1):
		return -1
	return idx + BOARD_SIZE

def get_left_idx(idx, BOARD_SIZE):
	if (idx) % BOARD_SIZE == 0:
		return -1
	return idx - 1

def get_right_idx(idx, BOARD_SIZE):
	if (idx + 1) % BOARD_SIZE == 0:
		return -1
	return idx + 1

def get_top_left_idx(idx, BOARD_SIZE):
	top = get_top_idx(idx, BOARD_SIZE)
	if top == -1:
		return -1
	return get_left_idx(top, BOARD_SIZE)

def get_btm_left_idx(idx, BOARD_SIZE):
	btm = get_btm_idx(idx, BOARD_SIZE)
	if btm == -1:
		return -1
	return get_left_idx(btm, BOARD_SIZE)

def get_top_right_idx(idx, BOARD_SIZE):
	top = get_top_idx(idx, BOARD_SIZE)
	if top == -1:
		return -1
	return get_right_idx(top, BOARD_SIZE)

def get_btm_right_idx(idx, BOARD_SIZE):
	btm = get_btm_idx(idx, BOARD_SIZE)
	if btm == -1:
		return -1
	return get_right_idx(btm, BOARD_SIZE)

def expand_all_directions(idx: int, depth: int, BOARD_SIZE: int):
	res = []
	dir_fns = [get_top_idx, get_btm_idx, get_left_idx, get_right_idx, get_top_left_idx, get_top_right_idx, get_btm_left_idx, get_btm_right_idx]
	for dir in dir_fns:
		last_dir_res = idx
		curr = []
		for i in range(depth):
			new_dir_res = dir(last_dir_res, BOARD_SIZE)
			if new_dir_res == -1:
				break
			curr.append(new_dir_res)
			last_dir_res = new_dir_res
		res.append(curr)
	return res

# returns true if a capture is possible by me if i place curr_piece in idx
# the opposite of validate_nocap_direction
def check_capture_made_dir(direction_fn, idx, board_size, curr_piece, board):
	check_cell_idx = direction_fn(idx, board_size)
	check_cell = board[check_cell_idx]
	# gets cell at direction_fn, if its enemy
	if check_cell > 0 and check_cell != curr_piece:
		# gets cell at direction_fn again
		check_cell_idx = direction_fn(check_cell_idx, board_size)
		check_cell = board[check_cell_idx]
		# if its still enemy
		if check_cell > 0 and check_cell != curr_piece:
			# gets cell at direction_fn again
			check_cell_idx = direction_fn(check_cell_idx, board_size)
			check_cell = board[check_cell_idx]
			# if its ally
			if check_cell == curr_piece:
				return True
	return False

# This function will simulate the effect of placing a piece on the board, and it would return None if such 
# a placmenet is invalid / impossible
def place_piece_attempt(index, piece, state, BOARD_SIZE) -> None | game_pb2.GameState:
	board = state.board

	# validate if board index is empty 
	if board[index] != 0:
		return None
	
	# validate if placing this piece violates double free three rule

	# validate if placing such a piece will capture opponenet
	captured_validation_res = []
	fn_mappings = [
		(0, get_btm_idx),
		(1, get_top_idx),
		(2, get_left_idx),
		(3, get_right_idx),
		(4, get_btm_left_idx),
		(5, get_top_right_idx),
		(6, get_top_left_idx),
		(7, get_btm_right_idx)
	]
	captured_validation_res.append(check_capture_made_dir(fn_mappings[0][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[1][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[2][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[3][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[4][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[5][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[6][1], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(check_capture_made_dir(fn_mappings[7][1], index, BOARD_SIZE, piece, board))
	we_captured_indices = []
	for (idx, elem) in enumerate(captured_validation_res):
		if elem is True:
			we_captured_indices.append(idx)
	if len(we_captured_indices) > 0:
		new_board = bytearray(board[:])
		new_board[index] = piece
		new_p1_captures = state.p1_captures
		new_p2_captures = state.p2_captures
		for we_captured_idx in we_captured_indices:
			# determine the direction of capture
			fn_mapping = fn_mappings[we_captured_idx]

			# turn neighbour cell into blank, fill curr blank and increase capture
			idx1 = fn_mapping[1](index, BOARD_SIZE)
			idx2 = fn_mapping[1](idx1, BOARD_SIZE)
			new_board[idx1] = 0
			new_board[idx2] = 0
			new_p1_captures = new_p1_captures + 1 if piece == 1 else new_p1_captures
			new_p2_captures = new_p2_captures + 1 if piece == 2 else new_p2_captures
		
		new_board = bytes(new_board)
		game_state = game_pb2.GameState(
			board=new_board,
			p1_captures=new_p1_captures,
			p2_captures=new_p2_captures,
			num_turns=state.num_turns + 1,
			is_end=1 if new_p1_captures >= 5 else 2 if new_p2_captures >= 5 else 0,
			time_to_think_ns=0
		)
		return game_state

	# validate if placing such a piece will get myself captured
	captured_validation_res = []
	fn_mappings = [
		(0, get_btm_idx, get_top_idx),
		(1, get_top_idx, get_btm_idx),
		(2, get_left_idx, get_right_idx),
		(3, get_right_idx, get_left_idx),
		(4, get_btm_left_idx, get_top_right_idx),
		(5, get_top_right_idx, get_btm_left_idx),
		(6, get_top_left_idx, get_btm_right_idx),
		(7, get_btm_right_idx, get_top_left_idx)
	]
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[0][1], fn_mappings[0][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[1][1], fn_mappings[1][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[2][1], fn_mappings[2][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[3][1], fn_mappings[3][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[4][1], fn_mappings[4][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[5][1], fn_mappings[5][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[6][1], fn_mappings[6][2], index, BOARD_SIZE, piece, board))
	captured_validation_res.append(static_eval.validate_nocap_direction(fn_mappings[7][1], fn_mappings[7][2], index, BOARD_SIZE, piece, board))
	try:
		we_got_captured_idx = captured_validation_res.index(False)
		
		# determine the direction of capture
		fn_mapping = fn_mappings[we_got_captured_idx]

		# turn neighbour cell into blank and increase capture 
		new_board = bytearray(board[:])
		new_board[fn_mapping[1](index, BOARD_SIZE)] = 0
		new_board = bytes(new_board)

		new_p1_captures = state.p1_captures if piece == 2 else state.p1_captures + 1
		new_p2_captures = state.p2_captures if piece == 1 else state.p2_captures + 1
		game_state = game_pb2.GameState(
			board=new_board,
			p1_captures=new_p1_captures,
			p2_captures=new_p2_captures,
			num_turns=state.num_turns + 1,
			is_end=1 if new_p1_captures >= 5 else 2 if new_p2_captures >= 5 else 0,
			time_to_think_ns=0
		)
		return game_state
	except:
		pass
	
	new_board = bytearray(board[:])
	# place piece in empty space, TODO check for capture and win and heuristics
	new_board[index] = piece
	new_board = bytes(new_board)

	game_state = game_pb2.GameState(
		board=new_board,
		p1_captures=state.p1_captures,
		p2_captures=state.p2_captures,
		num_turns=state.num_turns + 1,
		is_end=False,
		time_to_think_ns=0
	)

	return game_state

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
		directional_indices = sum(expand_all_directions(i, 2, BOARD_SIZE), []) # combine list results
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
			p2_captures=state.p2_captures,
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
	# BOARD_SIZE = 19

	# board = bytes([
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	# ]
	# )

	BOARD_SIZE = 9

	board = bytes([
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 1, 1, 0, 0, 0, 2, 0, 0,
		0, 1, 0, 1, 0, 0, 2, 0, 1,
		0, 2, 0, 0, 2, 0, 2, 0, 0,
		0, 0, 0, 0, 0, 0, 2, 0, 0,
		0, 0, 0, 0, 0, 0, 1, 0, 2,
		0, 0, 0, 0, 0, 0, 0, 0, 0
	])

	# p1 is 1, p2 is 2
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=0,
		p2_captures=0,
		num_turns=0,
		is_end=False,
		time_to_think_ns=0
	)

	print(expand_all_directions(0, BOARD_SIZE, BOARD_SIZE))
	# new_state = place_piece_attempt(19, 2, game_state, BOARD_SIZE)
	# if new_state is None:
	# 	print("new state is none")
	# else:
	# 	pretty_print_board(new_state.board, BOARD_SIZE)
	# 	print(f"{new_state}")

	# move_tree = generate_move_tree(game_state, BOARD_SIZE, 1, 3)
	# print(f"{len(move_tree)}")
	
	# for node in move_tree:
	# 	pretty_print_board(node[0].board, BOARD_SIZE)
	# 	print("")

	# possible_moves = generate_possible_moves(game_state, BOARD_SIZE, 1)
	# print(f"{len(possible_moves)}")
	# for state in possible_moves:
	# 	pretty_print_board(state.board, BOARD_SIZE)
	# 	print("")

main()