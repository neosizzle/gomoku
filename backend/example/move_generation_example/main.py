import grpc
import time

import game_pb2_grpc
import game_pb2
import static_eval

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
	if idx > (dim - BOARD_SIZE - 1):
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

# group pairs of directions together, assuming the results returned are
# [get_top_idx, get_btm_idx, get_left_idx, get_right_idx, get_top_left_idx, get_top_right_idx, get_btm_left_idx, get_btm_right_idx]
def group_local_expansions(local_expansions):
	res = []
	res.append(local_expansions[0][::-1] + local_expansions[1])	
	res.append(local_expansions[2][::-1] + local_expansions[3])
	res.append(local_expansions[4][::-1] + local_expansions[7])	
	res.append(local_expansions[5][::-1] + local_expansions[6])	

	return res

# given a 1d buffer and the piece, retuen True if the buffer has a free three if idx_to_place
# is placed with piece
def has_free_three(buffer, piece, idx_to_place):
	begin = 0
	buffer_clone = buffer[:]

	# return if buffer is shorter than 5, need 5 pieces for a free three
	if len(buffer) < 5 or idx_to_place == -1:
		return False
	
	buffer_clone[idx_to_place] = piece

	# iterate the cloned modified buffer to find the first piece
	while begin < len(buffer_clone):
		# If we found our piece, execute procedure
		if buffer_clone[begin] == piece and begin != len(buffer) - 1:
			# try to find end with 1 gap leniency
			gap = 1
			end = begin + 1

			while end < len(buffer_clone):
				if buffer_clone[end] == 0:
					if gap == 0:
						break
					gap -= 1
					end += 1
					continue
				
				# enemy encounter
				if buffer_clone[end] != piece:
					break

				end += 1

			# move end back to piece
			if end == len(buffer_clone):
				end -= 1
			while end > begin + 1 and  buffer_clone[end] != piece:
				end -= 1

			# print(f"begin {begin} end {end}, {end - begin}, buffer {buffer_clone}")
			# at this point, end should be valid
			# make sure end element is 0 and begin element - 1 is 0
			if begin == 0:
				begin = end
				continue
			
			if end < len(buffer) - 1 and buffer_clone[end + 1] != 0:
				begin = end
				continue

			if buffer_clone[begin - 1] != 0:
				begin = end
				continue

			# check if length of free pieces is 2 or 3
			if end - begin < 2 or end - begin > 3:
				begin = end
				continue

			# if end - begin == 2, make sure there are no gaps
			if end - begin == 2 and buffer_clone[end - 1] == 0:
				begin = end
				continue

			return True
		begin += 1
	return False

