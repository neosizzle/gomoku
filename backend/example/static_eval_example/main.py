import grpc
import time

import game_pb2_grpc
import game_pb2

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

def cell_scoring(board, idx, our_piece):
	if board[idx] == our_piece:
		return 1
	return -1

def flood_fill_score(BOARD_SIZE, board, score_matrix, idx, our_piece, curr_piece, traverse_cache):
	# print(f"top {get_top_idx(idx, BOARD_SIZE)} btm {get_btm_idx(idx, BOARD_SIZE)} left {get_left_idx(idx, BOARD_SIZE)} right {get_right_idx(idx, BOARD_SIZE)}") # Tested OK
	# print(f"topl {get_top_left_idx(idx, BOARD_SIZE)} btml {get_btm_left_idx(idx, BOARD_SIZE)} topr {get_top_right_idx(idx, BOARD_SIZE)} btmr {get_btm_right_idx(idx, BOARD_SIZE)}") # Tested OK

	# if we have been here before or the current piece is not ours, return
	if traverse_cache[idx] != 0 or board[idx] != curr_piece:
		return

	traverse_cache[idx] = 1

	# traverse all directions
	top_idx = get_top_idx(idx, BOARD_SIZE)
	if top_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, top_idx, our_piece, curr_piece, traverse_cache)

	btm_idx = get_btm_idx(idx, BOARD_SIZE)
	if btm_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, btm_idx, our_piece, curr_piece, traverse_cache)

	left_idx = get_left_idx(idx, BOARD_SIZE)
	if left_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, left_idx, our_piece, curr_piece, traverse_cache)

	right_idx = get_right_idx(idx, BOARD_SIZE)
	if right_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, right_idx, our_piece, curr_piece, traverse_cache)

	top_right_idx = get_top_right_idx(idx, BOARD_SIZE)
	if top_right_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, top_right_idx, our_piece, curr_piece, traverse_cache)

	top_left_idx = get_top_left_idx(idx, BOARD_SIZE)
	if top_left_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, top_left_idx, our_piece, curr_piece, traverse_cache)

	btm_right_idx = get_btm_right_idx(idx, BOARD_SIZE)
	if btm_right_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, btm_right_idx, our_piece, curr_piece, traverse_cache)

	btm_left_idx = get_btm_left_idx(idx, BOARD_SIZE)
	if btm_left_idx != -1:
		flood_fill_score(BOARD_SIZE, board, score_matrix, btm_left_idx, our_piece, curr_piece, traverse_cache)

	# scoring
	score_matrix[idx] = cell_scoring(board, idx, our_piece)

# we are maximizing for p1 here (piece 2)
def static_eval_flood(BOARD_SIZE, game_state, our_piece):
	dimension = (BOARD_SIZE * BOARD_SIZE)
	score_matrix = [0] * dimension
	board = game_state.board
	
	for i in range(dimension):
		# current cell is empty or we have scored this cell before, skip
		if board[i] == 0 or score_matrix[i] != 0:
			continue
		print(f"start fill @ idx {i}")
		flood_fill_score(BOARD_SIZE, board, score_matrix, i, our_piece, board[i], [0] * dimension)


	# TODO add captures to final score
	pretty_print_board(game_state.board, BOARD_SIZE)
	print("==========================")
	pretty_print_board(score_matrix, BOARD_SIZE)
	return sum(score_matrix)

def extract_dimensional_cells(board, row_indices):
    direction_cells = []
    for row_index_set in row_indices:
        row_cells = []
        for index in row_index_set:
            row_cells.append(board[index])
        direction_cells.append(row_cells)
    return direction_cells

def generate_row_indices(board_size):
    row_indices = []
    for i in range(board_size):
        curr_row = []
        for j in range(board_size):
            curr_row.append(i * board_size + j)
        row_indices.append(curr_row)
    return row_indices

def generate_column_indices(board_size):
    column_indices = []
    for i in range(board_size):
        curr_col = []
        for j in range(board_size):
            curr_col.append(i + (board_size * j))
        column_indices.append(curr_col)
    return column_indices

def generate_diag_indices(board_size):
	diag_indices = []
	combs = board_size + (board_size - 1)
	counter = 1
	direction_up = True
	for i in range(combs):
		# start case, the first elem is always 0
		if i == 0:
			diag_indices.append([0])
			counter += 1
			continue
		
		smallest_elem = 0
		# if direction is up, take the smallest of the last elemnt, else  2nd smallest
		if direction_up:
			smallest_elem = diag_indices[i - 1][0] + 1
		else:
			smallest_elem = diag_indices[i - 1][1] + 1

		# iterate through counter and append alements
		buffer = []
		for i in range(counter):
			buffer.append(smallest_elem + (i * (board_size - 1)))
		diag_indices.append(buffer)

		# if direction is up, check for peak and increment counter. If peak reached, change direction and decrement counter
		if direction_up:
			if counter == board_size:
				counter -= 1
				direction_up = False
			else:
				counter += 1

		# if direction is down, decrem counter
		else:
			counter -= 1
	return diag_indices

