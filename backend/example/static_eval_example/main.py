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

def calculate_gap_penalty(start_idx, end_idx, extraction, our_piece):
	penalty_end_idx = start_idx
	penalty_start_idx = start_idx
	res = 0
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
			res += 1
	return res

def calculate_open_bonus(extraction, our_piece, moves_next):
	res = 0
	start = -1

	while start < len(extraction) - 1:
		start += 1
		gap = 0
		power = 3
		cum_count = 1

		# keep going until start hits our piece
		if extraction[start] != our_piece :
			continue

		# we hit our piece, check for left edge and left enemy
		if start == 0 or extraction[start - 1] != 0:
			power -= 1
		
		# move start until the end of combo, counting our pieces
		while start < len(extraction):
			start += 1
			if start == len(extraction) or extraction[start] != our_piece:
				break
			if extraction[start] == 0:
				if gap == 0:
					gap += 1
					continue
				else:
					break
			cum_count += 1

		# check if we end the combo at an edge / enemy
		if start == len(extraction) or extraction[start] != 0:
			power -= 1

		# print(f'cum_count {cum_count} power {power}')
		res += pow(cum_count, power)

	# bonus multiplier if we are moving next
	if moves_next == our_piece:
		return res * res
	return res

# TODO optimize this, can check win condition here and can also calculate enemy score
def static_eval_directional(BOARD_SIZE, game_state, our_piece, enemy_piece, moves_next):
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

				# Move end idx to enemy piece or edge
				if end_idx == len(extraction):
						break
				while extraction[end_idx] != enemy_piece:
					end_idx += 1
					if end_idx == len(extraction):
						break
				
				# Extract section
				section = extraction[start_idx:end_idx]
				# print(f"{section}")

				# count number of my pieces in section and append score
				num_pieces_section = section.count(our_piece)
				extraction_score += (num_pieces_section)

				# incur penalty on big gaps on our combos (LOW SENSITIVITY)
				extraction_score -= calculate_gap_penalty(start_idx, end_idx, extraction, our_piece)
				
				# move start_idx to curr end_index
				start_idx = end_idx
			# incur bonus on open combos and next move advantage (HIGH SENSITIVITY)
			# print(f"{extraction} {our_piece} {moves_next} {calculate_open_bonus(extraction, our_piece, moves_next)}")
			extraction_score += calculate_open_bonus(extraction, our_piece, moves_next)
			total_score += extraction_score
		# print(total_score)
		score_res += total_score

	return score_res


def check_win_condition(BOARD_SIZE, game_state, our_piece, our_captures):
	board = game_state.board
	
	if our_captures >= 5:
		return True
	
	# generate indices for all directions
	all_indices_directions = []
	all_indices_directions.append(generate_row_indices(BOARD_SIZE))
	all_indices_directions.append(generate_column_indices(BOARD_SIZE))
	all_indices_directions.append(generate_diag_indices_inverse(BOARD_SIZE))
	all_indices_directions.append(generate_diag_indices(BOARD_SIZE))

	for direction_indices in all_indices_directions:
		# extract cells in  direction
		direction_cells = extract_dimensional_cells(board, direction_indices)
		
		for extraction_idx, extraction in enumerate(direction_cells):
			# count cumulative pieces
			cum_count = 0
			for cell in extraction:
				if cell == our_piece:
					cum_count += 1
				else:
					cum_count = 0
				
				if cum_count >= 5:
					if check_win_comb_nocap(BOARD_SIZE, board, direction_indices[extraction_idx]):
						return True
	return False