# Detects double free threes when attempting to place a piece, will return true if a double free three
# is recognigzed
def detect_double_free_threes(input_idx, BOARD_SIZE, piece, board) -> bool :
	# generate local expansions of current piece
	local_expansions = expand_all_directions(input_idx, BOARD_SIZE, BOARD_SIZE)

	# group pairs of directions together, assuming the results returned are
	# 	[get_top_idx, get_btm_idx, get_left_idx, get_right_idx, get_top_left_idx, get_top_right_idx, get_btm_left_idx, get_btm_right_idx]
	local_expansion_grouping = group_local_expansions(local_expansions)
	# print(local_expansion_grouping)

	# for each grouping, extract cells
	cell_value_buffers = []
	group_indices = []
	for local_expansion in local_expansion_grouping:
		cell_values = []
		group_idx = -1
		for (i, expansion_index) in enumerate(local_expansion):
			# if the current idx is more than the idx stated in expansion, 
			# append the current value of idx at board but also make sure group idx is not empty
			if expansion_index > input_idx and group_idx == -1:
				cell_values.append(board[input_idx])
				group_idx = i # the index where the the input index is located at the group 
			
			cell_values.append(board[expansion_index])
			
		# sometimes this group_idx will remain -1,
		# this means input_idx is at the border.
		# we need to fix this since we are 
		# still required to run checks at border placements
		if group_idx == -1:
			# assumine that we are placing on blank value
			cell_values.append(board[input_idx])
			group_idx = len(cell_values) - 1
		
		cell_value_buffers.append(cell_values)
		group_indices.append(group_idx)
		# print(f"{cell_values} {group_idx}")

	# count valid free threes for each grouping. If valid free threes are > 1, return True
	free_three_idx = -1
	for (i, buffer) in enumerate(cell_value_buffers):
		print(f"has_free_three({buffer}, {piece}, {group_indices[i]})")
		if has_free_three(buffer, piece, group_indices[i]):
			print(f"OK has_free_three({buffer}, {piece}, {group_indices[i]})")
			if free_three_idx != -1:
				return True
			free_three_idx = i

	if free_three_idx == -1:
		return False

	# # for the valid three, expand all elements in that grouping and count valid free threes
	# grouping_with_ft = local_expansion_grouping[free_three_idx]
	# # print(grouping_with_ft)
	# for grouping_idx in grouping_with_ft:
	# 	local_expansions_ft = expand_all_directions(grouping_idx, BOARD_SIZE, BOARD_SIZE)
	# 	local_expansion_grouping_ft = group_local_expansions(local_expansions_ft)

	# 	# for each grouping, extract cells
	# 	cell_value_buffers = []
	# 	group_indices = []
	# 	for local_expansion in local_expansion_grouping_ft:
	# 		cell_values = []
	# 		group_idx = -1 
	# 		for (i, expansion_index) in enumerate(local_expansion):
	# 			if expansion_index > grouping_idx and group_idx == -1:
	# 				cell_values.append(board[grouping_idx])
	# 				group_idx = i

	# 			cell_values.append(board[expansion_index])

	# 		# sometimes this group_idx will remain -1,
	# 		# this means input_idx is at the border.
	# 		# we need to fix this since we are 
	# 		# still required to run checks at border placements
	# 		if group_idx == -1:
	# 			# assumine that we are placing on blank value
	# 			cell_values.append(board[input_idx])
	# 			group_idx = len(cell_values) - 1

	# 		cell_value_buffers.append(cell_values)
	# 		group_indices.append(group_idx) 

	# 	# for each of those expansions. If any valid three is found besides the original buffer, return True
	# 	for (i, buffer) in enumerate(cell_value_buffers):
	# 		if free_three_idx == i:
	# 			continue
	# 		# print(f"{group_indices} {buffer} {local_expansion_grouping_ft[i]} {grouping_idx}")
	# 		if has_free_three(buffer, piece, group_indices[i]):
	# 			# print(f"\thas_free_three({buffer}, {piece}, {group_indices[i]}), {free_three_idx} {i}")
	# 			# print(f"{local_expansion_grouping_ft}")
	# 			# print(f"{cell_value_buffers}")
	# 			return True
	  
	return False

