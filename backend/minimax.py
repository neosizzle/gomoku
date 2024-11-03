import game_pb2_grpc
import game_pb2
import utils
import move_generation
import static_eval

def minimax_eval(
	move_tree: list[list[game_pb2.GameState | list[game_pb2.GameState]]],
	curr_state: game_pb2.GameState,
	BOARD_SIZE: int,
	is_max: bool,
	max_piece: int,
	alpha: int = -9999999,
	beta: int = 9999999
):
	our_piece = max_piece  # max_piece is our piece
	enemy_piece = 2 if our_piece == 1 else 1

	our_captures = curr_state.p0_captures if max_piece == 1 else curr_state.p1_captures
	enemy_captures = curr_state.p1_captures if max_piece == 1 else curr_state.p0_captures

	# Check if the current state exists in the move tree
	state_node_index = -1
	for i in range(len(move_tree)):
		if move_tree[i][1] is None:
			continue
		if move_tree[i][0].board == curr_state.board and len(move_tree[i][1]) > 0:
			state_node_index = i
			break

	# If no valid state found, perform static evaluation
	if state_node_index == -1:
		return static_eval.static_eval(BOARD_SIZE, curr_state, our_piece, enemy_piece, our_captures, enemy_captures)

	# Initialize ideal_score based on whether we're maximizing or minimizing
	move_tree_node = move_tree[state_node_index][0]
	move_tree_children = move_tree[state_node_index][1]
	
	if is_max:
		ideal_score = -9999999
		for child_state in move_tree_children:
			child_score = minimax_eval(move_tree, child_state, BOARD_SIZE, False, max_piece, alpha, beta)
			ideal_score = max(ideal_score, child_score)
			alpha = max(alpha, ideal_score)
			if beta <= alpha:
				break
	else:
		ideal_score = 9999999
		for child_state in move_tree_children:
			child_score = minimax_eval(move_tree, child_state, BOARD_SIZE, True, max_piece, alpha, beta)
			ideal_score = min(ideal_score, child_score)
			beta = min(beta, ideal_score)
			if beta <= alpha:
				break

	return ideal_score

@move_generation.measure_duration_ns
def basic_minimax(state: game_pb2.GameState, BOARD_SIZE: int, curr_piece: int, max_piece: int) -> game_pb2.GameState:
	depth = 3
	# generate move tree / get move tree from cache
	move_tree = move_generation.generate_move_tree(state, BOARD_SIZE, curr_piece, depth)
	root_node = move_tree[0][0] # garentee
	root_children = move_tree[0][1]
	max_score = -1
	max_score_idx = -1

	# iterate roots children and call minimax_eval, record the scores and pick the max one 
	for i in range(len(root_children)):
		child = root_children[i]
		child_score = minimax_eval(move_tree, child, BOARD_SIZE, curr_piece == max_piece, max_piece)
		if child_score > max_score:
			max_score = child_score
			max_score_idx = i

	print(f"{root_node.board == state.board}")
	return root_children[max_score_idx]

# def main():
	
# 	# # some metadata here
# 	# BOARD_SIZE = 19

# 	# board = bytes([
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# 	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 	# ]
# 	# )

# 	BOARD_SIZE = 9

# 	board = bytes([
# 		0, 0, 0, 0, 0, 0, 0, 0, 0,
# 		0, 0, 0, 0, 0, 0, 0, 0, 0,
# 		0, 0, 0, 0, 0, 0, 0, 0, 0,
# 		0, 0, 0, 0, 0, 0, 2, 0, 0,
# 		0, 0, 0, 0, 0, 0, 2, 0, 1,
# 		0, 0, 0, 0, 0, 0, 2, 0, 0,
# 		0, 0, 0, 0, 0, 0, 2, 0, 0,
# 		0, 0, 0, 0, 0, 2, 1, 1, 1,
# 		0, 0, 0, 0, 0, 0, 0, 0, 0
# 	])


# 	# p0 is 1, p1 is 2
# 	game_state = game_pb2.GameState(
# 		board=board,
# 		p1_captures=0,
# 		p0_captures=0,
# 		num_turns=0,
# 		is_end=False,
# 		time_to_think_ns=0
# 	)
# 	suggested_state = basic_minimax(game_state, BOARD_SIZE, 1, 1)
# 	utils.pretty_print_board(suggested_state.board, BOARD_SIZE)
# main()