# Takes directional functions and make sure that there wont be any potential captures by enemy in the next round
# returns true if there isnt any potential captures
def validate_potential_nocap_direction(direction_fn,anti_direction_fn, idx, board_size, curr_piece, board):
	
	check_cell_idx = direction_fn(idx, board_size)
	check_cell = board[check_cell_idx]

	# returns true (OK) if curr piece is not playable
	if curr_piece != 1 and curr_piece != 2:
		return True

	# gets cell at direction_fn, if its curr_piece
	if check_cell == curr_piece:
		# get cell to the new pieces direction_fn. if its enemy, 
		check_neigh_cell = board[direction_fn(check_cell_idx, board_size)]
		if check_neigh_cell != curr_piece and check_neigh_cell != 0:
			# get cell to the original cells anti_direction_fn
			anti_direct_cell = board[anti_direction_fn(idx, board_size)]
			if anti_direct_cell != curr_piece and anti_direct_cell == 0:
				return False
			
	# if cell at diretion fn aint curr_piece and its not space or border and not curr piece,
	# means this is enemy
	if check_cell != 0 and check_cell != -1 and check_cell != curr_piece:
		# get the neighbour at anti_dir in the original index
		anti_dir_idx = anti_direction_fn(idx, board_size)
		check_neigh_cell = board[anti_dir_idx]
		
		# if its curr_piece, check anti direction again
		if check_neigh_cell == curr_piece:
			check_neigh_cell = board[anti_direction_fn(anti_dir_idx, board_size)]

			# if its blank, return false
			if check_neigh_cell == 0:
				return False
	return True

# function to check if a win combination is valid. Retuns true if valid
def check_win_comb_nocap(BOARD_SIZE, board, indices_to_check):
	endgame_cap_validation_res = []
	for cum_index in indices_to_check:
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_btm_idx, get_top_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_top_idx, get_btm_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_left_idx, get_right_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_right_idx, get_left_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_btm_left_idx, get_top_right_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_top_right_idx, get_btm_left_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_top_left_idx, get_btm_right_idx, cum_index, BOARD_SIZE, board[cum_index], board))
		endgame_cap_validation_res.append(validate_potential_nocap_direction(get_btm_right_idx, get_top_left_idx, cum_index, BOARD_SIZE, board[cum_index], board))
	return endgame_cap_validation_res.count(False) == 0

def static_eval(BOARD_SIZE, game_state, our_piece, enemy_piece, our_captures, enemy_captures):
	moves_next = 1 if game_state.num_turns % 2 == 0 else 2 	# see who moves next, will have advantage. Assumes p1 always moves first
	print(f'moves next {moves_next}')

	my_score = static_eval_directional(BOARD_SIZE, game_state, our_piece, enemy_piece, moves_next)
	# my_score = -1
	print(f"my_score {my_score}")
	final_score = my_score
	final_score += our_captures * 2


	enemy_score = static_eval_directional(BOARD_SIZE, game_state, enemy_piece, our_piece, moves_next)
	# enemy_score = -1
	print(f"enemy_score {enemy_score}")
	final_score -= enemy_score
	final_score -= enemy_captures * 2

	if check_win_condition(BOARD_SIZE, game_state, 1, game_state.p1_captures):
		if our_piece == 1:
			final_score += 6969
		else:
			final_score -= 6969

	if check_win_condition(BOARD_SIZE, game_state, 2, game_state.p2_captures):
		if our_piece == 2:
			final_score += 6969
		else:
			final_score -= 6969

	pretty_print_board(game_state.board, BOARD_SIZE)
	print("==========================")
	return final_score

def main():
	
	# some metadata here
	BOARD_SIZE = 10

	board = bytes([
		1, 1, 1, 1, 0, 0, 0, 0, 0, 0,
		1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		1, 0, 0, 1, 0, 0, 0, 0, 0, 0,
		0, 0, 1, 1, 1, 1, 1, 0, 0, 0,
		0, 0, 2, 0, 0, 0, 2, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	]
	)
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=4,
		p2_captures=3,
		num_turns=0,
		is_end=False,
		time_to_think_ns=0
	)

	# check_valid_win_combo(BOARD_SIZE, game_state)
	# print(f"{calculate_open_bonus([0, 0, 0, 0, 0, 0, 0, 0, 1], 1, 2)}")

	score = static_eval(BOARD_SIZE, game_state, 2, 1, game_state.p2_captures, game_state.p1_captures)
	# score = 123

	print(f"score {score}, 1 won? {check_win_condition(BOARD_SIZE, game_state, 1, game_state.p1_captures)}, 2 won? {check_win_condition(BOARD_SIZE, game_state, 2, game_state.p2_captures)}")
	# print(validate_potential_nocap_direction(get_right_idx, get_left_idx, 31, BOARD_SIZE, board[31], board))

main()