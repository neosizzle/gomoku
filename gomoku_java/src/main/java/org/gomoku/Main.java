package org.gomoku;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;


import com.google.protobuf.ByteString;

import game.GameOuterClass;

public class Main {
     private static ByteString encodeBoard( byte[] board ) {
        byte[] boardBytes = new byte[board.length];
        for (int i = 0; i < board.length; i++) {
            boardBytes[i] = (byte) board[i];
        }
        return ByteString.copyFrom(boardBytes);
    }

    private static int[] decodeBoard(ByteString encodedBoard) {
        byte[] boardBytes = encodedBoard.toByteArray(); // Convert ByteString to byte array
        int[] board = new int[boardBytes.length];
        for (int i = 0; i < boardBytes.length; i++) {
            board[i] = boardBytes[i]; // Convert each byte to an int
        }
        return board;
    }

    
    public static void main(String[] args) throws InterruptedException, IOException {
         int port = 50051;
         Server server = ServerBuilder.forPort(port)
                 .addService(new GameService(9))
                 .build();

         server.start();
         System.out.println("Server started on port " + port + "...");

         Runtime.getRuntime().addShutdownHook(new Thread(() -> {
             System.err.println("Shutting down server...");
             try {
                 server.shutdown().awaitTermination();
                 System.out.println("Server shut down successfully.");
             } catch (InterruptedException e) {
                 System.err.println("Error during server shutdown: " + e.getMessage());
                 Thread.currentThread().interrupt();
             }
         }));

         server.awaitTermination();

//        final int BOARD_SIZE = 9;
//
//        byte[] board = {
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 1, 0, 0, 1, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 0, 2, 0, 0, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0,
//                0, 0, 0, 0, 0, 0, 0, 0, 0
//        };
//
//        GameOuterClass.GameState game_state = GameOuterClass.GameState.newBuilder()
//                .setBoard(encodeBoard(board))
//                .setP1Captures(4)
//                .setP2Captures(4)
//                .setNumTurns(0)
//                .setIsEnd(0)
//                .setTimeToThinkNs(0)
//                .build();
//
//        StaticEvaluation staticEvaluation = new StaticEvaluation();
//        MoveGeneration moveGeneration = new MoveGeneration(BOARD_SIZE);

//         int res = staticEvaluation.staticEval(BOARD_SIZE, game_state, 2, 1, (int) game_state.getP2Captures(), (int) game_state.getP1Captures());
//        List<GameOuterClass.GameState> res = moveGeneration.generatePossibleMoves(game_state, BOARD_SIZE, (byte) 1, true);
//        printBoard(Minimax.basicMinimax(game_state, 9, 2, 2).getBoard().toByteArray(), 9, 0);
    }
}
