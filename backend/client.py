import grpc
from flask import Flask, render_template, jsonify, request
import game_pb2_grpc
import game_pb2
import utils

class GomokuClient:
	def __init__(self):
		self.app = Flask('game_app', template_folder='./backend/templates')
		self.channel = grpc.insecure_channel('localhost:50051')
		self.stub = game_pb2_grpc.GameStub(self.channel)
		self.board_size = 10
		self.meta = self.stub.GetGameMeta(game_pb2.Empty())
		self.game_state = self.stub.GetLastGameState(game_pb2.Empty())
		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		self.app.add_url_rule('/', 'index', self.index)
		self.app.add_url_rule('/move', 'move', self.move, methods=['POST'])
		self.app.add_url_rule('/board', 'get_board', self.get_board)

	# returns true if a capture is possible by me if i place curr_piece in idx
	def check_capture_made_dir(self, direction_fn, idx, board):
		check_cell_idx = direction_fn(idx, self.board_size)
		check_cell = board[check_cell_idx]
		# gets cell at direction_fn, if its enemy
		if check_cell > 0 and check_cell != 1:
			# gets cell at direction_fn again
			check_cell_idx = direction_fn(check_cell_idx, self.board_size)
			check_cell = board[check_cell_idx]
			# if its still enemy
			if check_cell > 0 and check_cell != 1:
				# gets cell at direction_fn again
				check_cell_idx = direction_fn(check_cell_idx, self.board_size)
				check_cell = board[check_cell_idx]
				# if its ally
				if check_cell == 1:
					return True
		return False

	def index(self):
		return render_template('test.html', board=self.board, board_size=self.board_size)

	def get_board(self):
		return jsonify(board=self.board)

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
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[0][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[1][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[2][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[3][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[4][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[5][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[6][1], index, board_copy))
		captured_validation_res.append(self.check_capture_made_dir(fn_mappings[7][1], index, board_copy))
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

		# TODO validate if we get captured

		board_copy[index] = 1 # we are player 1, AI is 2
		self.game_state.board = bytes(board_copy)
		self.game_state.num_turns += 1
	
		print("suggesting next move for")
		utils.pretty_print_board(board_copy, self.board_size)

		next_move_state = self.stub.SuggestNextMove(self.game_state)
		self.game_state = next_move_state

		self.board = self.convert_to_2d(self.bytes_to_int_array(self.game_state.board), self.board_size)
		return jsonify(status=200)

	def bytes_to_int_array(self, byte_array):
		return [b for b in byte_array]

	def convert_to_2d(self, board_1d, size):
		return [board_1d[i:i + size] for i in range(0, len(board_1d), size)]


game_app = GomokuClient()
game_app.app.run(debug=True)