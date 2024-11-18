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
	curr_depth: int,
	alpha: int = -9999999,
	beta: int = 9999999,
):
	our_piece = max_piece  # max_piece is our piece
	enemy_piece = 2 if our_piece == 1 else 1

	our_captures = curr_state.p1_captures if max_piece == 1 else curr_state.p2_captures
	enemy_captures = curr_state.p2_captures if max_piece == 1 else curr_state.p1_captures

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
		# print(f"curr depth static {curr_depth} is_max? {is_max}")
		return static_eval.static_eval(BOARD_SIZE, curr_state, our_piece, enemy_piece, our_captures, enemy_captures)

	# print(" " * curr_depth * 2 + f"CALLED, is max: {is_max}")
	# utils.pretty_print_board_indent(curr_state.board, BOARD_SIZE, curr_depth)
	# print("")

	# Initialize ideal_score based on whether we're maximizing or minimizing
	move_tree_node = move_tree[state_node_index][0]
	move_tree_children = move_tree[state_node_index][1]
	
	selected_state = None
	if is_max:
		# print(f"curr depth max {curr_depth}")
		ideal_score = -9999999
		for child_state in move_tree_children:
			child_score = minimax_eval(move_tree, child_state, BOARD_SIZE, False, max_piece, curr_depth + 1, alpha, beta)
			if child_score > ideal_score:
				# print(" " * curr_depth * 2 + f"SELECTED {child_score}")
				selected_state = child_state
			ideal_score = max(ideal_score, child_score)
			alpha = max(alpha, ideal_score)
			if beta <= alpha:
				break
	else:
		# print(f"curr depth min {curr_depth}")
		ideal_score = 9999999
		for child_state in move_tree_children:
			child_score = minimax_eval(move_tree, child_state, BOARD_SIZE, True, max_piece, curr_depth + 1, alpha, beta)
			if child_score < ideal_score:
				# print(" " * curr_depth * 2 + f"SELECTED {child_score}")
				selected_state = child_state
			ideal_score = min(ideal_score, child_score)
			beta = min(beta, ideal_score)
			if beta <= alpha:
				break

	# print(" " * curr_depth * 2 + f"returning ideal score {ideal_score}")
	# if selected_state is None:
	# 	print(" " * curr_depth * 2 + "pruned")
	# else:
	# 	utils.pretty_print_board_indent(selected_state.board, BOARD_SIZE, curr_depth)
	# print("")
	return ideal_score # assume current node always has children, since base case is checked

def basic_minimax(state: game_pb2.GameState, BOARD_SIZE: int, curr_piece: int, max_piece: int) -> game_pb2.GameState:
	# we can afford to do depth 2 if still early game
	depth = 3 if state.num_turns > 4 else 2
	# generate move tree / get move tree from cache
	move_tree = move_generation.generate_move_tree(state, BOARD_SIZE, curr_piece, depth)
	root_node = move_tree[0][0] # garentee
	root_children = move_tree[0][1]
	max_score = -999999999
	max_score_idx = -1

	# iterate roots children and call minimax_eval, record the scores and pick the max one 
	# curr_piece != max_piece always false ??
	for i in range(len(root_children)):
		child = root_children[i]
		child_score = minimax_eval(move_tree, child, BOARD_SIZE, curr_piece != max_piece, max_piece, 0)
		if child_score > max_score:
			max_score = child_score
			max_score_idx = i

	# print(f"{root_node.board == state.board} max_score_idx {max_score_idx}")
	return root_children[max_score_idx]

@utils.measure_duration_ns
def main():
	
	# # some metadata here
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

	BOARD_SIZE = 10

	board = bytes([
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	])


	# p0 is 1, p1 is 2
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=0,
		p2_captures=0,
		num_turns=1,
		is_end=False,
		time_to_think_ns=0
	)
	suggested_state = basic_minimax(game_state, BOARD_SIZE, 2, 2)
	utils.pretty_print_board(suggested_state.board, BOARD_SIZE)
main()