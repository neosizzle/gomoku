import grpc
from flask import Flask, render_template, jsonify, request
import game_pb2_grpc
import game_pb2


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


	def index(self):
		return render_template('test.html', board=self.board, board_size=self.board_size)

	def get_board(self):
		return jsonify(board=self.board)

	def move(self):
		x = int(request.form['x'])
		y = int(request.form['y'])
		index = y * self.board_size + x  # Convert to 1D index
		
		# TODO: capture checking here
		board_copy = bytearray(self.game_state.board[:])
		board_copy[index] = 1 # we are player 1, AI is 2
		self.game_state.board = bytes(board_copy)
		self.game_state.num_turns += 1
	
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