package org.gomoku;

import com.google.protobuf.ByteString;
import game.GameGrpc;
import game.GameOuterClass;
import io.grpc.stub.StreamObserver;

import java.util.concurrent.ExecutorService;

public class GameService extends GameGrpc.GameImplBase {
    private final int size;
    private int[] board;
    private int isEnd = 0;
    private int numTurns = 0;
    private int[] captures = {0, 0}; // captures[0] = p1 captures, captures[1] = p2 captures
    private GameOuterClass.GameMeta meta;
    private final ExecutorService executor;

    public GameService(int size, ExecutorService executor) {
        this.size = size;
        this.board = new int[size * size];
        meta = GameOuterClass.GameMeta.newBuilder()
                .setInitialized(true)
                .setLastUpdated(System.currentTimeMillis())
                .setMode(GameOuterClass.ModeType.PVP_STANDARD)
                .setGridSize(size)
                .build();
        this.executor = executor;
    }

    @Override
    public void getGameMeta(GameOuterClass.Empty request, StreamObserver<GameOuterClass.GameMeta> responseObserver) {
        responseObserver.onNext(meta);
        responseObserver.onCompleted();
    }

    @Override
    public void setGameMeta(GameOuterClass.GameMeta request, StreamObserver<GameOuterClass.Empty> responseObserver) {
        this.meta = request;
        responseObserver.onNext(GameOuterClass.Empty.getDefaultInstance());
        responseObserver.onCompleted();
    }

    @Override
    public void reset(GameOuterClass.Empty request, StreamObserver<GameOuterClass.Empty> responseObserver) {
        initGame();
        responseObserver.onNext(GameOuterClass.Empty.getDefaultInstance());
        responseObserver.onCompleted();
    }

    @Override
    public void suggestNextMove(GameOuterClass.GameState request, StreamObserver<GameOuterClass.GameState> responseObserver) {
        int piece = request.getNumTurns() % 2 != 0 ? 2 : 1;
        GameOuterClass.GameState suggestedState = Minimax.basicMinimax(executor, request, size, piece, piece);
        responseObserver.onNext(suggestedState);
        responseObserver.onCompleted();
    }

    @Override
    public void getLastGameState(GameOuterClass.Empty request, StreamObserver<GameOuterClass.GameState> responseObserver) {
        responseObserver.onNext(getGameState());
        responseObserver.onCompleted();
    }


    private void initGame() {
        this.board = new int[size * size];
        this.isEnd = 0;
        this.numTurns = 0;
        this.captures = new int[] {0, 0};
        this.meta = GameOuterClass.GameMeta.newBuilder()
                .setInitialized(true)
                .setLastUpdated(System.currentTimeMillis())
                .setMode(GameOuterClass.ModeType.PVP_STANDARD)
                .setGridSize(size)
                .build();
    }

    private GameOuterClass.GameState getGameState() {
        return GameOuterClass.GameState.newBuilder()
                .setBoard(encodeBoard())
                .setP1Captures(captures[0])
                .setP2Captures(captures[1])
                .setNumTurns(numTurns)
                .setIsEnd(isEnd)
                .setTimeToThinkNs(0)
                .build();
    }

    private ByteString encodeBoard() {
        byte[] boardBytes = new byte[board.length];
        for (int i = 0; i < board.length; i++) {
            boardBytes[i] = (byte) board[i];
        }
        return ByteString.copyFrom(boardBytes);
    }

}
