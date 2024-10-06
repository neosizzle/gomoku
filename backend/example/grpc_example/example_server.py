import grpc
from concurrent import futures

import game_pb2_grpc
import game_pb2


# implement server functions here and store state
class GameServicer(game_pb2_grpc.GameServicer):
	def __init__(self):
		self._initialized = False
		self.last_updated = 0
		self.mode = "PVP_PRO"
		self.grid_size = 4

	def GetGameMeta(self, request, context):
		return game_pb2.GameMeta(_initialized=self._initialized, last_updated=self.last_updated, mode=self.mode, grid_size=self.grid_size)

	def SetGameMeta(self, request, context):
		self._initialized = request._initialized
		self.last_updated = request.last_updated
		self.mode = request.mode
		self.grid_size = request.grid_size
		return game_pb2.Empty()
	
	def SuggestNextMove(self, request, context):
		input_list = list(request.board)
		input_list[0] += 1
		new_state = game_pb2.GameState(
			board=bytes(input_list),
			p1_captures=request.p0_captures,
			p0_captures=request.p1_captures,
			num_turns=request.num_turns + 1,
			is_end=False,
			time_to_think_ns=0
		)
		return new_state

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    game_pb2_grpc.add_GameServicer_to_server(GameServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

serve()