import grpc
from concurrent import futures

import game_pb2_grpc
import game_pb2


# implement server functions here and store state
class GameServicer(game_pb2_grpc.GameServicer):
	def __init__(self):
		self._initialized = False
		self.gameId = 0
		self.mode = "PVP_PRO"
		self.gridSize = 4

	def GetGameMeta(self, request, context):
		return game_pb2.GameMeta(_initialized=self._initialized, gameId=self.gameId, mode=self.mode, gridSize=self.gridSize)

	def SetGameMeta(self, request, context):
		self._initialized = request._initialized
		self.gameId = request.gameId
		self.mode = request.mode
		self.gridSize = request.gridSize
		return game_pb2.Empty()
	
	def SuggestNextMove(self, request, context):
		input_list = list(request.board)
		input_list[0] += 1
		new_state = game_pb2.GameState(
			board=bytes(input_list),
			p1_captures=request.p0_captures,
			p0_captures=request.p1_captures,
			num_turns=request.num_turns + 1,
			is_end=False
		)
		return new_state

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    game_pb2_grpc.add_GameServicer_to_server(GameServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

serve()