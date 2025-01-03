package org.gomoku;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;


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
        ExecutorService executor = Executors.newFixedThreadPool(5);
         Server server = ServerBuilder.forPort(port)
                 .addService(new GameService(19, executor))
                 .build();

         server.start();
         System.out.println("Server started on port " + port + "...");

         Runtime.getRuntime().addShutdownHook(new Thread(() -> {
             System.err.println("Shutting down server...");
             try {
                 executor.shutdown();
                 server.shutdown().awaitTermination();
                 System.out.println("Server shut down successfully.");
             } catch (InterruptedException e) {
                 System.err.println("Error during server shutdown: " + e.getMessage());
                 Thread.currentThread().interrupt();
             }
         }));

         server.awaitTermination();

        // testing area, the authors are lazy to create executable examples
        final int BOARD_SIZE = 19;

        byte[] board = {
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        };

        GameOuterClass.GameState game_state = GameOuterClass.GameState.newBuilder()
                .setBoard(encodeBoard(board))
                .setP1Captures(0)
                .setP2Captures(0)
                .setNumTurns(9)
                .setIsEnd(0)
                .setTimeToThinkNs(0)
                .build();
        
        StaticEvaluation staticEvaluation = new StaticEvaluation();
//        MoveGeneration moveGeneration = new MoveGeneration(BOARD_SIZE);
        GomokuUtils gomokuUtils = new GomokuUtils(BOARD_SIZE);
        
        int res = staticEvaluation.staticEval(BOARD_SIZE, game_state, 2, 1, (int) game_state.getP2Captures(), (int) game_state.getP1Captures());
        // boolean res = staticEvaluation.checkWinCondition(BOARD_SIZE, game_state, 1, (int) game_state.getP1Captures());

        // List<GameOuterClass.GameState> res = moveGeneration.generatePossibleMoves(game_state, BOARD_SIZE, (byte) 2, true);
        // List<GomokuUtils.GameStateNode> res = moveGeneration.generateMoveTree(game_state, BOARD_SIZE, (byte) 2, 3);
        // boolean res = moveGeneration.hasThreat(50, BOARD_SIZE, (byte) 2, board);

        // boolean res = moveGeneration.detectDoubleFreeThrees(50, BOARD_SIZE, (byte) 2, board);
        // byte[] buffer = {
        //     0, 0, 0, 1, 0, 0, 2, 0, 0
        // };
        //  List<Byte> byteList = new ArrayList<>();
        // for (byte b : buffer) {
        //     byteList.add(b); // Add each byte to the List
        // }
        // boolean res = moveGeneration.hasFreeThree(byteList, (byte) 2, 5);

        System.out.println(res);
        
        // System.out.println(res.size());
        // for (GameOuterClass.GameState state : res) {
        //     gomokuUtils.prettyPrintBoard(state.getBoard().toByteArray());
        //     System.out.println("");
        // }
        // gomokuUtils.prettyPrintBoard(Minimax.basicMinimax(game_state, BOARD_SIZE, 2, 2).getBoard().toByteArray());

        // Function<Integer, Integer> fn = gomokuUtils::getLeftIdx;
        // System.out.println(moveGeneration.checkCaptureBlockDir(fn, 35, BOARD_SIZE, 2, board));
    }
}
