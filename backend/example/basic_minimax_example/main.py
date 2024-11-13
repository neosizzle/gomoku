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
		):
	our_piece = max_piece # max_piece is our piece
	enemy_piece = -1
	if our_piece == 1:
		enemy_piece = 2
	else:
		enemy_piece = 1

	our_captures = -1
	enemy_captures = -1
	if max_piece == 1:
		our_captures = curr_state.p0_captures
		enemy_captures = curr_state.p1_captures
	else:
		our_captures = curr_state.p1_captures
		enemy_captures = curr_state.p0_captures
		
	# if i cant find state in tree or state in tree has no children, do static eval
	state_node_index = -1
	for i in range(len(move_tree)):
		if move_tree[i][1] == None:
			continue
		if move_tree[i][0].board == curr_state.board and len(move_tree[i][1]) > 0:
			state_node_index = i
	if state_node_index == -1:
		return static_eval.static_eval(BOARD_SIZE, curr_state, our_piece, enemy_piece, our_captures, enemy_captures)
	
	# call minimax eval on all childred
	ideal_score = 0
	if is_max:
		ideal_score = -9999999
	else:
		ideal_score = 99999999
	move_tree_node = move_tree[state_node_index][0]
	move_tree_children = move_tree[state_node_index][1]
	for i in range(len(move_tree_children)):
		child_state = move_tree_children[i]
		child_score = minimax_eval(move_tree, child_state, BOARD_SIZE, not is_max, max_piece)
		if is_max:
			if child_score > ideal_score:
				ideal_score = child_score
		else:
			if child_score < ideal_score:
				ideal_score = child_score
	return ideal_score # assume current node always has children, since base case is checked

def basic_minimax(state: game_pb2.GameState, BOARD_SIZE: int, curr_piece: int, max_piece: int) -> game_pb2.GameState:
	depth = 2
	# generate move tree / get move tree from cache
	move_tree = move_generation.generate_move_tree(state, BOARD_SIZE, curr_piece, depth)
	root_node = move_tree[0][0] # garentee
	root_children = move_tree[0][1]
	max_score = -999999999
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

	BOARD_SIZE = 9

	board = bytes([
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 2, 0, 0,
		0, 0, 0, 0, 0, 0, 2, 0, 1,
		0, 0, 0, 0, 0, 0, 2, 0, 0,
		0, 0, 0, 0, 0, 0, 2, 0, 0,
		0, 0, 0, 0, 0, 2, 1, 1, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0
	])


	# p0 is 1, p1 is 2
	game_state = game_pb2.GameState(
		board=board,
		p1_captures=0,
		p0_captures=0,
		num_turns=0,
		is_end=False,
		time_to_think_ns=0
	)
	suggested_state = basic_minimax(game_state, BOARD_SIZE, 1, 1)
	utils.pretty_print_board(suggested_state.board, BOARD_SIZE)
main()