import grpc
import time

import game_pb2_grpc
import game_pb2

def main():
	channel = grpc.insecure_channel('localhost:50051')
	stub = game_pb2_grpc.GameStub(channel)
	meta = stub.GetGameMeta(game_pb2.Empty())
	game_state = game_pb2.GameState(
		board=bytes([0] * 16),
		p1_captures=0,
		p0_captures=0,
		num_turns=0,
		is_end=False
	)

	print(meta)
	
	while True:
		print(game_state.board)
		game_state = stub.SuggestNextMove(game_state)
		time.sleep(1)

main()