import grpc
from flask import Flask, render_template, jsonify, request
import game_pb2_grpc
import game_pb2
import utils
import static_eval
import move_generation

class GomokuClient:
	def __init__(self):
		self.app = Flask('game_app', template_folder='./frontend/templates')
		self.channel = grpc.insecure_channel('localhost:50051')
		self.stub = game_pb2_grpc.GameStub(self.channel)
		self.board_size = 19
		self.meta = self.stub.GetGameMeta(game_pb2.Empty()) # TODO: should we decrecate this?
		self.game_state = self.stub.GetLastGameState(game_pb2.Empty())
		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		self.mode = None
		self.variant = None

		# Render endpoints
		self.app.add_url_rule('/', 'index', self.render_index)
		self.app.add_url_rule('/game', 'game', self.render_game)

		# State retrival / modification endpoints
		self.app.add_url_rule('/set_config', 'set_config', self.set_config, methods=['POST'])
		self.app.add_url_rule('/suggest_move', 'suggest_move', self.suggest_move, methods=['POST'])
		self.app.add_url_rule('/move', 'move', self.move, methods=['POST'])
		self.app.add_url_rule('/move_pvp', 'move_pvp', self.move_pvp, methods=['POST'])
		self.app.add_url_rule('/board', 'get_board', self.get_board)
		self.app.add_url_rule('/static_eval', 'get_static_eval', self.get_static_eval)
		self.app.add_url_rule('/reset', 'reset', self.reset, methods=['POST'])

	# returns true if a capture is possible by me if i place curr_piece in idx
	def check_capture_made_dir(self, direction_fn, idx, board, our_piece):
		check_cell_idx = direction_fn(idx, self.board_size)
		check_cell = board[check_cell_idx]
		# gets cell at direction_fn, if its enemy
		if check_cell > 0 and check_cell != our_piece:
			# gets cell at direction_fn again
			check_cell_idx = direction_fn(check_cell_idx, self.board_size)
			check_cell = board[check_cell_idx]
			# if its still enemy
			if check_cell > 0 and check_cell != our_piece:
				# gets cell at direction_fn again
				check_cell_idx = direction_fn(check_cell_idx, self.board_size)
				check_cell = board[check_cell_idx]
				# if its ally
				if check_cell == our_piece:
					return True
		return False

	def render_index(self):
		return render_template('index.html')

	def render_game(self):
		# TODO evaluators wont check error handling for uninit values right??
		return render_template('game.html',
						board=self.board,
						board_size=self.board_size,
						mode = self.mode,
						variant = self.variant
						)

	def set_config(self):
		variant = request.form['variant']
		mode = request.form['mode']
		# TODO call to backend to set game meta

		self.mode = mode
		self.variant = variant
		return jsonify(status=200)

	def get_board(self):
		return jsonify(
			board=self.board,
			p1_captures=self.game_state.p1_captures,
			p2_captures=self.game_state.p2_captures,
			is_end = self.game_state.is_end,
			num_turns = self.game_state.num_turns
			)

	def get_static_eval(self):
		p1_eval = static_eval.static_eval(self.board_size, self.game_state, 1, 2, self.game_state.p1_captures, self.game_state.p2_captures)
		p2_eval = static_eval.static_eval(self.board_size, self.game_state, 2, 1, self.game_state.p1_captures, self.game_state.p2_captures)
		
		return jsonify(
			p1_eval=p1_eval,
			p2_eval=p2_eval
		)

	def reset(self):
		self.meta = self.stub.GetGameMeta(game_pb2.Empty()) # TODO: should we decrecate this?
		self.game_state = self.stub.GetLastGameState(game_pb2.Empty())
		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		self.mode = None
		self.variant = None

		self.stub.Reset(game_pb2.Empty())

		return jsonify(status=200)
	
	# Make a player move in AI mode and expect
	# an AI move in response
	def move(self):
		x = int(request.form['x'])
		y = int(request.form['y'])
		index = y * self.board_size + x  # Convert to 1D index

		# capture checking here
		board_copy = bytearray(self.game_state.board[:])
		
		# validate if placing such a piece will capture opponenet
		captured_validation_res = []
		fn_mappings = [
			(0, utils.get_btm_idx),
			(1, utils.get_top_idx),
			(2, utils.get_left_idx),
			(3, utils.get_right_idx),
			(4, utils.get_btm_left_idx),
			(5, utils.get_top_right_idx),
			(6, utils.get_top_left_idx),
			(7, utils.get_btm_right_idx)
		]
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[0][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[1][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[2][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[3][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[4][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[5][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[6][1], index, board_copy, 1))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[7][1], index, board_copy, 1))
		we_captured_indices = []
		for (idx, elem) in enumerate(captured_validation_res):
			if elem is True:
				we_captured_indices.append(idx)
		if len(we_captured_indices) > 0:
			for we_captured_idx in we_captured_indices:
				# determine the direction of capture
				fn_mapping = fn_mappings[we_captured_idx]

				# turn neighbour cell into blank, fill curr blank and increase capture
				idx1 = fn_mapping[1](index, self.board_size)
				idx2 = fn_mapping[1](idx1, self.board_size)
				board_copy[idx1] = 0
				board_copy[idx2] = 0
				self.game_state.p1_captures += 1

		board_copy[index] = 1 # we are player 1, AI is 2
			
		# validate to deny double free three
		if move_generation.detect_double_free_threes(index, self.board_size, 1, board_copy) :
			return jsonify(status=400, message="Double free three")

		# apply new changes to board and increment turn count
		self.game_state.board = bytes(board_copy)
		self.game_state.num_turns += 1

		# check win from calling player here. Dont need to wait for 
		# ai to return move. 
		if static_eval.check_win_condition(self.board_size, self.game_state, 1, self.game_state.p1_captures) :
			self.game_state.is_end = 1
			self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
			return jsonify(status=200)

		print("suggesting next move for")
		utils.pretty_print_board(board_copy, self.board_size)

		next_move_state = self.stub.SuggestNextMove(self.game_state)
		self.game_state = next_move_state

		# print("suggested")
		# utils.pretty_print_board(self.game_state.board, self.board_size)
		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		return jsonify(status=200)

	def suggest_move(self):
		curr_piece = 1 if self.game_state.num_turns % 2 == 0 else 2

		print("suggesting next move for")
		board_copy = bytearray(self.game_state.board[:])
		utils.pretty_print_board(board_copy, self.board_size)

		if self.game_state.num_turns == 0:
			print("Opening is not set yet, not suggesting any move")
			return jsonify(status=200, index=-1)

		suggested_state = self.stub.SuggestNextMove(self.game_state)
		print("suggested")
		utils.pretty_print_board(suggested_state.board, self.board_size)
		res = -1
		for (idx, elem) in enumerate(suggested_state.board):
			if elem == curr_piece:
				if board_copy[idx] != curr_piece:
					res = idx
					break

		return jsonify(status=200, index=res)

	# Make a player move in Pvp mode
	def move_pvp(self):
		x = int(request.form['x'])
		y = int(request.form['y'])
		our_piece = int(request.form['piece'])
		index = y * self.board_size + x  # Convert to 1D index

		# capture checking here
		board_copy = bytearray(self.game_state.board[:])

		# validate if placing such a piece will capture opponenet
		captured_validation_res = []
		fn_mappings = [
			(0, utils.get_btm_idx),
			(1, utils.get_top_idx),
			(2, utils.get_left_idx),
			(3, utils.get_right_idx),
			(4, utils.get_btm_left_idx),
			(5, utils.get_top_right_idx),
			(6, utils.get_top_left_idx),
			(7, utils.get_btm_right_idx)
		]

		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[0][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[1][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[2][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[3][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[4][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[5][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[6][1], index, board_copy, our_piece))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[7][1], index, board_copy, our_piece))
		we_captured_indices = []
		for (idx, elem) in enumerate(captured_validation_res):
			if elem is True:
				we_captured_indices.append(idx)
		if len(we_captured_indices) > 0:
			for we_captured_idx in we_captured_indices:
				# determine the direction of capture
				fn_mapping = fn_mappings[we_captured_idx]

				# turn neighbour cell into blank, fill curr blank and increase capture
				idx1 = fn_mapping[1](index, self.board_size)
				idx2 = fn_mapping[1](idx1, self.board_size)
				board_copy[idx1] = 0
				board_copy[idx2] = 0
				if our_piece == 1:
					self.game_state.p1_captures += 1
				else:
					self.game_state.p2_captures += 1
		
		board_copy[index] = our_piece
			
		# validate to deny double free three
		if move_generation.detect_double_free_threes(index, self.board_size, our_piece, board_copy) :
			return jsonify(status=400, message="Double free three")
		
		# apply new changes to board and increment turn count
		self.game_state.board = bytes(board_copy)
		self.game_state.num_turns += 1

		# check win from calling player here.
		our_captures = self.game_state.p1_captures
		if our_piece == 2:
			our_captures = self.game_state.p2_captures
		if static_eval.check_win_condition(self.board_size, self.game_state, our_piece, our_captures) :
			self.game_state.is_end = our_piece
			self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
			return jsonify(status=200)

		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		return jsonify(status=200)

	def bytes_to_int_array(self, byte_array):
		return [b for b in byte_array]

	def convert_to_2d(self, board_1d, size):
		return [board_1d[i:i + size] for i in range(0, len(board_1d), size)]


game_app = GomokuClient()
game_app.app.run(debug=True)