# This function will simulate the effect of placing a piece on the board, and it would return None if such 
# a placmenet is invalid / impossible
def place_piece_attempt(index, piece, state, BOARD_SIZE, ignore_self_captured=False) -> None | game_pb2.GameState:
	board = state.board

	# validate if board index is empty 
	if board[index] != 0:
		return None
	
	# validate if placing this piece violates double free three rule
	if detect_double_free_threes(index, BOARD_SIZE, piece, board):
		return None

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
			is_end=0,
			time_to_think_ns=0
		)

		# check for win condition
		is_end = 0
		if piece == 1:
			if static_eval.check_win_condition(BOARD_SIZE, game_state, 1, new_p1_captures) : is_end = 1
		if piece == 2:
			if static_eval.check_win_condition(BOARD_SIZE, game_state, 2, new_p2_captures) : is_end = 2

		game_state.is_end = is_end

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
		
		# if we want to ignore self captured, return none
		if ignore_self_captured:
			return None
		
		# determine the direction of capture
		fn_mapping = fn_mappings[we_got_captured_idx]

		# turn neighbour cell into blank and increase capture 
		new_board = bytearray(board[:])
		new_board[fn_mapping[1](index, BOARD_SIZE)] = 0
		new_board = bytes(new_board)

		new_p1_captures = state.p1_captures if piece == 1 else state.p1_captures + 1
		new_p2_captures = state.p2_captures if piece == 2 else state.p2_captures + 1

		game_state = game_pb2.GameState(
			board=new_board,
			p1_captures=new_p1_captures,
			p2_captures=new_p2_captures,
			num_turns=state.num_turns + 1,
			is_end=0,
			time_to_think_ns=0
		)

		# check for win condition
		is_end = 0
		if piece == 1:
			if static_eval.check_win_condition(BOARD_SIZE, game_state, 2, new_p2_captures) : is_end = 2
		if piece == 2:
			if static_eval.check_win_condition(BOARD_SIZE, game_state, 1, new_p1_captures) : is_end = 1

		game_state.is_end = is_end

		return game_state
	except:
		pass
	
	new_board = bytearray(board[:])
	# place piece in empty space, TODO check for win and heuristics
	new_board[index] = piece
	new_board = bytes(new_board)

	game_state = game_pb2.GameState(
		board=new_board,
		p1_captures=state.p1_captures,
		p2_captures=state.p2_captures,
		num_turns=state.num_turns + 1,
		is_end=0,
		time_to_think_ns=0
	)

	# check for win condition
	is_end = 0
	if piece == 1:
		if static_eval.check_win_condition(BOARD_SIZE, game_state, 1, state.p1_captures) : is_end = 1
	if piece == 2:
		if static_eval.check_win_condition(BOARD_SIZE, game_state, 2, state.p2_captures) : is_end = 2

	game_state.is_end = is_end

	return game_state

# generates a list of next states based on the initial state given 
# filter_endmoves = if winning endgame moves are generated, only return those moves
def generate_possible_moves(state: game_pb2.GameState, BOARD_SIZE: int, piece: int, filter_endmoves=False) -> list[game_pb2.GameState]:
	curr_board = state.board
	dims = BOARD_SIZE * BOARD_SIZE
	res = []
	indices_to_check = set() # set for no dupes

	# check if state is already endgame, if yes, return none
	if state.is_end != 0:
		return res

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

		# attempt ro place piece in empty space. If such a piece is not valid
		# do not add the move into the result array
		game_state = place_piece_attempt(i, piece, state, BOARD_SIZE, ignore_self_captured=True)
		if game_state is not None:
			res.append(game_state)

	if filter_endmoves:
		winning_moves = list(filter(lambda x: x.is_end == piece, res))
		if len(winning_moves) > 0:
			res = winning_moves

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
			root_children = generate_possible_moves(state, BOARD_SIZE, curr_piece, filter_endmoves=True)
			res.append([state, root_children])
			for state in root_children:
				res.append([state, None])
		else :
			new_leaves = []

			# iterate the adjacency list to find leaves
			for j in range(len(res)):
				if res[j][1] == None:
					# generate children of leaf
					leaf_children = generate_possible_moves(res[j][0], BOARD_SIZE, curr_piece, filter_endmoves=True)
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
		0, 0, 0, 1, 0, 0, 0, 0, 0,
		0, 0, 1, 1, 1, 1, 0, 0, 0,
		0, 0, 0, 2, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 2, 0, 0, 0, 0,
		0, 0, 0, 2, 0, 2, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0
	])

	# p1 is 1, p2 is 2
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=4,
		p2_captures=4,
		num_turns=0,
		is_end=0,
		time_to_think_ns=0
	)

	print(detect_double_free_threes(68, BOARD_SIZE, 2, board))
	# print(has_free_three([0, 0, 0, 0, 0, 0, 0, 0, 0], 1, 8))
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

	# possible_moves = generate_possible_moves(game_state, BOARD_SIZE, 1, filter_endmoves=True)
	# print(f"{len(possible_moves)}")
	# for state in possible_moves:
	# 	pretty_print_board(state.board, BOARD_SIZE)
	# 	print("")

main()