def generate_diag_indices_inverse(board_size):
	diag_indices = []
	combs = board_size + (board_size - 1)
	counter = 1
	direction_up = True
	for i in range(combs):
		# start case, the first elem is always last elem of first row
		if i == 0:
			diag_indices.append([board_size - 1])
			counter += 1
			continue
		
		smallest_elem = 0
		# if direction is up, take the smallest of the last elemnt, else  2nd smallest
		if direction_up:
			smallest_elem = diag_indices[i - 1][0] - 1
		else:
			smallest_elem = diag_indices[i - 1][1] - 1

		# iterate through counter and append alements
		buffer = []
		for i in range(counter):
			buffer.append(smallest_elem + (i * (board_size + 1)))
		diag_indices.append(buffer)

		# if direction is up, check for peak and increment counter. If peak reached, change direction and decrement counter
		if direction_up:
			if counter == board_size:
				counter -= 1
				direction_up = False
			else:
				counter += 1

		# if direction is down, decrem counter
		else:
			counter -= 1
	return diag_indices

# we are maximizing for p1 here (piece 2)
def static_eval_directional(BOARD_SIZE, game_state, our_piece, enemy_piece):
	dimension = (BOARD_SIZE * BOARD_SIZE)
	board = game_state.board
	num_our_piece = board.count(our_piece)
	score_res = num_our_piece

	# generate indices for all directions
	all_indices_directions = []
	all_indices_directions.append(generate_row_indices(BOARD_SIZE))
	all_indices_directions.append(generate_column_indices(BOARD_SIZE))
	all_indices_directions.append(generate_diag_indices_inverse(BOARD_SIZE))
	all_indices_directions.append(generate_diag_indices(BOARD_SIZE))

	for direction_indices in all_indices_directions:
		# extract cells in  direction
		direction_cells = extract_dimensional_cells(board, direction_indices)

		# score each extraction
		total_score = 0
		for extraction in direction_cells:
			start_idx = 0
			end_idx = 0
			extraction_score = 0
			while start_idx < len(extraction):
				# print(f"Start {start_idx}")
				# Move start idx to our piece
				while extraction[start_idx] != our_piece :
					start_idx += 1
					if start_idx == len(extraction):
						break

				end_idx = start_idx

				# Move end idx to enemy piece
				if end_idx == len(extraction):
						break
				while extraction[end_idx] != enemy_piece:
					end_idx += 1
					if end_idx == len(extraction):
						break
				
				# Extract section
				section = extraction[start_idx:end_idx]
				print(f"{section}")

				# count number of my pieces in section and append score
				num_pieces_section = section.count(our_piece)
				extraction_score += (num_pieces_section) * 2

				# incur penalty on big gaps
				penalty_end_idx = start_idx
				penalty_start_idx = start_idx
				while penalty_end_idx != end_idx:
					# move penalty_end to either the blank or end 
					while penalty_end_idx != end_idx and extraction[penalty_end_idx] != 0:
						penalty_end_idx += 1

					# if penalty_end is at end already, can break, should be no more penalty
					if penalty_end_idx == end_idx:
						break

					# move penalty_end to the next non-blank symbol
					while penalty_end_idx != end_idx and extraction[penalty_end_idx] == 0:
						penalty_end_idx += 1

					# if penalty_end is at end already, can break, should be no more penalty
					if penalty_end_idx == end_idx:
						break

					# can assume penalty_end is at enemy piece now, move penalty start to a non - our piece
					while extraction[penalty_start_idx] == our_piece:
						penalty_start_idx += 1

					# can assume that penalty_end is actually bigger than penalty_start now, get diff
					# if diff is more than winning  piece count, incur 1 point penalty
					diff = penalty_end_idx - penalty_start_idx
					if diff > 4 :
						extraction_score -= 1

				# move start_idx to curr end_index
				start_idx = end_idx
			total_score += extraction_score
		print(total_score)
		score_res += total_score



	# TODO add captures to final score
	pretty_print_board(game_state.board, BOARD_SIZE)
	print("==========================")
	return score_res

def main():
	
	# some metadata here
	BOARD_SIZE = 10

	board = bytes([
		1, 1, 1, 0, 0, 0, 0, 0, 0, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 2, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	]
	)
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=0,
		p0_captures=0,
		num_turns=0,
		is_end=False,
		time_to_think_ns=0
	)

	score = static_eval_directional(BOARD_SIZE, game_state, 1, 2)

	print(f"score {score}")

main()