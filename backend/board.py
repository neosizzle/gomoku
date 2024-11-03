import grpc
import game_pb2_grpc
import game_pb2
from concurrent import futures
import time
from google.protobuf.wrappers_pb2 import BoolValue
import minimax
class GomokuGame(game_pb2_grpc.GameServicer):
	def __init__(self):
		self.size = 19
		self.board = [0] * (self.size * self.size)
		self.current_player = 1
		self.captures = {'1': 0, '2': 0}
		self.num_turns = 0
		self.meta = game_pb2.GameMeta(_initialized=True, last_updated=int(time.time()), mode=game_pb2.ModeType.PVP_STANDARD, grid_size=self.size)

	def GetGameMeta(self, request, context):
		return self.meta

	def SetGameMeta(self, request, context):
		self.meta = request
		return game_pb2.Empty()

	def Reset(self, request, context):
		self.__init__()
		return game_pb2.Empty()

	def SuggestNextMove(self, game_state, context):
		suggested_state = minimax.basic_minimax(game_state, 19, 2, 2)
		self.current_player = 1
		return suggested_state

	def updateState(self, game_state):
		self.board = self.decode_board(game_state.board)
	
	def GetLastGameState(self, request, context):
		return self.get_game_state()

	def GetGameState(self, request, context):
		return self.get_game_state()

	def decode_board(self, board_bytes):
		return [b for b in board_bytes]

	def get_game_state(self):
		board_bytes = self.encode_board()
		return game_pb2.GameState(
			board = board_bytes,
			p1_captures=1,
			p0_captures=2,
			num_turns=self.num_turns,
			is_end=self.is_game_over(),
			time_to_think_ns=0
		)
		
	def encode_board(self):
		return bytes(self.board)

	def PlacePiece(self, move_request, context):
		print(f"Received move: x={move_request.x}, y={move_request.y}")
		row = move_request.y
		col = move_request.x
		index = row * self.size + col  # Convert to 1D index

		if self.current_player != 1:  # Ensure it's Player 1's turn
			return BoolValue(value=False)

		if self.is_move_valid(index):
			self.board[index] = self.current_player
			self.num_turns += 1
			
			# Now let the AI suggest a move
			suggested_state = self.SuggestNextMove(self.get_game_state(), context)
			
			# Update the board state after AI move
			self.updateState(suggested_state)
			# print(self.board)
			return BoolValue(value=True)
		else:
			print("Invalid move. Try again.")
		
		return BoolValue(value=False)

	def is_move_valid(self, index):
		if 0 <= index < len(self.board):  # Check bounds
			return self.board[index] == 0  # Check if the cell is empty
		return False
	def surrounding_check(self, row, col):
		surrounding_values = []

		directions = [
			(-1, -1), (-1, 0), (-1, 1),
			(0, -1),          (0, 1),    
			(1, -1), (1, 0), (1, 1)       
		]

		for dr, dc in directions:
			new_row, new_col = row + dr, col + dc

			if 0 <= new_row < self.size and 0 <= new_col < self.size:
				value = self.board[new_row][new_col]
				if value == 1 or value == 2:
					return True
		return False

	def is_game_over(self):
		return self.check_winner() or self.num_turns >= self.size * self.size

	def check_winner(self, row=None, col=None):
		return False

	def check_capture(self, row, col):
		return False

	def handle_capture(self, row, col):
		pass

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	game_pb2_grpc.add_GameServicer_to_server(GomokuGame(), server)
	server.add_insecure_port('[::]:50051')
	server.start()
	print("Server is running on port 50051...")
	try:
		while True:
			pass
	except KeyboardInterrupt:
		server.stop(0)

serve()