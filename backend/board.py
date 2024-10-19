import grpc
import game_pb2_grpc
import game_pb2
from concurrent import futures
import time
from google.protobuf.wrappers_pb2 import BoolValue

class GomokuGame(game_pb2_grpc.GameServicer):
    def __init__(self):
        self.size = 19
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 1
        self.captures = {'X': 0, 'O': 0}
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
        row, col = self.decode_board(game_state.board)
        if self.place_piece(row, col):
            return self.get_game_state()
        context.set_details("Invalid move.")
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        return game_state

    def GetLastGameState(self, request, context):
        return self.get_game_state()

    def GetGameState(self, request, context):
        return self.get_game_state()

    def decode_board(self, board_bytes):
        board = [board_bytes[i:i+19] for i in range(0, len(board_bytes), 19)]
        return [(i, j) for i in range(self.size) for j in range(self.size) if board[i][j] != b' ']

    def get_game_state(self):
        board_bytes = self.encode_board()
        return game_pb2.GameState(
            board=board_bytes,
            p1_captures=1,
            p0_captures=2,
            num_turns=self.num_turns,
            is_end=self.is_game_over(),
            time_to_think_ns=0
        )

    def encode_board(self):
        flat_board = [cell for row in self.board for cell in row]
        return b''.join(int(cell).to_bytes(4, byteorder='big') for cell in flat_board)

    def PlacePiece(self, move_request, context):
        print(f"Received move: x={move_request.x}, y={move_request.y}")
        row = move_request.y
        col = move_request.x
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            self.num_turns += 1
            self.current_player = 2 if self.current_player == 1 else 1
            return BoolValue(value=True)
        else:
            print("Invalid move. Try again.")
        return BoolValue(value=False)

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