import grpc
from flask import Flask, render_template, jsonify, request
import game_pb2_grpc
import game_pb2


class GomokuClient:
    def __init__(self):
        self.app = Flask('game_app', template_folder='./backend/templates')
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = game_pb2_grpc.GameStub(self.channel)
        self.update_game_state()
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/move', 'move', self.move, methods=['POST'])
        self.app.add_url_rule('/board', 'get_board', self.get_board)


    def index(self):
        return render_template('test.html', board=self.board)

    def get_board(self):
        return jsonify(board=self.board)

    def move(self):
        x = int(request.form['x'])
        y = int(request.form['y'])

        move_request = game_pb2.MoveRequest(x=x, y=y)
        response = self.stub.PlacePiece(move_request)
        if response.value:
            self.update_game_state()
        return jsonify(status=response.value)  # Ensure response.value is correctly accessed

    def update_game_state(self):
        self.meta = self.stub.GetGameMeta(game_pb2.Empty())
        self.game_state = self.stub.GetLastGameState(game_pb2.Empty())
        self.board = self.convert_to_2d_list(self.bytes_to_int_array(self.game_state.board), self.meta.grid_size)

    def bytes_to_int_array(self, byte_data):
        return [int.from_bytes(byte_data[i:i + 4], 'big') for i in range(0, len(byte_data), 4)]

    def convert_to_2d_list(self, int_array, size):
        return [int_array[i:i + size] for i in range(0, len(int_array), size)]

game_app = GomokuClient()
game_app.app.run(debug=True)